"""异步网络请求"""
import os
import time
import random
import asyncio
import aiohttp
from io import BytesIO
from pathlib import Path
from threading import Lock
from Fun.BaseTools import Task, TaskAsyncManage, Get, TaskSignal, LogClass

logger = LogClass.get_logger(__name__, console_level='WARNING')


class AsyncHTTPManage(TaskAsyncManage):
    """异步请求管理类
    
    特性：
    - 继承 TaskAsyncManage，使用内部异步池管理并发
    - 共享 aiohttp session 连接池
    - 支持代理配置,注意由于异步请求共享连接对象,代理只能由该类指定
    - 所有异步操作通过 submit_task 提交到父类异步池
    - 支持API速率限制控制
    - 在启用API速率限制时带有速率信号,发送当前已经请求的次数rate_limit_count_signal
    - 在启用API速率限制时带有API受限信号,发送当前速率达到上限信号rate_limit_signal
    """
    connect_limit = 48  # 连接池总大小
    host_limit = 16  # 同一主机最大连接数
    default_timeout = aiohttp.ClientTimeout(
        total=None,  # 总超时（包含所有操作）
        connect=5,  # 连接超时
        sock_read=15  # 读取间隔超时15秒（两次数据接收之间的最大等待时间）
    )
    default_retry_time = (1, 3)
    default_start_time = (0, 1)

    def __init__(self, num_work: int = None, proxies=None, rate_limit: int = None, rate_period: float = 60.0):
        """
        初始化异步请求管理器
        :param num_work: 工作线程数
        :param proxies: 代理地址，如 'http://127.0.0.1:7890'
        :param rate_limit: API速率限制（每分钟最大请求数），None表示不限制
        :param rate_period: 速率限制的时间窗口（秒），默认60秒
        """
        super().__init__(num_work)
        self.proxies = proxies

        # 速率控制配置
        self.rate_limit = rate_limit  # 速率最大限制
        self.rate_period = rate_period  # 请求次数
        self._request_timestamps = []
        self._rate_lock = None  # 在事件循环中初始化
        self._lock = Lock()  # 线程锁
        # 初始化 session（同步等待完成）
        self._init_session()

    async def _async_init_session(self):
        """异步初始化 session"""
        connector = aiohttp.TCPConnector(
            limit=self.connect_limit,
            limit_per_host=self.host_limit,
        )
        self.session = aiohttp.ClientSession(
            connector=connector,
            trust_env=True if self.proxies is None else False,
            proxy=self.proxies
        )

        # 如果启用了速率限制，初始化锁
        if self.rate_limit is not None:
            self._rate_lock = asyncio.Lock()
            self.rate_limit_count_signal = TaskSignal()
            self.rate_limit_signal = TaskSignal()

    def _init_session(self):
        """初始化 session（同步等待异步初始化完成）"""
        init_task = Task(self._async_init_session, task_manage=self)
        init_task.start(5, 2)  # 同步等待初始化完成
        if not hasattr(self, 'session'):
            raise Exception(f"{self.__class__.__name__} 初始化失败")

    def stop(self):
        """停止并清理资源"""
        # 关闭 session
        if self.session is not None:
            async def close_session():
                await self.session.close()

            close_task = Task(close_session, task_manage=self)
            close_task.start(timeout=5)
        # 调用父类停止方法（会停止内部异步池）
        super().stop()

    async def _async_set_proxies(self, proxies=None):
        """异步设置代理并重建session"""
        # 关闭旧session
        if self.session is not None and not self.session.closed:
            await self.session.close()

        # 更新代理配置
        self.proxies = proxies

        # 创建新的connector和session
        connector = aiohttp.TCPConnector(
            limit=self.connect_limit,
            limit_per_host=self.host_limit,
        )
        self.session = aiohttp.ClientSession(
            connector=connector,
            trust_env=True if self.proxies is None else False,
            proxy=self.proxies
        )

    def set_proxies(self, proxies=None, timeout=5):
        """
        动态设置代理地址
        :param proxies: 代理地址，如 'http://127.0.0.1:7890'，None表示不使用代理
        :param timeout: 超时时间（秒），默认5秒
        """
        set_task = Task(self._async_set_proxies, args=(proxies,), task_manage=self)
        set_task.start(timeout=timeout)
        logger.info(f"{self.__class__.__name__} 代理已更新为: {proxies}")

    def _check_and_get_wait_time(self) -> tuple[float, bool]:
        """
        检查速率限制状态并计算需要等待的时间（临界区）
        :return: (wait_time, need_wait) 等待时间和是否需要等待
        """
        with self._lock:
            now = time.time()

            # 移除超过时间窗口的旧记录
            self._request_timestamps = [
                ts for ts in self._request_timestamps
                if now - ts < self.rate_period
            ]

            # 如果已达到限制，计算需要等待的时间
            if len(self._request_timestamps) >= self.rate_limit:
                oldest = self._request_timestamps[0]
                wait_time = self.rate_period - (now - oldest) + 0.1
                need_wait = wait_time > 0
            else:
                wait_time = 0.0
                need_wait = False

            return wait_time, need_wait

    def _record_request(self):
        """
        记录本次请求时间戳（临界区）
        """
        with self._lock:
            # 重新清理过期记录
            now = time.time()
            self._request_timestamps = [
                ts for ts in self._request_timestamps
                if now - ts < self.rate_period
            ]

            # 记录本次请求
            self._request_timestamps.append(time.time())
            self.rate_limit_count_signal.emit(self.rate_period)

            # 调试信息（可选）
            if len(self._request_timestamps) % 10 == 0:
                logger.info(f"当前请求计数: {len(self._request_timestamps)}/"
                            f"{self.rate_limit} (窗口: {self.rate_period}秒)")

    async def _wait_with_check(self, wait_time: float, parent_task=None) -> bool:
        """
        执行等待操作，期间定期检查父任务状态
        :param wait_time: 需要等待的总时间（秒）
        :param parent_task: 父任务对象，用于检查isRunning状态
        :return: True表示等待完成，False表示被中断
        """
        self.rate_limit_signal.emit(self.rate_limit)
        logger.info(f"API速率限制: 已达 {self.rate_limit}次/{self.rate_period}秒，"
                    f"等待 {wait_time:.1f} 秒...")

        # 分段等待，每1秒检查一次父任务状态
        elapsed = 0.0
        check_interval = 1.0
        while elapsed < wait_time:
            # 检查父任务是否仍在运行
            if parent_task is not None and not parent_task.isRunning:
                logger.info(f"API速率限制等待被中断: {parent_task.name}已停止")
                return False

            # 计算本次睡眠时长（不超过剩余时间和检查间隔）
            remaining = wait_time - elapsed
            sleep_time = min(check_interval, remaining)
            await asyncio.sleep(sleep_time)
            elapsed += sleep_time

        return True

    def _wait_with_check_sync(self, wait_time: float, parent_task=None) -> bool:
        """
        同步版本：执行等待操作，期间定期检查父任务状态
        :param wait_time: 需要等待的总时间（秒）
        :param parent_task: 父任务对象，用于检查isRunning状态
        :return: True表示等待完成，False表示被中断
        """
        self.rate_limit_signal.emit(self.rate_limit)
        logger.info(f"API速率限制: 已达 {self.rate_limit}次/{self.rate_period}秒，"
                    f"等待 {wait_time:.1f} 秒...")

        # 分段等待，每1秒检查一次父任务状态
        elapsed = 0.0
        check_interval = 1.0
        while elapsed < wait_time:
            # 检查父任务是否仍在运行
            if parent_task is not None and not parent_task.isRunning:
                logger.info(f"API速率限制等待被中断: {parent_task.name}已停止")
                return False

            # 计算本次睡眠时长（不超过剩余时间和检查间隔）
            remaining = wait_time - elapsed
            sleep_time = min(check_interval, remaining)
            time.sleep(sleep_time)
            elapsed += sleep_time

        return True

    async def wait_for_rate_limit(self, parent_task=None) -> bool:
        """
        等待直到可以发起新的请求（遵守API速率限制）
        如果未设置速率限制，则直接返回
        :param parent_task:关联的父任务，用于检查isRunning状态
        :return: True表示可以继续执行，False表示父任务已停止
        """
        if self.rate_limit is None:
            return True

        # 第一步：检查并获取等待时间（临界区）
        wait_time, need_wait = self._check_and_get_wait_time()

        # 第二步：如果需要等待，在锁外进行（不阻塞其他线程/协程）
        if need_wait:
            if not await self._wait_with_check(wait_time, parent_task):
                return False

        # 第三步：记录本次请求（临界区）
        self._record_request()

        return True

    def wait_for_rate_limit_sync(self, parent_task=None) -> bool:
        """
        同步版本：等待直到可以发起新的请求（遵守API速率限制）
        如果未设置速率限制，则直接返回
        :param parent_task:关联的父任务，用于检查isRunning状态
        :return: True表示可以继续执行，False表示父任务已停止
        """
        if self.rate_limit is None:
            return True

        # 第一步：检查并获取等待时间（临界区）
        wait_time, need_wait = self._check_and_get_wait_time()

        # 第二步：如果需要等待，在锁外进行（不阻塞其他线程）
        if need_wait:
            if not self._wait_with_check_sync(wait_time, parent_task):
                return False

        # 第三步：记录本次请求（临界区）
        self._record_request()

        return True

    def get_rate_limit_status(self) -> dict:
        """
        获取当前速率限制状态
        :return: 包含当前请求数、剩余配额等信息的字典
        """
        if self.rate_limit is None:
            return {"enabled": False}

        now = time.time()
        with self._lock:
            recent_requests = [ts for ts in self._request_timestamps if now - ts < self.rate_period]
        current_count = len(recent_requests)
        remaining = max(0, self.rate_limit - current_count)

        return {
            "enabled": True,
            "limit": self.rate_limit,
            "period": self.rate_period,
            "current_count": current_count,
            "remaining": remaining,
            "utilization": f"{current_count / self.rate_limit * 100:.1f}%"
        }


class AsyncJson(Task):
    """异步请求Json文件"""

    def __init__(self, url: str, async_manager: 'AsyncHTTPManage', params: dict = None,
                 headers: dict = None, timeout: aiohttp.ClientTimeout = None, retry_count=3):
        """
        异步获取Json文件
        :param url: 请求的URL
        :param params:请求参数
        :param async_manager:异步请求管理类
        :param headers: 请求头,默认无
        :param timeout: 超时时间,默认请查看AsyncHTTPManage.default_timeout设置
        """
        super().__init__(self.__execute, async_manager)
        self.url = url
        self.params = params
        self.headers = headers
        self.async_manager = async_manager
        self.retry_count = retry_count
        self.timeout = async_manager.default_timeout if timeout is None else timeout
        # 请求后的状态和结果
        self.status_code = 0

    @property
    def request_args(self) -> dict:
        """实际请求时的关键词参数"""
        return {'headers': self.headers, 'params': self.params, 'timeout': self.timeout}

    async def __execute(self) -> dict:
        """异步请求,无结果时返回空字典"""
        retry_count = 0  # 当前重试次数
        kwargs = self.request_args  # 请求参数
        session = self.async_manager.session  # 连接对象
        tetry_time = round(random.uniform(*self.async_manager.default_retry_time), 2)  # 重试等待时间
        while self.isRunning and retry_count < self.retry_count:
            try:
                # 遵循任务池速率限制
                if not await self.async_manager.wait_for_rate_limit(self):
                    return {}
                async with session.get(self.url, **kwargs) as response:
                    self.status_code = response.status
                    if self.status_code == 200:
                        return await response.json()
            except Exception as e:
                retry_count += 1
                logger.warning(f"{self.__class__.__name__} 第{retry_count}次请求失败: "
                               f"{self.url} {tetry_time}秒后重试 错误: {e}")
            await asyncio.sleep(tetry_time)
        return {}


class AsyncChunkDownloader(Task):
    """
    支持异步分块下载文件
    支持指定块数量或块大小
    分块下载时将进入限制并发
    注意:分块下载时每一块都属于一次独立的请求
    """
    default_temp_dir = os.path.join(Get.run_dir(), 'async_download_temp')
    single_read_size = 1024 * 1024 * 1  # 单次读取大小,默认1MB
    chunk_num_max = 10  # 最大分块数量,严格限制无论是否指定
    chunk_size_min = 1024 * 1024 * 5  # 最小块尺寸
    chunk_size_max = 1024 * 1024 * 10  # 最大块尺寸
    # 单个文件下载的最大连接数量,注意该限制仅针对单个文件,协程池的最大工作数量决定最终并行数量
    num_work_max = 10

    def __init__(self, url: str, async_manager: 'AsyncHTTPManage',
                 num_chunks: int = None, params: dict = None, headers: dict = None,
                 timeout: aiohttp.ClientTimeout = None, retry_count=3):
        """
        异步下载文件（支持分块并发）
        :param url: 请求的URL
        :param async_manager: 异步请求管理类
        :param num_chunks: 分块数量,不指定时将根据文件大小智能计算
        :param params: 请求参数
        :param headers: 请求头
        :param timeout: 超时设置
        :param retry_count:重试次数
        """
        super().__init__(self.__execute, async_manager)
        self.url = url
        self.params = params
        self.headers = headers
        self.__num_chunks = num_chunks
        self.chunk_size = 0  # 实际每个块的大小
        self.async_manager = async_manager
        self.temp_dir = self.default_temp_dir  # 缓存目录
        self.retry_count = retry_count  # 重试次数
        self.support_chunk = False  # 是否支持分块下载
        self.file_size = 0  # 文件大小
        self.file_bytesio = None  # 下载的文件
        self.file_chunk_bytesio: dict[int, BytesIO] = {}  # 分块下载的文件
        self.semaphore = asyncio.Semaphore(self.num_work_max)  # 限制并发
        self.timeout = async_manager.default_timeout if timeout is None else timeout
        self.status_code = 0

    @property
    def request_args(self) -> dict:
        """实际请求时的关键词参数"""
        return {'headers': self.headers, 'params': self.params, 'timeout': self.timeout}

    @property
    def num_chunks(self) -> int:
        """计算分块数量：优先使用用户指定值，否则根据文件大小智能计算
        
        保证除最后一块外，其他块的大小在 [chunk_size_min, chunk_size_max] 范围内
        最后一块可能小于 chunk_size_min（用于容纳余数）
        严格限制最大分块数量不超过 chunk_num_max
        """
        # 用户指定了分块数，直接使用（但仍受最大块数限制）
        if self.__num_chunks is not None:
            return max(1, min(self.__num_chunks, self.chunk_num_max))

        # 尚未获取文件大小时，返回0
        if self.file_size == 0:
            return 0

        # 小文件：小于等于最小块大小，不分块
        if self.file_size <= self.chunk_size_min:
            return 1

        # 计算最少需要多少块才能保证每块不超过上限
        # 向上取整：file_size / chunk_size_max
        min_chunks = (self.file_size + self.chunk_size_max - 1) // self.chunk_size_max

        # 计算最多可以分成多少块才能保证前N-1块不小于下限
        max_chunks = (self.file_size - 1) // self.chunk_size_min + 1

        # 如果最大块数为0或1，至少分1块
        if max_chunks <= 1:
            return 1

        # 选择最少的块数（提高单块大小，减少并发压力和API请求次数）
        chunks = min_chunks

        # 确保不超过最大块数限制（关键：严格遵守 chunk_num_max）
        chunks = min(chunks, max_chunks, self.chunk_num_max)

        # 最终验证：检查分块是否合理
        if chunks > 1:
            # 计算基础块大小和余数
            base_chunk_size = self.file_size // chunks

            # 如果基础块大小小于下限，尝试减少块数（但不能少于min_chunks）
            if base_chunk_size < self.chunk_size_min:
                # 重新计算：使用更大的块大小
                chunks = max(min_chunks, (self.file_size + self.chunk_size_max - 1) // self.chunk_size_max)
                # 再次确保不超过最大块数限制
                chunks = min(chunks, self.chunk_num_max)
        logger.info(f'{self.url} 分块数量为: {chunks}')
        return chunks

    @property
    def chunks_list(self) -> list[tuple[int, int, int]]:
        """分块,返回每块的起始,结束,编号"""
        num_chunks = self.num_chunks
        if num_chunks <= 1 or self.file_size == 0:
            return [(0, self.file_size - 1, 0)] if self.file_size > 0 else []

        chunk_size = self.file_size // num_chunks
        chunks = []

        for i in range(num_chunks):
            start = i * chunk_size
            # 最后一块直接到文件末尾，自动包含所有剩余字节
            if i == num_chunks - 1:
                end = self.file_size - 1
            else:
                end = start + chunk_size - 1
            chunks.append((start, end, i))
        return chunks

    async def get_file_size(self, session) -> int:
        """获取文件大小"""
        # 遵循任务池速率限制
        if not await self.async_manager.wait_for_rate_limit(self):
            return 0

        async with session.head(self.url) as response:
            headers = response.headers
            self.status_code = response.status
            if headers.get('Accept-Ranges', '').lower() == 'bytes':
                self.support_chunk = True  # 支持分块
            file_size = int(headers.get('content-length', 0))
            if file_size == 0:
                raise ValueError(f"{self.__class__.__name__} {self.url} 无法获取文件大小")
            return file_size

    async def progress_emit(self):
        """进度监控"""
        last_finished = self.progress.finished
        last_time = time.time()
        while self.isRunning and self.progress.get_progress() < 100:
            if self.progress.finished - last_finished > 1024 * 4:  # 相差大于4KB
                interval = time.time() - last_time
                rate = (self.progress.finished - last_finished) / interval if interval > 0 else 0
                self.progress.rate = int(rate)
                last_finished = self.progress.finished
                last_time = time.time()
                self.progress_signal.emit(self.progress)
            await asyncio.sleep(0.2)

    def merge_file(self) -> BytesIO | None:
        """合并文件"""
        file_bytesio = BytesIO()
        for chunk_num, chunk_file in sorted(self.file_chunk_bytesio.items(), key=lambda x: x[0], reverse=False):
            if chunk_file is None: break
            file_bytesio.write(chunk_file.getbuffer())
        # 数据验证
        if file_bytesio.tell() == self.file_size:
            self.file_bytesio = file_bytesio
            return file_bytesio

    async def download_one(self, session, url, kwargs, single_read_size=None) -> BytesIO | None:
        """
        下载单个文件逻辑
        :param session:请求对象
        :param url:请求地址
        :param kwargs:请求参数
        :param single_read_size:单次读取大小,None时使用默认值,0表示一次读取全部
        :return 返回 BytesIO|None
        """
        # 获取文件本次下载的文件大小用于下载后比对是否有误
        range = kwargs['headers'].get('Range', None)
        if range:
            start, end = range.split('=')[1].split('-')
            file_size = int(end) - int(start) + 1
        else:
            file_size = self.file_size
        # 遵循任务池速率限制
        if not await self.async_manager.wait_for_rate_limit():
            return None
        # 请求
        async with session.get(url, **kwargs) as response:
            file_bytesio = BytesIO()
            total_read = 0
            while self.isRunning:
                if single_read_size != 0:
                    single_read_size = self.single_read_size if single_read_size is None else single_read_size
                    chunk_data = await response.content.read(single_read_size)
                    if not chunk_data:
                        break
                else:
                    chunk_data = await response.read()
                file_bytesio.write(chunk_data)
                total_read += len(chunk_data)
                self.progress.finished = total_read
                if single_read_size == 0:
                    break
            if not self.isRunning:
                return None
            # 验证数据完整性
            if total_read == file_size:
                return file_bytesio
            raise ValueError(f"{url} 下载数据不完整: 期望{file_size}字节,实际{total_read}字节")

    async def download_chunk(self, session, url, start, end, chunk_num) -> tuple[int, BytesIO | None]:
        """下载单个块"""
        if not self.isRunning:
            return chunk_num, None
        if chunk_num in self.file_chunk_bytesio:
            return chunk_num, self.file_chunk_bytesio[chunk_num]
        # 请求前准备
        kwargs = self.request_args
        headers = self.headers.copy() if self.headers is not None else {}
        headers['Range'] = f'bytes={start}-{end}'
        kwargs['headers'] = headers
        await asyncio.sleep(round(random.uniform(*self.async_manager.default_start_time), 2))  # 错峰运行
        # 发送请求
        async with self.semaphore:
            if not self.isRunning:
                return chunk_num, None
            try:
                logger.info(f'{url} 开始下载第{chunk_num}块: {start}-{end} 大小为{end - start + 1}')
                chunk_file_bytesio = await self.download_one(session, url, kwargs)
                if isinstance(chunk_file_bytesio, BytesIO):
                    self.file_chunk_bytesio[chunk_num] = chunk_file_bytesio
                    return chunk_num, chunk_file_bytesio
            except Exception:
                raise Exception(f'{url} 第{chunk_num}块 下载失败: {start}-{end} 大小为{end - start + 1}')

    async def __execute(self) -> BytesIO | None:
        """异步分块下载文件"""
        if not self.isRunning:
            return None
        start_time = time.time()
        session = self.async_manager.session
        logger.info(f'{Path(self.url).name} 获取请求头')
        try:
            self.file_size = await self.get_file_size(session)  # 获取文件大小
            if self.file_size == 0:
                if not self.isRunning:
                    return None
                raise ValueError(f"{self.__class__.__name__} {self.url} 获取文件大小失败")
        except ValueError:
            return None
        self.progress.total = self.file_size  # 设置进度最大值
        # 启动进度监控任务
        progress_task = asyncio.create_task(self.progress_emit())
        # 支持分块下载并且文件大小大于最小限制
        chunks_list = self.chunks_list
        retry_count = 0
        logger.info(f'{Path(self.url).name} 开始下载')
        while self.isRunning and retry_count < self.retry_count:
            try:
                if self.support_chunk and len(chunks_list) > 1:
                    # 并发下载所有块
                    await asyncio.gather(
                        *[self.download_chunk(session, self.url, start, end, i)
                          for start, end, i in chunks_list])
                    if len(self.file_chunk_bytesio) == len(chunks_list):
                        self.file_bytesio = self.merge_file()
                        break
                    else:
                        raise ValueError(f"分块下载数量不对: "
                                         f"当前获取数量{len(self.file_chunk_bytesio)}个块 "
                                         f"预计获取分块数量{len(chunks_list)}个块")
                else:
                    chunks_files = await self.download_one(session, self.url, self.request_args)
                    if isinstance(chunks_files, BytesIO):
                        self.file_bytesio = chunks_files
                        break
                    else:
                        raise ValueError(f"下载失败")
            except Exception as e:
                retry_count += 1
                logger.exception(f"{self.__class__.__name__}.__execute 下载失败: 第{retry_count}次 错误: {e}")
            await asyncio.sleep(round(random.uniform(*self.async_manager.default_retry_time), 2))
        # 停止进度监控任务
        progress_task.cancel()
        success = '下载失败'
        if self.file_bytesio is not None:
            success = '下载完成'
            self.progress.finished = self.progress.total
            self.progress_signal.emit(self.progress)
        logger.info(f'{Path(self.url).name} {success} 耗时: {time.time() - start_time:.2f}s')
        return self.file_bytesio

    def save_file(self, file_path):
        """保存文件"""
        if self.file_bytesio is None:
            return
        with open(file_path, 'wb') as f:
            f.write(self.file_bytesio.getvalue())


if __name__ == '__main__':
    from Fun.BaseTools import ImageLoad
    from Fun.BaseTools.Get import get_threads

    urls = [
        "https://w.wallhaven.cc/full/ml/wallhaven-mlwj3m.jpg",
        "https://w.wallhaven.cc/full/e8/wallhaven-e8ekxl.jpg",
        "https://w.wallhaven.cc/full/qr/wallhaven-qrgl87.jpg",
        "https://w.wallhaven.cc/full/7j/wallhaven-7jw8po.jpg",
        "https://w.wallhaven.cc/full/8g/wallhaven-8gkw32.png",
    ]
    header = {"X-API-Key": 'mxYAr8xPS6J4gyVOtfu0YQHwftSO4p6x'}
    print('创建异步池之前')
    for i in get_threads(): print(i)
    async_manager = AsyncHTTPManage(100, rate_limit=45)
    tasks = [AsyncChunkDownloader(url, async_manager, num_chunks=1, headers=header) for url in urls]
    # [task.progress_signal.connect(lambda x: print(x)) for task in tasks]
    [task.start() for task in tasks]
    print('程序运行时')
    for i in get_threads(): print(i)
    for task in tasks:
        result = task.result(0)
        if result is not None:
            file_name = Path(task.url).name
            ImageLoad(result).save(f'./save_image/{file_name}')

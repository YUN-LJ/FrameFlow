"""异步网络请求"""
import time
import asyncio
import aiohttp
import threading
from io import BytesIO
from pathlib import Path
from Fun.BaseTools import Task, TaskManage


class AsyncManage(TaskManage):
    """异步请求管理类，拥有独立事件循环和连接池"""
    connect_limit = 100  # 连接池大小

    def __init__(self, num_work: int = None, proxies=None):
        super().__init__(num_work)
        self.session = None
        self.proxies = proxies
        # 创建新的事件循环（不绑定当前线程）
        self.loop = asyncio.new_event_loop()
        # 启动后台线程运行该循环
        self._thread = threading.Thread(
            target=self._run_loop, name=f'{self.__class__.__name__}.循环线程', daemon=True)
        self._thread.start()
        self._stopped = False  # 停止标志

    def _run_loop(self):
        """在后台线程中运行事件循环"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def _async_init(self):
        """异步初始化 session"""
        connector = aiohttp.TCPConnector(
            limit=self.connect_limit,  # 总连接池大小
            limit_per_host=self.connect_limit,  # 同一主机的最大连接数
        )
        self.session = aiohttp.ClientSession(connector=connector, trust_env=True, proxy=self.proxies)

    def _ensure_session(self):
        """确保 session 已初始化（同步方式）"""
        if self.session is None:
            # 在当前循环上执行初始化协程，并等待完成
            future = asyncio.run_coroutine_threadsafe(self._async_init(), self.loop)
            future.result()  # 阻塞等待完成

    async def get_session(self):
        """异步获取 session（适用于协程内部直接 await）"""
        if self.session is None:
            await self._async_init()
        return self.session

    def run_coro(self, coro):
        """
        同步提交协程到该管理器的事件循环，并阻塞等待结果。
        适用于需要在同步方法中调用异步代码的场景（如 __execute）。
        """
        if self._stopped:
            raise RuntimeError("AsyncManage 已经停止")
        self._ensure_session()
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result()  # 返回协程的执行结果

    def stop(self):
        """停止事件循环并清理资源"""
        if self._stopped:
            return super().stop()
        self._stopped = True

        # 关闭 session（需要在循环中执行）
        if self.session:
            async def close_session():
                await self.session.close()

            future = asyncio.run_coroutine_threadsafe(close_session(), self.loop)
            try:
                future.result(timeout=5)  # 等待关闭完成
            except Exception:
                pass

        # 停止事件循环
        self.loop.call_soon_threadsafe(self.loop.stop)
        self._thread.join(timeout=5)
        self.loop.close()
        return super().stop()


class AsyncJson(Task):
    """异步请求Json文件"""

    def __init__(self, url: str, async_manager: 'AsyncManage',
                 params: dict = None, headers: dict = None,
                 proxies=None, timeout: aiohttp.ClientTimeout = None):
        """
        异步获取Json文件
        :param url: 请求的URL
        :param async_manager:异步请求管理类
        :param headers: 请求头,默认无
        :param proxies: 代理,默认无
        :param timeout: 超时时间,默认时间3秒
        """
        super().__init__(self.__execute, async_manager)
        self.url = url
        self.params = params
        self.headers = headers
        self.proxies = proxies
        self.async_manager = async_manager
        if timeout is None:
            self.timeout = aiohttp.ClientTimeout(
                total=15,  # 总超时（包含所有操作）
                connect=5,  # 连接超时
                sock_read=10  # 读取超时
            )
        else:
            self.timeout = timeout

        # 请求后的状态和结果
        self.status_code = 0

    async def __async_main(self) -> dict:
        try:
            kwargs = {
                'headers': self.headers,
                'params': self.params,
                'timeout': self.timeout,
            }
            if self.proxies:
                kwargs['proxy'] = self.proxies
            session = await self.async_manager.get_session()
            async with session.get(self.url, **kwargs) as response:
                self.status_code = response.status
                if self.status_code == 200:
                    result = await response.json()
                    return result
                return {}
        except Exception as e:
            self.status_code = 404
            print(f"请求失败: {self.url}, 错误: {e}")
        return {}

    def __execute(self) -> dict:
        """同步执行入口：通过 manager 的专属循环运行协程"""
        return self.async_manager.run_coro(self.__async_main())


class AsyncChunkDownloader(Task):
    """异步分块下载文件，支持指定块数量或块大小"""

    def __init__(self, url: str, async_manager: 'AsyncManage', num_chunks: int = 8,
                 params: dict = None, headers: dict = None,
                 proxies=None, timeout: aiohttp.ClientTimeout = None, retry_count=3):
        """
        异步下载文件（支持分块并发）
        :param url: 请求的URL
        :param async_manager: 异步请求管理类
        :param num_chunks: 分块数量，默认8
        :param params: 请求参数
        :param headers: 请求头
        :param proxies: 代理
        :param timeout: 超时设置
        :param retry_count:重试次数
        """
        super().__init__(self.__execute, async_manager)
        self.url = url
        self.params = params
        self.headers = headers
        self.proxies = proxies
        self.num_chunks = num_chunks
        self.async_manager = async_manager
        self.chunks_finished: dict[int, BytesIO] = {}
        self.retry_count = retry_count
        self.run_chunk = False  # 是否支持分块下载
        self.chunk_size = 0  # 实际每个块的大小
        self.file_size = 0
        self.file_bytesio = None  # 下载的文件
        if timeout is None:
            self.timeout = aiohttp.ClientTimeout(total=15, connect=5, sock_read=10)
        else:
            self.timeout = timeout

        self.status_code = 0

    async def get_file_size(self, session) -> int:
        """获取文件大小"""
        async with session.head(self.url) as response:
            headers = response.headers
            if headers.get('Accept-Ranges', '').lower() == 'bytes':
                self.run_chunk = True
            self.file_size = int(headers.get('content-length', 0))
            if self.file_size == 0:
                raise ValueError("无法获取文件大小")
            return self.file_size

    async def progress_emit(self):
        last_finished = self.progress.finished
        last_time = time.time()
        while self.isRunning and self.progress.get_progress() < 100:
            await asyncio.sleep(0.2)
            interval = time.time() - last_time
            rate = (self.progress.finished - last_finished) / interval if interval > 0 else 0
            self.progress.rate = int(rate)
            last_finished = self.progress.finished
            last_time = time.time()
            self.progress_signal.emit(self.progress)

    async def download_chunk(self, session, url, start, end, chunk_num) -> tuple[int, BytesIO | None]:
        """下载单个块"""
        if chunk_num in self.chunks_finished:
            return chunk_num, self.chunks_finished[chunk_num]
        headers = self.headers if self.headers else {}
        headers['Range'] = f'bytes={start}-{end}'
        kwargs = {'headers': headers, 'params': self.params, 'timeout': self.timeout, }
        if self.proxies: kwargs['proxy'] = self.proxies
        retry_count = 0
        while self.isRunning and retry_count < self.retry_count:
            try:
                async with session.get(url, **kwargs) as response:
                    data = await response.read()
                    chunk_file = BytesIO(data)
                    self.progress.finished += len(data)
                    self.chunks_finished[chunk_num] = chunk_file
                    return chunk_num, chunk_file
            except Exception as e:
                self.status_code = 404
                retry_count += 1
                print(f"请求失败: {self.url} 第{chunk_num}块,正在重试第{retry_count}次, 错误: {e}")
        return chunk_num, None

    async def download_file_async(self) -> BytesIO | None:
        """异步分块下载文件"""
        session = await self.async_manager.get_session()
        self.progress.total = await self.get_file_size(session)
        if self.run_chunk:
            # 2. 计算每个块的范围
            chunk_size = self.file_size // self.num_chunks
            chunks = []
            for i in range(self.num_chunks):
                start = i * chunk_size
                end = start + chunk_size - 1
                if i == self.num_chunks - 1:  # 最后一块
                    end = self.file_size - 1
                chunks.append((start, end, i))

            # 4. 并发下载所有块
            tasks = [self.download_chunk(session, self.url, start, end, i) for start, end, i in chunks]
            chunk_files: tuple[tuple[int, BytesIO | None]] = await asyncio.gather(*tasks, self.progress_emit())
            # 5. 合并所有块
            file_bytesio = BytesIO()
            for chunk_num, chunk_file in sorted(chunk_files[:-1], key=lambda x: x[0], reverse=False):
                if chunk_file is not None:
                    file_bytesio.write(chunk_file.getbuffer())
                    self.chunks_finished.pop(chunk_num)
                else:
                    return None
            file_bytesio.seek(0)
            return file_bytesio
        else:
            print(f"{self.url} 不支持分块下载")
            kwargs = {'headers': self.headers, 'params': self.params, 'timeout': self.timeout}
            if self.proxies: kwargs['proxy'] = self.proxies
            try:
                async with session.get(self.url, **kwargs) as response:
                    file_bytesio = BytesIO()
                    while self.isRunning:
                        chunk_data = await response.content.read(8192)
                        if chunk_data:
                            file_bytesio.write(chunk_data)
                            self.progress.finished += len(chunk_data)
                        else:
                            if self.progress.finished >= self.progress.total:
                                break
                            else:
                                raise ValueError("数据不完整")
            except Exception as e:
                self.status_code = 404
                print(f"请求失败: {self.url}, 错误: {e}")
                return None
            return file_bytesio

    def save_file(self, file_path):
        """保存文件"""
        if self.file_bytesio is None:
            return
        with open(file_path, 'wb') as f:
            f.write(self.file_bytesio.getvalue())

    def __execute(self) -> BytesIO | None:
        start_time = time.time()
        print(f'{Path(self.url).name} 开始下载...')
        self.file_bytesio = self.async_manager.run_coro(self.download_file_async())
        print(f'{Path(self.url).name} 下载完成，耗时: {time.time() - start_time:.2f}s')
        return self.file_bytesio


if __name__ == '__main__':
    url = "https://w.wallhaven.cc/full/qr/wallhaven-qrgl87.jpg"
    async_manager = AsyncManage(proxies='http://192.168.137.68:8080')
    task_1 = AsyncChunkDownloader(url, async_manager, num_chunks=10)
    task_1.progress_signal.connect(lambda x: print(x))
    task_1.start(0)
    task_1.save_file(Path(url).name)

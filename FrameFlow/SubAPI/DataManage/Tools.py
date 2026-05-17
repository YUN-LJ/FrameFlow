"""工具类"""
import json
from SubAPI.DataManage.ImportPack import *
from pandas.core.util.hashing import hash_pandas_object

logger = LogClass.get_logger(__name__, console_level='WARNING')

PD_LOAD_FUNC = {
    '.csv': pd.read_csv,
    '.xlsx': pd.read_excel,
    '.xls': pd.read_excel,
    '.feather': pd.read_feather,
}  # 加载数据函数映射字典


def data_frame_to_hash(data: pd.DataFrame) -> int:
    """返回整个 DataFrame 的哈希值"""
    if isinstance(data, pd.DataFrame):
        # 方案A：返回整数哈希（推荐，最快）
        return int(hash_pandas_object(data, index=False).sum())
    return 0


def deep_dict_hash(d: dict) -> str:
    """处理嵌套字典的哈希"""
    json_str = json.dumps(d, sort_keys=True, default=str)
    return hashlib.md5(json_str.encode()).hexdigest()


def load_feather(file_path: str, columns=None, dtype=None) -> pd.DataFrame:
    """
    加载feather文件
    :param file_path: 文件路径
    :param columns: 列头
    :param dtype: 类型
    """
    try:
        load_pd = pd.DataFrame(columns=columns)
        if File.check_exist(file_path):
            extension = FileBase(file_path).extension
            func = PD_LOAD_FUNC.get(extension, None)
            if func is not None:
                load_pd = func(file_path)
        if dtype is not None:
            load_pd = load_pd.astype(dtype)
        return load_pd
    except Exception as e:
        logger.exception(f'加载失败: {e}')
        return pd.DataFrame()


def save_pandas(file_path: str, df: pd.DataFrame) -> bool:
    """保存pandas表格"""
    extension = FileBase(file_path).extension
    FileBase(FileBase(file_path).dir_name).ensure_exists()  # 确保文件夹存在
    try:
        if extension == '.xlsx':
            df.to_excel(file_path, index=False)
        elif extension == '.csv':
            df.to_csv(file_path, index=False, encoding='utf-8')
        elif extension == '.feather':
            df.to_feather(file_path)
        else:
            raise TypeError(f'不支持的保存格式:{extension}')
        return True
    except Exception as e:
        logger.exception(f'保存失败: {e}')
        return False


@singleton_decorator
class DataManage:
    """
    数据类,单例模式
    用于管理DataBase的读取、自动保存
    data_object内存储了全部的DataBase子类实例
    """
    data_object: dict[str, 'DataBase'] = {}  # {ClassName:DataBase}

    def __init__(self):
        # 实例属性
        self.isRunning = True  # 是否正在运行
        self.isAutoSave = False  # 是否正在自动保存
        # 实例化全部的DataBase子类,子类在实例话时会默认调用该管理类的add_data_object方法
        # for data_subclass in DataBase.__subclasses__():
        #     data_subclass()
        # 自动保存线程
        self._auto_save_timer = ReuseTimer(60, self.__auto_save)
        self._auto_save_timer.start()

    def add_data_object(self, data_object: 'DataBase') -> Task | None:
        name = data_object.__class__.__name__
        if name not in self.__class__.data_object.keys():
            self.__class__.data_object.update({name: data_object})
            task = Task(data_object.load, GlobalValue.GLOBAL_TASK_MANAGE, name=name)
            task.finish_signal.connect(self.__data_callback)
            task.start(priority=3)
            return task
        else:
            return None

    def __data_callback(self, task: Task):
        """数据类加载后的回调函数"""
        data_object = self.data_object.get(task.name, None)
        if data_object is not None:
            data_object.set_data(task.result())
            data_object.load_signal.emit(task.result())
            data_object.loaded = True

    def __auto_save(self):
        """自动保存函数"""
        for name, data in self.__class__.data_object.items():
            if self.isRunning:
                self.isAutoSave = True
                logger.info(f'{self.__class__.__name__}.__auto_save 正在保存数据:{name}')
                data.save()
                self.isAutoSave = False

    def stop(self):
        self.isRunning = False
        self._auto_save_timer.stop()
        logger.info(f'{self.__class__.__name__}.stop 关闭自动保存线程')
        while self.isAutoSave: time.sleep(0.2)  # 等待自动保存线程完成
        logger.info(f'{self.__class__.__name__}.stop 正在保存全部数据')
        # 保存全部数据
        for name, data in self.__class__.data_object.items(): data.save()
        logger.info(f'{self.__class__.__name__}.stop 已经保存全部数据')


class DataBase:
    """
    数据基类,使用with语句自动加锁并返回内部数据(推荐用法)
    with语句退出后会计算当前数据是否发生改变
    使用示例
    with DataBase() as df:
        print(df) -> self.__data
    内部自带四个信号
        self.load_signal = TaskSignal()  # 加载完成的信号,发送加载完成的数据
        self.change_signal = TaskSignal()  # 数据修改信号,发送类本身
    """

    def __init__(self, local_path: str = None):
        """
        :param local_path:本地路径
        """
        self.loaded = False  # 是否加载完本地数据
        self.local_path = local_path  # 本地数据路径
        self.__data = None  # 数据对象
        self.__lock = threading.RLock()  # 同一线程可重入线程锁
        self.__enter_hash = None  # 进入时的数据哈希值（用于检测变化）
        self.load_signal = TaskSignal()  # 加载完成的信号,发送加载完成的数据
        self.change_signal = TaskSignal()  # 数据修改信号,发送类本身
        DataManage().add_data_object(self)

    def load_callback(self, func):
        self.load_signal.connect_once(func)
        if self.is_loaded():
            self.load_signal.emit(self.data)

    def is_loaded(self, timeout: float | int = None) -> bool:
        """
        是否加载完本地数据
        :param timeout:等待到加载完成的超时时间（秒），None为不等待直接返回状态
        :return: 是否已加载完成
        """
        if timeout is not None and isinstance(timeout, (float, int)):
            timeout = max(timeout, 0)
            start_time = time.time()
            while not self.loaded:
                if timeout != 0 and time.time() - start_time >= timeout:
                    return False
                time.sleep(0.1)
            return True
        return self.loaded

    def __repr__(self):
        return str(self.__data)

    @property
    def lock(self):
        """获取锁"""
        return self.__lock

    @property
    def data(self) -> pd.DataFrame | EasyConfig:
        """获取数据"""
        return self.__data

    def set_data(self, data):
        """设置内部数据"""
        with self.__lock:
            old_hash, new_hash = 0, 0
            if isinstance(self.__data, pd.DataFrame):
                old_hash = data_frame_to_hash(self.__data)
                new_hash = data_frame_to_hash(data)
            elif isinstance(self.__data, EasyConfig):
                old_hash = deep_dict_hash(self.__data.get_config_data())
                new_hash = deep_dict_hash(data.get_config_data())
            self.__data = data
            if old_hash != new_hash:
                self.change_signal.emit(self)

    def load(self):
        """加载数据的方法"""
        raise NotImplementedError('请实现load方法')

    def save(self):
        """保存数据的方法"""
        raise NotImplementedError('请实现save方法')

    def __enter__(self):
        """进入上下文管理器，自动加锁并返回数据"""
        self.__lock.acquire()
        return self.__data

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器，自动释放锁"""
        self.__lock.release()
        return False  # 不抑制异常

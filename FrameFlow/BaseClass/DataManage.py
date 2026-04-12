"""
数据管理
新增数据类需要继承DataBase类并重写load方法和save方法
创建DataBase类的子类实例并
调用DataManage.add_data_object方法即可自动加载本地数据和自动保存数据

DataBase类的子类其内部数据保存在变量self.__data中
使用DataBase.data方法即可获取到内部数据
多线程环境下对数据进行操作时请使用
with DataBase.lock:
    data = DataBase.data
"""
import pandas as pd, os, time
import threading
from threading import Lock
from BaseClass.TaskManage import Task, TaskManage, TaskSignal
from BaseClass import GlobalValue
from Fun.Norm import file, general, get


class DataManage:
    """
    数据类,用于管理DataBase的读取、自动保存,推荐只实例化一次
    data_object内存储了全部的DataBase子类实例
    """
    data_object = {}  # {ClassName:DataBase}
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        # 实例属性
        self.isRunning = True  # 是否正在运行
        self.__task_manage = TaskManage(2)
        self.isAutoSave = False  # 是否正在自动保存
        self.timer = general.ReuseTimer(60, self.__auto_save, daemon=True)
        self.timer.start()
        # 实例化全部的DataBase子类
        for data_subclass in DataBase.__subclasses__():
            data_subclass()

    @classmethod
    def add_data_object(cls, data_object) -> Task | None:
        self = cls()
        name = data_object.__class__.__name__
        if name not in self.__class__.data_object.keys():
            self.__class__.data_object.update({name: data_object})
            task = Task(data_object.load, self.__task_manage, name=name)
            task.finish_signal.connect(self.__data_callback)
            task.start()
            return task
        else:
            return None

    def __data_callback(self, task: Task):
        """数据类加载后的回调函数"""
        data_object: DataBase = self.__class__.data_object.get(task.name, None)
        if data_object is not None:
            data_object.set_data(task.result())
            data_object.load_signal.emit(task.result())
            data_object.loaded = True

    def __auto_save(self):
        """自动保存函数"""
        for name, data in self.__class__.data_object.items():
            if self.isRunning:
                self.isAutoSave = True
                # print(f'{self.__class__.__name__}.__auto_save 正在保存数据:{name} 时间:{get.now_time()}')
                data.save()
                self.isAutoSave = False

    @classmethod
    def stop(cls):
        self = cls()
        self.isRunning = False
        self.__task_manage.stop()
        print(f'{self.__class__.__name__}.stop 关闭自动保存线程')
        self.timer.stop()
        while self.isAutoSave:  # 等待自动保存线程完成
            time.sleep(0.2)
        print(f'{self.__class__.__name__}.stop 正在保存全部数据 时间:{get.now_time()}')
        # 保存全部数据
        for name, data in self.__class__.data_object.items():
            data.save()


class DataBase:
    """数据基类"""
    pd_load_func = {
        '.csv': pd.read_csv,
        '.xlsx': pd.read_excel,
        '.xls': pd.read_excel,
        '.feather': pd.read_feather,
    }

    def __init__(self, local_path: str = None):
        """
        :param local_path:本地路径
        """
        self.loaded = False  # 是否加载完本地数据
        self.local_path = local_path  # 本地数据路径
        self.__data = None  # 数据对象
        self.__lock = threading.Lock()  # 线程锁
        self.load_signal = TaskSignal()  # 加载完成的信号,发送加载完成的数据
        DataManage.add_data_object(self)

    @classmethod
    def load_callback(cls, func):
        self = cls()
        self.load_signal.connect(func)
        if self.is_loaded():
            self.load_signal.emit(self.data())

    @classmethod
    def is_loaded(cls, wait: float | int = None) -> bool:
        """
        是否加载完本地数据
        :param wait:等待到加载完成,输入等待间隔
        """
        self = cls()
        if wait is not None and isinstance(wait, (float, int)):
            wait_time = wait if isinstance(wait, (float, int)) and wait >= 0 else 1
            while not self.loaded: time.sleep(wait_time)
            return True
        return self.loaded

    def __repr__(self):
        return str(self.__data)

    @classmethod
    @property
    def lock(cls):
        """获取锁"""
        return cls().__lock

    @property
    def data(self):
        """获取数据"""
        return self.__data

    def set_data(self, data, use_lock=True):
        """设置内部数据"""
        if use_lock:
            with self.__lock:
                self.__data = data
        else:
            self.__data = data

    def load(self):
        """加载数据的方法"""

    def save(self):
        """保存数据的方法"""

    @classmethod
    def load_pandas(cls, file_path, columns, dtpye=None) -> pd.DataFrame:
        load_pd = pd.DataFrame(columns=columns)
        if file.check_exist(file_path):
            extension = file.get_file_extension(file_path)
            func = cls.pd_load_func.get(extension, None)
            if func is not None:
                load_pd = func(file_path)
        if dtpye is not None:
            load_pd = load_pd.astype(dtpye)
        return load_pd

    @staticmethod
    def save_pandas(file_path: str, df: pd.DataFrame) -> bool:
        """保存pandas表格"""
        extension = os.path.splitext(file_path)[1]
        file.ensure_exist(os.path.dirname(file_path))
        if extension == '.xlsx':
            df.to_excel(file_path, index=False)
        elif extension == '.csv':
            df.to_csv(file_path, index=False, encoding='utf-8')
        elif extension == '.feather':
            df.to_feather(file_path)
        return True


class SearchData(DataBase):
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        super().__init__()

    @classmethod
    def add_data(cls, new_data: pd.DataFrame):
        """新增结构化数据"""
        self = cls()
        with self.lock:
            self.set_data(pd.concat(
                [self.data(), new_data]).drop_duplicates(
                subset=['id', '关键词', '类别码', '分级码'],
                keep='last', ignore_index=True), use_lock=False)

    @classmethod
    def data(cls) -> pd.DataFrame:
        return super(SearchData, cls()).data

    @classmethod
    def clear(cls):
        self = cls()
        self.set_data(pd.DataFrame(columns=GlobalValue.search_columns).astype(GlobalValue.search_dtype))

    @staticmethod
    def load() -> pd.DataFrame:
        load_pd = pd.DataFrame(columns=GlobalValue.search_columns).astype(GlobalValue.search_dtype)
        return load_pd


class ImageInfo(DataBase):
    _instance = None
    _lock = threading.Lock()
    columns = GlobalValue.ImageInfoColumns()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        super().__init__(GlobalValue.image_info_path)

    @classmethod
    def add_data(cls, new_data: pd.DataFrame):
        """新增结构化数据"""
        self = cls()
        with self.lock:
            self.set_data(pd.concat(
                [self.data(), new_data]).drop_duplicates(
                subset=['id'], keep='last', ignore_index=True), use_lock=False)

    @classmethod
    def del_data(cls, mask_bool: pd.Series, use_lock=True):
        """传入bool掩码,True表示留下,False表示删除"""
        self = cls()
        if use_lock:
            with self.lock:
                self.set_data(self.data()[mask_bool].reset_index(drop=True), use_lock=False)
        else:
            self.set_data(self.data()[mask_bool].reset_index(drop=True), use_lock=False)

    @classmethod
    def to_excel(cls) -> str | None:
        self = cls()
        if self.is_loaded():
            save_path = os.path.join(GlobalValue.config_dir, 'image_info.xlsx')
            self.data().to_excel(save_path, index=False)
            return save_path

    @classmethod
    def load_from_excel(cls, file_path: str) -> bool:
        self = cls()
        if self.is_loaded():
            load_pd = self.load_pandas(file_path, GlobalValue.image_info_columns, GlobalValue.image_info_dtype)
            load_pd.sort_values(by=['关键词', '日期'], ascending=[True, False],
                                key=self.__smart_key, inplace=True)
            self.add_data(load_pd)
            return True
        return False

    @classmethod
    def data(cls) -> pd.DataFrame:
        return super(ImageInfo, cls()).data

    def __smart_key(self, series):
        if series.name == '关键词':
            return series.str.lower()
        else:
            return series  # 日期列不做任何转换

    @classmethod
    def load(cls) -> pd.DataFrame:
        self = cls()
        load_pd = self.load_pandas(self.local_path, GlobalValue.image_info_columns, GlobalValue.image_info_dtype)
        if not load_pd.empty:
            # load_pd.dropna(how='any', inplace=True)  # 删除有缺失值的行
            # reset_index->删除索引
            load_pd = load_pd[~(load_pd == '').any(axis=1)].reset_index(drop=True)  # 删除有''的行
            # 检查本地路径的文件是否存在,将不存在的路径改为''
            mask = pd.Series(file.check_exist(load_pd['本地路径']))
            load_pd.loc[~mask, '本地路径'] = ''
            # 将结果排序
            load_pd.sort_values(by=['关键词', '日期'], ascending=[True, False],
                                key=self.__smart_key, inplace=True)
            load_pd.reset_index(drop=True, inplace=True)
        return load_pd

    @classmethod
    def save(cls):
        self = cls()
        if self.data() is not None:
            with self.lock:
                self.save_pandas(self.local_path, self.data())


class KeyWord(DataBase):
    _instance = None
    _lock = threading.Lock()
    columns = GlobalValue.KeyWordColumns()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        super().__init__(GlobalValue.key_word_path)

    @classmethod
    def data(cls) -> pd.DataFrame:
        return super(KeyWord, cls()).data

    @classmethod
    def add_data(cls, new_data: pd.DataFrame):
        """新增结构化数据"""
        self = cls()
        with self.lock:
            self.set_data(pd.concat(
                [self.data(), new_data]).drop_duplicates(subset=['关键词'], keep='last').sort_values(
                '关键词', key=lambda x: x.str.lower(), ignore_index=True), use_lock=False)

    @classmethod
    def del_data(cls, key: str | list):
        """删除某关键词"""
        self = cls()
        if isinstance(key, str):
            key = [key]
        with self.lock:
            self.set_data(
                self.data()[~self.data()['关键词'].isin(key)].reset_index(drop=True), use_lock=False)

    @classmethod
    def to_excel(cls) -> str | None:
        self = cls()
        if self.is_loaded():
            save_path = os.path.join(GlobalValue.config_dir, 'key_word.xlsx')
            self.data().to_excel(save_path, index=False)
            return save_path

    @classmethod
    def load_from_excel(cls, file_path: str) -> bool:
        self = cls()
        if self.is_loaded():
            load_pd = self.load_pandas(file_path, GlobalValue.key_word_columns, GlobalValue.key_word_dtype)
            load_pd.sort_values('关键词', key=lambda x: x.str.lower(), inplace=True)
            # 防止excle修改类型
            load_pd['分级码'].str.zfill(3)
            load_pd['类别码'].str.zfill(3)
            self.add_data(load_pd)
            return True
        return False

    @classmethod
    def load(cls) -> pd.DataFrame:
        self = cls()
        load_pd = self.load_pandas(self.local_path, GlobalValue.key_word_columns, GlobalValue.key_word_dtype)
        load_pd.sort_values('关键词', key=lambda x: x.str.lower(), inplace=True)
        load_pd.reset_index(drop=True, inplace=True)
        return load_pd

    @classmethod
    def save(cls):
        self = cls()
        if self.data() is not None:
            with self.lock:
                self.save_pandas(self.local_path, self.data())


class ImageHistory(DataBase):
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        super().__init__(GlobalValue.image_history_path)

    @classmethod
    def add_data(cls, new_data: pd.DataFrame):
        """新增结构化数据"""
        self = cls()
        with self.lock:
            self.set_data(pd.concat(
                [self.data(), new_data]).drop_duplicates(
                subset=['本地路径'], keep='last', ignore_index=True), use_lock=False)

    @classmethod
    def del_data(cls, mask_bool: pd.Series, use_lock=True):
        """传入bool掩码,True表示留下,False表示删除"""
        self = cls()
        if use_lock:
            with self.lock:
                self.set_data(self.data()[mask_bool].reset_index(drop=True), use_lock=False)
        else:
            self.set_data(self.data()[mask_bool].reset_index(drop=True), use_lock=False)

    @classmethod
    def clear(cls):
        self = cls()
        self.set_data(pd.DataFrame(columns=GlobalValue.image_history_columns).astype(GlobalValue.image_history_dtype))

    @classmethod
    def data(cls) -> pd.DataFrame:
        return super(ImageHistory, cls()).data

    @classmethod
    def to_excel(cls) -> str | None:
        self = cls()
        if self.is_loaded():
            save_path = os.path.join(GlobalValue.config_dir, 'image_history.xlsx')
            self.data().to_excel(save_path, index=False)
            return save_path

    @classmethod
    def load_from_excel(cls, file_path: str) -> bool:
        self = cls()
        if self.is_loaded():
            load_pd = self.load_pandas(file_path, GlobalValue.image_history_columns, GlobalValue.image_history_dtype)
            self.add_data(load_pd)
            return True
        return False

    @classmethod
    def load(cls) -> pd.DataFrame:
        self = cls()
        load_pd = self.load_pandas(self.local_path, GlobalValue.image_history_columns, GlobalValue.image_history_dtype)
        load_pd.reset_index(drop=True, inplace=True)
        return load_pd

    @classmethod
    def save(cls):
        self = cls()
        if self.data() is not None:
            with self.lock:
                self.save_pandas(self.local_path, self.data())


class ConfigData(DataBase):
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        super().__init__(GlobalValue.config_path)

    @classmethod
    def data(cls) -> file.EasyConfig:
        return super(ConfigData, cls()).data

    @classmethod
    def load(cls) -> file.EasyConfig:
        self = cls()
        config = file.EasyConfig(self.local_path)
        config.load_config()
        return config

    @classmethod
    def save(cls):
        self = cls()
        if self.data() is not None:
            with self.lock:
                self.data().save()


if __name__ == '__main__':
    import time

    DataManage()
    while not ImageInfo.is_loaded(): time.sleep(1)
    with ImageInfo.lock:
        print(ImageInfo.data())

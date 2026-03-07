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
import pandas as pd, os
from threading import Lock
from GlobalModule.TaskManage import Task, TaskManage
from GlobalModule import GlobalValue
from Fun.Norm import file, general, get


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
        self.__lock = Lock()  # 线程锁

    def __repr__(self):
        return str(self.__data)

    @property
    def lock(self):
        """获取锁"""
        return self.__lock

    @property
    def data(self):
        """获取数据"""
        return self.__data

    def set_data(self, data):
        """设置内部数据"""
        with self.__lock:
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
        """保存pandas表格,传入空表格时返回Flase,保存成功返回True"""
        extension = os.path.splitext(file_path)[1]
        file.ensure_exist(os.path.dirname(file_path))
        if df.empty:
            return False
        if extension == '.xlsx':
            df.to_excel(file_path, index=False)
        elif extension == '.csv':
            df.to_csv(file_path, index=False, encoding='utf-8')
        elif extension == '.feather':
            df.to_feather(file_path)
        return True


class SearchData(DataBase):
    def __init__(self):
        super().__init__()

    def add_data(self, new_data: pd.DataFrame):
        """新增结构化数据"""
        self.set_data(pd.concat(
            [self.data, new_data]).drop_duplicates(
            subset=['id', '关键词', '类别码', '分级码'],
            keep='last', ignore_index=True))

    @property
    def data(self) -> pd.DataFrame:
        return super().data

    def load(self) -> pd.DataFrame:
        load_pd = pd.DataFrame(columns=GlobalValue.search_columns).astype(GlobalValue.search_dtype)
        return load_pd


class ImageInfo(DataBase):

    def __init__(self):
        super().__init__(GlobalValue.image_info_path)

    def add_data(self, new_data: pd.DataFrame):
        """新增结构化数据"""
        self.set_data(pd.concat(
            [self.data, new_data]).drop_duplicates(
            subset=['id'], keep='last', ignore_index=True))

    @property
    def data(self) -> pd.DataFrame:
        return super().data

    def load(self) -> pd.DataFrame:
        load_pd = self.load_pandas(self.local_path, GlobalValue.image_info_columns, GlobalValue.image_info_dtype)
        if not load_pd.empty:
            # load_pd.dropna(how='any', inplace=True)  # 删除有缺失值的行
            # reset_index->删除索引
            load_pd = load_pd[~(load_pd == '').any(axis=1)].reset_index(drop=True)  # 删除有''的行
            # 检查本地路径的文件是否存在,将不存在的路径改为''
            mask = pd.Series(file.check_exist(load_pd['本地路径']))
            load_pd.loc[~mask, '本地路径'] = ''
        return load_pd

    def save(self):
        if self.data is not None:
            with self.lock:
                self.save_pandas(self.local_path, self.data)


class KeyWord(DataBase):
    def __init__(self):
        super().__init__(GlobalValue.key_word_path)

    @property
    def data(self) -> pd.DataFrame:
        return super().data

    def load(self) -> pd.DataFrame:
        load_pd = self.load_pandas(self.local_path, GlobalValue.key_word_columns, GlobalValue.key_word_dtype)
        return load_pd

    def save(self):
        if self.data is not None:
            with self.lock:
                self.save_pandas(self.local_path, self.data)


class ImageHistory(DataBase):
    def __init__(self):
        super().__init__(GlobalValue.image_history_path)

    @property
    def data(self) -> pd.DataFrame:
        return super().data

    def load(self) -> pd.DataFrame:
        load_pd = self.load_pandas(self.local_path, GlobalValue.image_history_columns, GlobalValue.image_history_dtype)
        return load_pd

    def save(self):
        if self.data is not None:
            with self.lock:
                self.save_pandas(self.local_path, self.data)


class ConfigData(DataBase):
    def __init__(self):
        super().__init__(GlobalValue.config_path)

    @property
    def data(self) -> file.EasyConfig:
        return super().data

    def load(self) -> file.EasyConfig:
        config = file.EasyConfig(self.local_path)
        config.load_config()
        return config

    def save(self):
        if self.data is not None:
            with self.lock:
                self.data.save()


class DataManage:
    """
    数据类,用于管理DataBase的读取、自动保存,推荐只实例化一次
    data_object内存储了全部的DataBase子类实例
    """
    init_object = []  # 该类的全部实例化对象
    data_object = {}  # {ClassName:DataBase}
    auto_save_state = False  # 用于确保自动保存线程只开启一次
    data_save_stop = False  # 用于确保全部数据已经被保存过一次,不重复被保存

    def __init__(self):
        self.isRunning = True  # 是否正在运行
        self.__task_manage = TaskManage()
        if not self.__class__.auto_save_state:
            self.__class__.auto_save_state = True
            self.isAutoSave = False  # 是否正在自动保存
            self.timer = general.ReuseTimer(60, self.__auto_save, daemon=True)
            self.timer.start()
        if self not in self.__class__.init_object:
            self.__class__.init_object.append(self)

    def add_data_object(self, data_object: DataBase) -> Task | None:
        name = data_object.__class__.__name__
        if name not in self.__class__.data_object.keys():
            self.__class__.data_object.update({name: data_object})
            task = Task(func=data_object.load, name=name)
            task.add_done_callback(self.__data_callback)
            self.__task_manage.add_task(task)
            return task
        else:
            return None

    def __data_callback(self, task: Task):
        """数据类加载后的回调函数"""
        data_object: DataBase = self.__class__.data_object.get(task.name, None)
        if data_object is not None:
            data_object.set_data(task.result())

    def __auto_save(self):
        """自动保存函数"""
        for name, data in self.__class__.data_object.items():
            if self.isRunning:
                self.isAutoSave = True
                # print(f'{self.__class__.__name__}.__auto_save 正在保存数据:{name} 时间:{get.now_time()}')
                data.save()
                self.isAutoSave = False

    def stop(self):
        self.isRunning = False
        self.__task_manage.stop()
        if hasattr(self, 'timer'):
            print(f'{self.__class__.__name__}.stop 关闭自动保存线程')
            self.timer.stop()
            while self.isAutoSave:  # 等待自动保存线程完成
                time.sleep(0.2)
        if not self.__class__.data_save_stop:
            print(f'{self.__class__.__name__}.stop 正在保存全部数据 时间:{get.now_time()}')
            self.__class__.data_save_stop = True
            # 保存全部数据
            for name, data in self.__class__.data_object.items():
                data.save()




if __name__ == '__main__':
    import time

    start = time.time()
    data_manage = DataManage()

    image_info = ImageInfo()
    key_word = KeyWord()
    image_history = ImageHistory()
    config_data = ConfigData()

    image_info_task = data_manage.add_data_object(image_info)
    key_word_task = data_manage.add_data_object(key_word)
    image_history_task = data_manage.add_data_object(image_history)
    config_data_task = data_manage.add_data_object(config_data)
    while (not image_info_task.done() or
           not key_word_task.done() or
           not image_history_task.done()):
        time.sleep(1)
    print(data_manage.data_object)
    data_manage.stop()
    end = time.time()
    print(end - start)

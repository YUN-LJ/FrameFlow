"""数据类"""
from SubAPI.DataManage.ImportPack import *
from SubAPI.DataManage.Tools import load_feather, save_pandas, DataBase
from Fun.BaseTools import Time

logger = LogClass.get_logger(__name__, console_level='WARNING')


@singleton_decorator
class SearchData(DataBase):

    def __init__(self):
        super().__init__()

    def add_data(self, new_data: pd.DataFrame):
        """新增结构化数据"""
        with self.lock:
            self.set_data(
                pd.concat([self.data, new_data]).drop_duplicates(
                    subset=['id', '关键词', '类别码', '分级码'], keep='last', ignore_index=True))

    def clear(self):
        self.set_data(pd.DataFrame(columns=DataConfig.search_columns).astype(DataConfig.search_dtype))

    def load(self) -> pd.DataFrame:
        load_pd = pd.DataFrame(columns=DataConfig.search_columns).astype(DataConfig.search_dtype)
        return load_pd

    def save(self):
        pass


@singleton_decorator
class ImageInfo(DataBase):
    columns = DataConfig.ImageInfoColumns()

    def __init__(self):
        super().__init__(DataConfig.image_info_path)

    def add_data(self, new_data: pd.DataFrame):
        """新增结构化数据"""
        with self.lock:
            self.set_data(
                pd.concat([self.data, new_data]).drop_duplicates(subset=['id'], keep='last', ignore_index=True))

    def del_data(self, mask_bool: pd.Series):
        """传入bool掩码,True表示留下,False表示删除"""
        with self.lock:
            self.set_data(self.data[mask_bool].reset_index(drop=True))

    def del_row(self, image_id: str):
        """删除指定图像ID的一行数据"""
        with self.lock:
            mask = self.data['id'] != image_id
            self.del_data(mask)

    def to_excel(self) -> str | None:
        """转为excel保存,返回保存路径"""
        if self.is_loaded():
            save_path = os.path.join(DataConfig.CONFIG_DIR, 'image_info.xlsx')
            self.data.to_excel(save_path, index=False)
            return save_path

    def load_from_excel(self, file_path: str) -> bool:
        """从excel中加载数据"""
        if self.is_loaded():
            load_pd = load_feather(file_path, DataConfig.image_info_columns, DataConfig.image_info_dtype)
            load_pd.sort_values(by=['关键词', '日期'], ascending=[True, False], key=self.__smart_key, inplace=True)
            self.add_data(load_pd)
            return True
        return False

    def __smart_key(self, series):
        if series.name == '关键词':
            return series.str.lower()
        else:
            return series  # 日期列不做任何转换

    @Time.timer_decorator(name='图像信息数据有效性检查')
    def check_files(self):
        """检查本地文件是否存在"""
        self.is_loaded(0)
        logger.info('检查文件是否存在中...')
        if self.data is not None:
            mask = pd.Series(File.check_exist(self.data['本地路径']))
            self.data.loc[~mask, '本地路径'] = ''

    def load(self) -> pd.DataFrame:
        load_pd = load_feather(self.local_path, DataConfig.image_info_columns, DataConfig.image_info_dtype)
        if not load_pd.empty:
            # load_pd.dropna(how='any', inplace=True)  # 删除有缺失值的行
            # reset_index -> 删除索引
            load_pd = load_pd[~(load_pd == '').any(axis=1)].reset_index(drop=True)  # 删除有''的行
            # 将结果排序
            load_pd.sort_values(by=['关键词', '日期'], ascending=[True, False],
                                key=self.__smart_key, inplace=True)
            load_pd.reset_index(drop=True, inplace=True)
            # 后台检查文件是否存在
            check_task = Task(self.check_files, GlobalValue.GLOBAL_TASK_MANAGE,
                              name=f'{self.__class__.__name__}.check_files')
            check_task.start(priority=4)
        return load_pd

    def save(self):
        if self.data is not None:
            with self.lock:
                self.set_data(self.data[~(self.data == '').any(axis=1)].reset_index(drop=True))  # 删除有''的行
                save_pandas(self.local_path, self.data)


@singleton_decorator
class KeyWord(DataBase):
    columns = DataConfig.KeyWordColumns()

    def __init__(self):
        super().__init__(DataConfig.key_word_path)

    def add_data(self, new_data: pd.DataFrame):
        """新增结构化数据"""
        with self.lock:
            self.set_data(pd.concat(
                [self.data, new_data]).drop_duplicates(subset=['关键词'], keep='last').sort_values(
                '关键词', key=lambda x: x.str.lower(), ignore_index=True))

    def del_data(self, key: str | list):
        """删除某关键词"""
        if isinstance(key, str):
            key = [key]
        with self.lock:
            self.set_data(
                self.data[~self.data['关键词'].isin(key)].reset_index(drop=True))

    def to_excel(self) -> str | None:
        if self.is_loaded():
            save_path = os.path.join(DataConfig.CONFIG_DIR, 'key_word.xlsx')
            self.data.to_excel(save_path, index=False)
            return save_path

    def load_from_excel(self, file_path: str) -> bool:
        if self.is_loaded():
            load_pd = load_feather(file_path, DataConfig.key_word_columns, DataConfig.key_word_dtype)
            load_pd.sort_values('关键词', key=lambda x: x.str.lower(), inplace=True)
            # 防止excle修改类型
            load_pd['分级码'].str.zfill(3)
            load_pd['类别码'].str.zfill(3)
            self.add_data(load_pd)
            return True
        return False

    def load(self) -> pd.DataFrame:
        load_pd = load_feather(self.local_path, DataConfig.key_word_columns, DataConfig.key_word_dtype)
        load_pd.sort_values('关键词', key=lambda x: x.str.lower(), inplace=True)
        load_pd.reset_index(drop=True, inplace=True)
        return load_pd

    def save(self):
        if self.data is not None:
            with self.lock:
                save_pandas(self.local_path, self.data)


@singleton_decorator
class ImageHistory(DataBase):

    def __init__(self):
        super().__init__(DataConfig.image_history_path)

    def add_data(self, new_data: pd.DataFrame):
        """新增结构化数据"""
        with self.lock:
            self.set_data(pd.concat(
                [self.data, new_data]).drop_duplicates(
                subset=['本地路径'], keep='last', ignore_index=True))

    def del_data(self, mask_bool: pd.Series):
        """传入bool掩码,True表示留下,False表示删除"""
        with self.lock:
            self.set_data(self.data[mask_bool].reset_index(drop=True))

    def clear(self):
        self.set_data(pd.DataFrame(columns=DataConfig.image_history_columns).astype(DataConfig.image_history_dtype))

    def to_excel(self) -> str | None:
        if self.is_loaded():
            save_path = os.path.join(DataConfig.CONFIG_DIR, 'image_history.xlsx')
            self.data.to_excel(save_path, index=False)
            return save_path

    def load_from_excel(self, file_path: str) -> bool:
        if self.is_loaded():
            load_pd = load_feather(file_path, DataConfig.image_history_columns, DataConfig.image_history_dtype)
            self.add_data(load_pd)
            return True
        return False

    def load(self) -> pd.DataFrame:
        load_pd = load_feather(self.local_path, DataConfig.image_history_columns, DataConfig.image_history_dtype)
        load_pd.reset_index(drop=True, inplace=True)
        return load_pd

    def save(self):
        if self.data is not None:
            with self.lock:
                save_pandas(self.local_path, self.data)


@singleton_decorator
class ConfigData(DataBase):

    def __init__(self):
        super().__init__(DataConfig.config_path)

    def load(self) -> EasyConfig:
        config = EasyConfig(self.local_path)
        config.load_config()
        return config

    def save(self):
        if self.data is not None:
            with self.lock:
                self.data.save()

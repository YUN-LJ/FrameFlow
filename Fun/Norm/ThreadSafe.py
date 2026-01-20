"""线程安全类"""
import os
from threading import Lock
from typing import Any, Optional, List as TypingList, Union, Iterator
import copy
from pandas import DataFrame


class Dict:
    """支持读取、修改、删除的字典"""

    def __init__(self, auto_delete=False):
        """
        :param auto_delete: 取出值时删除值
        """
        self.__dict = {}  # 内部字典
        self.__lock = Lock()  # 内部锁
        self.__auto_delete = auto_delete

    def get(self, key, default=None):
        with self.__lock:
            if self.__auto_delete:
                return self.__dict.pop(key, default)
            else:
                return self.__dict.get(key, default)

    def pop(self, key, default=None):
        with self.__lock:
            return self.__dict.pop(key, default)

    def append(self, key, value) -> bool:
        """键不存在时添加"""
        with self.__lock:
            if key not in self.__dict:
                self.__dict[key] = value
                return True
            else:
                return False

    @property
    def get_lock(self):
        return self.__lock

    @property
    def get_dict(self):
        return self.__dict

    def __setitem__(self, key, value):
        with self.__lock:
            self.__dict[key] = value

    def __getitem__(self, key):
        with self.__lock:
            if self.__auto_delete:
                return self.__dict.pop(key)
            else:
                return self.__dict[key]

    def __delitem__(self, key):
        with self.__lock:
            del self.__dict[key]

    def __str__(self):
        return str(self.__dict)


class List:
    """线程安全的列表，支持读取、修改、删除操作"""

    def __init__(self, auto_delete: bool = False, initial_data: Optional[list] = None):
        """
        :param auto_delete: 取出值时是否自动删除
        :param initial_data: 初始数据
        """
        self.__list = [] if initial_data is None else list(initial_data)
        self.__lock = Lock()  # 内部锁
        self.__auto_delete = auto_delete

    def get(self, index: int, default: Any = None) -> Any:
        """
        获取指定索引的值

        :param index: 索引位置
        :param default: 索引不存在时的默认值
        :return: 索引处的值或默认值
        """
        with self.__lock:
            try:
                if self.__auto_delete:
                    value = self.__list.pop(index)
                    return value
                else:
                    return self.__list[index]
            except (IndexError, TypeError):
                return default

    def pop(self, index: int = -1, default: Any = None) -> Any:
        """
        移除并返回指定索引的元素

        :param index: 索引位置，默认为-1（最后一个）
        :param default: 索引不存在时的默认值
        :return: 移除的元素或默认值
        """
        with self.__lock:
            try:
                return self.__list.pop(index)
            except (IndexError, TypeError):
                return default

    def append(self, item: Any) -> None:
        """在列表末尾添加元素"""
        with self.__lock:
            self.__list.append(item)

    def insert(self, index: int, item: Any) -> None:
        """在指定位置插入元素"""
        with self.__lock:
            self.__list.insert(index, item)

    def remove(self, item: Any) -> bool:
        """
        移除第一个匹配的元素

        :param item: 要移除的元素
        :return: 是否成功移除
        """
        with self.__lock:
            try:
                self.__list.remove(item)
                return True
            except ValueError:
                return False

    def clear(self) -> None:
        """清空列表"""
        with self.__lock:
            self.__list.clear()

    def copy(self) -> list:
        """返回列表的浅拷贝"""
        with self.__lock:
            return self.__list.copy()

    def deep_copy(self) -> list:
        """返回列表的深拷贝"""
        with self.__lock:
            return copy.deepcopy(self.__list)

    def slice(self, start: int = 0, end: Optional[int] = None) -> list:
        """
        返回列表切片

        :param start: 起始索引
        :param end: 结束索引（不包含）
        :return: 切片后的列表
        """
        with self.__lock:
            if end is None:
                return self.__list[start:]
            return self.__list[start:end]

    def extend(self, items: list) -> None:
        """扩展列表"""
        with self.__lock:
            self.__list.extend(items)

    def index(self, item: Any, start: int = 0, end: Optional[int] = None) -> int:
        """
        返回元素第一次出现的索引

        :param item: 要查找的元素
        :param start: 起始搜索位置
        :param end: 结束搜索位置
        :return: 元素的索引，不存在则返回-1
        """
        with self.__lock:
            try:
                if end is None:
                    return self.__list.index(item, start)
                return self.__list.index(item, start, end)
            except ValueError:
                return -1

    def count(self, item: Any) -> int:
        """统计元素出现的次数"""
        with self.__lock:
            return self.__list.count(item)

    def sort(self, key=None, reverse: bool = False) -> None:
        """排序列表"""
        with self.__lock:
            self.__list.sort(key=key, reverse=reverse)

    def reverse(self) -> None:
        """反转列表"""
        with self.__lock:
            self.__list.reverse()

    def __len__(self) -> int:
        """获取列表长度"""
        with self.__lock:
            return len(self.__list)

    def __getitem__(self, index: Union[int, slice]) -> Any:
        """
        获取元素或切片

        支持索引访问和切片操作
        """
        with self.__lock:
            if isinstance(index, slice):
                # 切片操作返回普通列表
                return self.__list[index]

            if self.__auto_delete:
                return self.__list.pop(index)
            else:
                return self.__list[index]

    def __setitem__(self, index: Union[int, slice], value: Any) -> None:
        """
        设置元素或切片

        支持索引赋值和切片赋值
        """
        with self.__lock:
            self.__list[index] = value

    def __delitem__(self, index: Union[int, slice]) -> None:
        """
        删除元素或切片

        支持索引删除和切片删除
        """
        with self.__lock:
            del self.__list[index]

    def __contains__(self, item: Any) -> bool:
        """检查元素是否在列表中"""
        with self.__lock:
            return item in self.__list

    def __iter__(self) -> Iterator:
        """迭代器"""
        with self.__lock:
            # 返回副本的迭代器以避免并发修改问题
            return iter(self.__list.copy())

    def __reversed__(self) -> Iterator:
        """反向迭代器"""
        with self.__lock:
            return reversed(self.__list.copy())

    def __str__(self) -> str:
        """字符串表示"""
        with self.__lock:
            return str(self.__list)

    def __repr__(self) -> str:
        """调试表示"""
        with self.__lock:
            return f"ThreadSafeList({self.__list})"

    @property
    def lock(self) -> Lock:
        """获取内部锁（谨慎使用）"""
        return self.__lock

    @property
    def data(self) -> list:
        """获取内部列表的副本（线程安全）"""
        with self.__lock:
            return self.__list.copy()

    @property
    def length(self) -> int:
        """获取列表长度（属性形式）"""
        with self.__lock:
            return len(self.__list)

    def batch_operation(self, operation_func) -> Any:
        """
        批量操作装饰器

        :param operation_func: 接受列表作为参数的函数
        :return: 操作函数的返回值
        """
        with self.__lock:
            return operation_func(self.__list)

    def find_all(self, condition_func) -> list:
        """
        查找所有满足条件的元素

        :param condition_func: 条件函数，接受元素返回bool
        :return: 满足条件的元素列表
        """
        with self.__lock:
            return [item for item in self.__list if condition_func(item)]

    def remove_all(self, condition_func) -> list:
        """
        移除所有满足条件的元素

        :param condition_func: 条件函数，接受元素返回bool
        :return: 被移除的元素列表
        """
        with self.__lock:
            to_remove = [item for item in self.__list if condition_func(item)]
            self.__list = [item for item in self.__list if not condition_func(item)]
            return to_remove


class SafeDateFrame:
    """线程安全的DataFrame类型"""

    def __init__(self, data=None, columns=None, dtype=None):
        self.__df = DataFrame(data, columns=columns).astype(dtype)
        self.__lock = Lock()

    def __setitem__(self, key, value):
        with self.__lock:
            row_rule, column_name = key
            self.__df.loc[row_rule, column_name] = value

    def __getitem__(self, rule):
        """获取符合条件的列数据"""
        with self.__lock:
            return self.__df[rule].copy(deep=True)

    def __delitem__(self, rule):
        with self.__lock:
            self.__df = self.__df[~rule]

    def Append(self, new_data: DataFrame, func):
        """
        添加新数据
        :param new_data:要添加的新数据
        :param func:添加数据的函数需要有两个形参,返回值会作为内部的DataFrame
        """
        with self.__lock:
            new_df = func(self.__df.copy(deep=True), new_data)
            if isinstance(new_df, DataFrame):
                self.__df = new_df

    def Loc(self, rule):
        """获取符合条件的行数据"""
        with self.__lock:
            return self.__df.loc[rule].copy(deep=True)

    def Save(self, save_path):
        extension = os.path.splitext(save_path)[1]
        with self.__lock:
            if extension == '.xlsx':
                self.__df.to_excel(save_path, index=False)
            elif extension == '.csv':
                self.__df.to_csv(save_path, index=False, encoding='utf-8')
            elif extension == '.feather':
                self.__df.to_feather(save_path)

"""
用于ini文件处理
"""
import configparser, os

from Fun.Norm import get, file


class INI:
    def __init__(self, ini_file: str = None, section_name: str = None):
        """
        :param ini_file:文件路径
        :param section_name:节名
        """
        if ini_file is None:
            self.RUN_PATH = get.run_dir()
            self.INI_FILE = f'{self.RUN_PATH}/config.ini'  # ini文件路径,默认为运行路径
        else:
            self.INI_FILE = ini_file
        if section_name is None:
            self.SECTION_NAME = 'Set'  # ini文件中需要操作的节的名称,默认为Set节
        else:
            self.SECTION_NAME = section_name

    def config_init(self) -> configparser.RawConfigParser:
        """
        实例化configparser.RawConfigParser()类
        """
        config = configparser.RawConfigParser()  # 需要实例化一个ConfigParser对象
        config.optionxform = lambda option: option  # 防止保存文件时键值小写
        config.read(self.INI_FILE, encoding='utf-8')
        return config

    def create(self) -> bool:
        """
        创建一个新的ini文件
        """
        config = self.config_init()
        self.save(config)
        return True

    def append_section(self, section_name: str) -> bool:
        """
        新增节

        :param section_name:要添加的节的名称
        """
        config = self.config_init()
        # 检查要添加的节是否存在
        if not config.has_section(section_name):
            config.add_section(section_name)  # 添加节
            self.save(config)
            return True
        else:
            print(f'节{section_name}已经存在!')
            return False

    def append_values(self, value_dict: dict, section_name=None) -> bool:
        """
        新增数据

        :param value_dict:要添加的数据,数据格式{值名:值}
        :param section_name:将数据添加在哪个节下面
        """
        if section_name is None:
            section_name = self.SECTION_NAME
        config = self.config_init()
        if not config.has_section(section_name):
            config.add_section(section_name)  # 添加节
        for value_name, value in value_dict.items():  # items()返回字典的键 值
            # 不管值存不存在,尝试删除,删除成功时会返回True
            value_name = str(value_name)  # 避免int键在ini文件中为str类型的错误
            config.remove_option(section_name, value_name)  # 删除键值对
            config.set(section_name, value_name, value)  # 设置键值对
        self.save(config)
        return True

    def del_section(self, section_name=None) -> bool:
        """
        删除节

        :param section_name:要删除的节的名称
        """
        if section_name is None:
            section_name = self.SECTION_NAME
        config = self.config_init()
        if config.has_section(section_name):
            config.remove_section(section_name)  # 删除节
            self.save(config)
            return True
        else:
            print(f'没有该节:{section_name}')
            return False

    def del_values(self, value_name: list, section_name=None) -> bool:
        """
        删除数据

        :param section_name:要删除的数据在哪个节下面
        :param value_name:要删除的数据列表名称
        """
        if section_name is None:
            section_name = self.SECTION_NAME
        config = self.config_init()
        error_values = []
        if config.has_section(section_name):
            # 尝试遍历value_name依次删除值
            for value in value_name:
                try:
                    config.remove_option(section_name, value)  # 删除值
                except ValueError:
                    print(f'节{section_name}没找到该值:{value}')
                    error_values.append(value)
            self.save(config)
            return True
        else:
            print(f'没有该节:{section_name}')
            return False

    def get_sections(self) -> list[str]:
        """
        获取ini文件的全部节
        返回所有节列表,没有内容时返回[]
        """
        config = self.config_init()
        sections = config.sections()
        return sections

    def get_values(self, value_name: str = None, section_name: str = None) -> str | dict:
        """
        获取指定变量名的数据内容,不指定时默认返回全部
        返回数据内容,指定变量名时返回str类型,否则返回dict
        """
        if section_name is None:
            section_name = self.SECTION_NAME
        config = self.config_init()
        if config.has_section(section_name):
            try:
                if value_name is None:
                    # 获取全部数据,数据格式是[(值名,值)]
                    values = config.items(section_name)
                    # 转为字典类型
                    value_dict = {value_name: value for value_name, value in values}
                    return value_dict
                else:
                    value = config.get(section_name, value_name)  # 获取值
                    return value
            except:
                print(f'节{section_name}没有该值:{value_name}')
                return ''
        else:
            print(f'没有该节:{section_name}')
            return ''

    def save(self, config):
        file.ensure_exist(os.path.dirname(self.INI_FILE))
        with open(self.INI_FILE, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        configfile.close()

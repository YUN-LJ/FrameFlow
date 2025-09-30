class INI:
    """
    用于ini文件处理

    SetPath是必须要运行的函数
    SetSection可选运行
    不运行时section_name参数需要传递
    """

    def __init__(self, config_path, section_name=None):
        """
        :param config_path:ini文件地址
        :param section_name:要操作的节
        """
        self.__config_path = config_path
        self.__section_name = section_name

    def __ConfigInstance(self) -> configparser.RawConfigParser:
        """
        实例化configparser.RawConfigParser()类
        """
        config = configparser.RawConfigParser()  # 需要实例化一个ConfigParser对象
        config.optionxform = lambda option: option  # 防止保存文件时键值小写
        config.read(self.__config_path, encoding='utf-8')
        return config

    def Create(self) -> bool:
        """
        创建一个新的ini文件
        """
        config = self.__ConfigInstance()
        self.Save(config)
        return True

    def AppendSection(self, section_name=None) -> bool:
        """
        新增节

        :param section_name:要添加的节的名称
        """
        if section_name == None:
            section_name = self.__section_name
        config = self.__ConfigInstance()
        # 检查要添加的节是否存在
        if config.has_section(section_name) == False:
            config.add_section(section_name)  # 添加节
            self.Save(config)
            return True
        else:
            return False

    def AppendValues(self, value_dict: dict, section_name=None) -> bool:
        """
        新增数据

        :param value_dict:要添加的数据,数据格式{值名:值}
        :param section_name:将数据添加在哪个节下面
        """
        if section_name == None:
            section_name = self.__section_name
        config = self.__ConfigInstance()
        if config.has_section(section_name) == False:
            config.add_section(section_name)  # 添加节
        for value_name, value in value_dict.items():  # items()返回字典的键 值
            # 不管值存不存在,尝试删除,删除成功时会返回True
            value_name = str(value_name)  # 避免int键在ini文件中为str类型的错误
            config.remove_option(section_name, value_name)  # 删除键值对
            config.set(section_name, value_name, value)  # 设置键值对
        self.Save(config)
        return True

    def DelSection(self, section_name=None) -> bool:
        """
        删除节

        :param section_name:要添加的节的名称
        """
        if section_name == None:
            section_name = self.__section_name
        config = self.__ConfigInstance()
        if config.has_section(section_name) == True:
            config.remove_section(section_name)  # 删除节
            self.Save(config)
            return True
        else:
            print(f'DelSection没找到该节:{section_name}')
            return False

    def DelValues(self, value_name: list, section_name=None) -> bool:
        """
        删除数据

        :param section_name:要删除的数据在哪个节下面
        :param value_name:要删除的数据列表名称
        """
        if section_name == None:
            section_name = self.__section_name
        config = self.__ConfigInstance()
        erro_values = []
        if config.has_section(section_name) == True:
            # 尝试遍历value_name依次删除值
            for value in value_name:
                try:
                    config.remove_option(section_name, value)  # 删除值
                except ValueError:
                    print(f'DelINIValue没找到该值:{value}')
                    erro_values.append(value)
            self.Save(config)
            return True
        else:
            print(f'DelINIValue没找到该节:{section_name}')
            return False

    def GetAllSections(self) -> list[str]:
        """
        获取ini文件的全部节
        返回所有节列表,没有内容时返回[]
        """
        config = self.__ConfigInstance()
        sections = config.sections()
        return sections

    def GetValue(self, value_name, section_name=None) -> str:
        """
        获取指定变量名的数据内容
        返回数据内容,否则返回None
        """
        if section_name == None:
            section_name = self.__section_name
        config = self.__ConfigInstance()
        if config.has_section(section_name) == True:
            try:
                value = config.get(section_name, value_name)  # 获取值
                return value
            except:
                print(f'GetValue没有该值:{value_name}')
                return ''
        else:
            print(f'GetValue没有该节:{section_name}')
            return ''

    def GetValues(self, section_name=None) -> dict[str, str]:
        """
        获取指定节下的全部数据内容
        返回数据内容{值名:值},否则返回{}
        """
        if section_name == None:
            section_name = self.__section_name
        config = self.__ConfigInstance()
        value_dict = {}
        if config.has_section(section_name) == True:
            # 获取全部数据,数据格式是[(值名,值)]
            values = config.items(section_name)
            # 转为字典类型
            for value_name, value in values:
                value_dict[value_name] = value
        else:
            print(f'GetValue没有该节:{section_name}')
        return value_dict

    def Save(self,config):
        with open(self.__config_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        configfile.close()



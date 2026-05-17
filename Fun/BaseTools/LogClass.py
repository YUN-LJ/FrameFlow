"""日志管理模块"""
import os
import sys
import logging
from typing import Optional
from pathlib import Path
from Fun.BaseTools import singleton_decorator
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


class LogConfig:
    """日志配置类"""

    # 日志目录
    LOG_DIR = Path('E:/code/Python/simple/AutoWallpaper/FrameFlow/config') if Path(
        sys.argv[0]).suffix == '.py' else Path.cwd() / 'config'

    # 日志文件配置
    LOG_FILE = LOG_DIR / 'app.log'
    ERROR_LOG_FILE = LOG_DIR / 'error.log'

    # 日志格式
    CONSOLE_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    FILE_FORMAT = '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s'
    DETAILED_FORMAT = '%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s'

    # 日志级别映射
    LEVEL_MAP = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }


@singleton_decorator
class LogManager:
    """日志管理器（单例模式）"""

    def __init__(self):
        self._loggers = {}
        self._setup_log_directory()

    def _setup_log_directory(self):
        """创建日志目录"""
        LogConfig.LOG_DIR.mkdir(parents=True, exist_ok=True)

    def get_logger(
            self,
            name: str = None,
            level: str = 'INFO',
            console_output: bool = True,
            console_level: str = 'INFO',
            file_output: bool = True,
            error_file_output: bool = True,
            max_bytes: int = 10 * 1024 * 1024,  # 10MB
            backup_count: int = 5,
            use_detailed_format: bool = True
    ) -> logging.Logger:
        """
        获取或创建logger实例

        :param name: logger名称，默认为调用者模块名
        :param level: 日志级别 ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        :param console_output: 是否输出到控制台
        :param console_level: 控制台日志级别，默认INFO
        :param file_output: 是否输出到文件
        :param error_file_output: 是否将ERROR及以上级别单独输出到error.log
        :param max_bytes: 单个日志文件最大大小（字节）
        :param backup_count: 保留的备份文件数量
        :param use_detailed_format: 是否使用详细格式（包含函数名和行号）
        :return: Logger实例
        """
        # 如果未指定名称，使用调用者模块名
        if name is None:
            import inspect
            frame = inspect.currentframe().f_back
            name = frame.f_globals.get('__name__', 'unknown')

        # 如果已经创建过，直接返回
        if name in self._loggers:
            return self._loggers[name]

        # 创建logger
        logger = logging.getLogger(name)
        logger.setLevel(LogConfig.LEVEL_MAP.get(level.upper(), logging.INFO))

        # 避免重复添加handler
        if logger.handlers:
            self._loggers[name] = logger
            return logger

        # 设置格式
        format_str = LogConfig.DETAILED_FORMAT if use_detailed_format else LogConfig.FILE_FORMAT
        file_formatter = logging.Formatter(format_str)
        console_formatter = logging.Formatter(LogConfig.CONSOLE_FORMAT)

        # 控制台Handler
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(LogConfig.LEVEL_MAP.get(console_level.upper(), logging.INFO))
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

        # 文件Handler（轮转）
        if file_output:
            try:
                file_handler = RotatingFileHandler(
                    filename=LogConfig.LOG_FILE,
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding='utf-8'
                )
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                print(f"警告: 无法创建日志文件Handler: {e}")

        # 错误日志文件Handler（只记录ERROR及以上）
        if error_file_output:
            try:
                error_handler = RotatingFileHandler(
                    filename=LogConfig.ERROR_LOG_FILE,
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding='utf-8'
                )
                error_handler.setLevel(logging.ERROR)
                error_handler.setFormatter(file_formatter)
                logger.addHandler(error_handler)
            except Exception as e:
                print(f"警告: 无法创建错误日志文件Handler: {e}")

        # 阻止日志传播到根logger（避免重复输出）
        logger.propagate = False

        self._loggers[name] = logger
        return logger

    def configure_root_logger(
            self,
            level: str = 'WARNING',
            console_output: bool = True
    ):
        """
        配置根logger（捕获所有未配置的logger）

        :param level: 日志级别
        :param console_output: 是否输出到控制台
        """
        root_logger = logging.getLogger()
        root_logger.setLevel(LogConfig.LEVEL_MAP.get(level.upper(), logging.WARNING))

        # 清除默认handler
        root_logger.handlers.clear()

        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(logging.Formatter(LogConfig.CONSOLE_FORMAT))
            root_logger.addHandler(console_handler)

    def set_level(self, name: str, level: str):
        """动态修改logger的日志级别"""
        if name in self._loggers:
            self._loggers[name].setLevel(LogConfig.LEVEL_MAP.get(level.upper(), logging.INFO))

    def disable_logging(self, name: str = None):
        """禁用指定logger或所有logger"""
        if name:
            if name in self._loggers:
                self._loggers[name].setLevel(logging.CRITICAL + 1)
        else:
            for logger in self._loggers.values():
                logger.setLevel(logging.CRITICAL + 1)

    def enable_logging(self, name: str = None, level: str = 'INFO'):
        """启用指定logger或所有logger"""
        if name:
            if name in self._loggers:
                self._loggers[name].setLevel(LogConfig.LEVEL_MAP.get(level.upper(), logging.INFO))
        else:
            for logger in self._loggers.values():
                logger.setLevel(LogConfig.LEVEL_MAP.get(level.upper(), logging.INFO))

    def close_all_handlers(self):
        """关闭所有handler（程序退出时调用）"""
        for logger in self._loggers.values():
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)
        self._loggers.clear()


def get_logger(
        name: str = None,
        level: str = 'INFO',
        **kwargs
) -> logging.Logger:
    """
    便捷函数：获取logger实例

    :param name: logger名称
    :param level: 日志级别
    :param kwargs: 其他参数传递给 LogManager.get_logger
    :return: Logger实例
    """
    return LogManager().get_logger(name=name, level=level, **kwargs)

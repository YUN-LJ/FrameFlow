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


def _safe_rotate(source, dest):
    """
    安全的文件轮转函数，处理Windows文件锁定问题
    """
    import time
    import shutil
    
    try:
        # 如果目标文件已存在，先删除
        if os.path.exists(dest):
            try:
                os.remove(dest)
            except PermissionError:
                # 如果删除失败，等待后重试
                time.sleep(0.1)
                try:
                    os.remove(dest)
                except Exception:
                    pass
        
        # 尝试重命名
        os.rename(source, dest)
    except PermissionError:
        # Windows下文件被锁定时，使用复制+清空的方式
        try:
            shutil.copy2(source, dest)
            # 清空原文件而不是删除
            with open(source, 'w', encoding='utf-8') as f:
                f.truncate(0)
        except Exception:
            # 如果所有方法都失败，静默忽略
            pass
    except Exception:
        pass


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
                    encoding='utf-8',
                    delay=True
                )
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(file_formatter)
                file_handler.namer = lambda name: name + '.log'
                file_handler.rotator = lambda source, dest: _safe_rotate(source, dest)
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
                    encoding='utf-8',
                    delay=True
                )
                error_handler.setLevel(logging.ERROR)
                error_handler.setFormatter(file_formatter)
                error_handler.namer = lambda name: name + '.log'
                error_handler.rotator = lambda source, dest: _safe_rotate(source, dest)
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

    def set_level(self, name: str = None, level: str = 'INFO'):
        """
        动态修改logger的日志级别
        
        :param name: logger名称，不指定则操作全部logger
        :param level: 日志级别，默认为'INFO'
        """
        loggers_to_process = [self._loggers[name]] if name and name in self._loggers else self._loggers.values()

        for logger in loggers_to_process:
            logger.setLevel(LogConfig.LEVEL_MAP.get(level.upper(), logging.INFO))

    def set_console_output(self, name: str = None, enable: bool = True, console_level: str = None):
        """
        动态启用或禁用logger的控制台输出
        
        :param name: logger名称，不指定则操作全部logger
        :param enable: 是否启用控制台输出，默认为True
        :param console_level: 控制台日志级别，仅在启用时有效，不指定则保持原有级别
        """
        loggers_to_process = [self._loggers[name]] if name and name in self._loggers else self._loggers.values()

        for logger in loggers_to_process:
            if enable:
                # 检查是否已存在控制台handler
                has_console_handler = any(
                    isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
                    for h in logger.handlers)

                if not has_console_handler:
                    # 添加控制台handler
                    console_handler = logging.StreamHandler(sys.stdout)
                    level = LogConfig.LEVEL_MAP.get(console_level.upper(),
                                                    logging.INFO) if console_level else logging.INFO
                    console_handler.setLevel(level)
                    console_formatter = logging.Formatter(LogConfig.CONSOLE_FORMAT)
                    console_handler.setFormatter(console_formatter)
                    logger.addHandler(console_handler)
                elif console_level:
                    # 如果已存在控制台handler且指定了级别，则更新级别
                    for handler in logger.handlers:
                        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                            handler.setLevel(LogConfig.LEVEL_MAP.get(console_level.upper(), logging.INFO))
                            break
            else:
                # 移除所有控制台handler
                logger.handlers = [h for h in logger.handlers
                                   if not (
                                isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler))]

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

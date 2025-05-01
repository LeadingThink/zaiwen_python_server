from datetime import datetime, time
from enum import Enum
import json
from logging.handlers import TimedRotatingFileHandler
from pydantic import BaseModel
import logging
from pathlib import Path

from .utils import split_numeric_alpha


class XlogMode(Enum):
    CONSOLE = "CONSOLE"
    FILE = "FILE"
    HTTP = "HTTP"


class XlogLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR


class XlogOptions(BaseModel):
    appid: str = None
    mode: XlogMode = XlogMode.CONSOLE
    level: XlogLevel = XlogLevel.INFO
    app: str = "zaiwen-python-server"
    path: str = "logs"
    retention: int = 7
    interval: str = "1D"


# 去掉所有扩展名的例子
def remove_all_extensions(file_name):
    return Path(file_name).with_suffix("").name


class XlogRotatingFileHandler(TimedRotatingFileHandler):
    def get_rotation_filename(self, default_name):
        if self.when == "S":
            suffix = "%Y%m%d%H%M%S"
        elif self.when == "M":
            suffix = "%Y%m%d%H%M"
        elif self.when == "H":
            suffix = "%Y%m%d%H"
        elif self.when == "D":
            suffix = "%Y%m%d"

        # 获取当前日期
        current_date = datetime.now().strftime(suffix)
        # 获取文件的基础名，不包含路径和后缀
        base_name = Path(default_name).stem  # 例如 "xlog"
        base_name = remove_all_extensions(base_name)  # 去掉所有扩展名
        # 构建新的文件名 xlog_YYYY-MM-DD.log
        new_filename = f"{base_name}_{current_date}.log"

        # 获取原始日志文件的目录
        dir_name = Path(default_name).parent

        # 返回新的完整路径
        return str(Path(dir_name) / new_filename)


def getBackupCount(when, interval, retention):
    """
    根据时间单位和间隔计算保留的日志文件数量。

    参数:
    when : str : 时间单位 ('S' - 秒, 'M' - 分钟, 'H' - 小时, 'D' - 天)
    interval : int : 间隔值
    retention : int : 希望保留的时间量

    返回:
    int : 计算出的备份数量
    """
    if when == "S":
        return int(retention * (24 * 60 * 60 / interval))
    elif when == "M":
        return int(retention * (24 * 60 / interval))
    elif when == "H":
        return int(retention * (24 / interval))
    elif when == "D":
        return int(retention * (1 / interval))
    else:
        return 1  # 默认情况下返回 1


class ZaiwenaiXlog:
    def __init__(self, options: XlogOptions = XlogOptions()):
        self.options = options
        self.logger = self.build()

    def build(self):
        # 获取日志记录器实例
        logger = logging.getLogger("xlog")
        logger.setLevel(self.options.level.value)

        if self.options.mode == XlogMode.FILE:
            # 初始化日志目录
            Path(self.options.path).mkdir(
                parents=True, exist_ok=True
            )  # 使用 Path 对象创建目录
            interval, when = split_numeric_alpha(
                self.options.interval
            )  # 检查时间间隔格式
            # 创建轮转函数
            handler = XlogRotatingFileHandler(
                filename=f"{self.options.path}/{self.options.app}.log",  # TimedRotatingFileHandler 需要字符串路径
                when=when.upper(),
                interval=interval,  # 轮转周期
                backupCount=getBackupCount(when, interval, self.options.retention),
                encoding="utf-8",
                delay=False,  # 如果日志文件在创建时不存在，立即创建它
                utc=False,  # 使用本地时间进行轮换计算和命名
                # suffix="%Y%m%d%H", # 指定处理器附加的时间戳格式，与 namer 函数期望的格式一致
                # 注意：此后缀不包含 .log 扩展名
            )

            formatter = logging.Formatter("%(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        elif self.options.mode == XlogMode.CONSOLE:
            # 创建控制台处理器
            ch = logging.StreamHandler()
            ch.setLevel(self.options.level.value)  # 为处理器设置级别

            # 创建格式化器并设置给处理器
            formatter = logging.Formatter("%(message)s")
            ch.setFormatter(formatter)

            # 将处理器添加到 logger
            logger.addHandler(ch)

        return logger

    def getLogger(self):
        return self.logger

    def getOptions(self):
        return self.options

    def formatMsg(self, type, msg):
        nowTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(msg, str):
            return json.dumps(
                {
                    "datetime": nowTime,
                    "type": type,
                    "appid": self.options.appid,
                    "msg": msg,
                },
                ensure_ascii=False,
            )
        elif isinstance(msg, dict):
            return json.dumps(
                {"datetime": nowTime, "type": type, "appid": self.options.appid, **msg},
                ensure_ascii=False,
            )
        else:
            return ""

    def debug(self, msg):
        self.logger.debug(self.formatMsg("DEBUBG", msg))

    def info(self, msg):
        self.logger.info(self.formatMsg("INFO", msg))

    def warning(self, msg):
        self.logger.warning(self.formatMsg("WARNING", msg))

    def error(self, msg):
        self.logger.error(self.formatMsg("ERROR", msg))

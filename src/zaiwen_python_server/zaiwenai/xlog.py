from enum import Enum
from pydantic import BaseModel


class XlogMode(Enum):
    CONSOLE = 1
    FILE = 2
    HTTP = 3


class XlogLevel(Enum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5


class XlogOptions(BaseModel):
    mode: XlogMode = XlogMode.CONSOLE
    level: XlogLevel = XlogLevel.INFO


def buildXlog(options: XlogOptions):
    return


xlog = buildXlog()

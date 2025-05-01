import sys
from dotenv import load_dotenv

from .utils import getEnv, hasArgsKey

args = sys.argv[1:]


class ZaiwenaiConfig:
    def __init__(self):
        # 初始化配置文件
        load_dotenv()  # 加载默认配置项目

        dotenv_path = ""
        if hasArgsKey(args, "-production"):
            dotenv_path = ".env.production"
        elif hasArgsKey(args, "-development"):
            dotenv_path = ".env.development"
        elif hasArgsKey(args, "-test"):
            dotenv_path = ".env.test"
        else:
            dotenv_path = None

        if dotenv_path is not None:
            load_dotenv(dotenv_path=dotenv_path, verbose=True, override=True)

    def get(self, key, default=None):
        # 获取环境变量
        return getEnv(key, default)

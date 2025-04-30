import os
import sys

args = sys.argv[1:]


# 判断启动参数是否有对应的值
def hasArgsKey(key):
    try:
        args.index(key)
        return True
    except ValueError:
        return False


# 获取环境变量
def getEnv(key, default=None):
    return os.environ.get(key, default)

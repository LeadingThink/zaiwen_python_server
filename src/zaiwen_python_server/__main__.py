import zaiwen_python_server
import sys
from dotenv import load_dotenv

from zaiwen_python_server.utils import hasArgsKey

# 初始化配置文件
load_dotenv()  # 加载默认配置项目

dotenv_path = ""
if hasArgsKey("-production"):
    dotenv_path = ".env.production"
elif hasArgsKey("-development"):
    dotenv_path = ".env.development"
else:
    dotenv_path = None

if dotenv_path is not None:
    load_dotenv(dotenv_path=dotenv_path, verbose=True, override=True)

# 启动主包的main
if __name__ == "__main__":
    sys.exit(zaiwen_python_server.main())

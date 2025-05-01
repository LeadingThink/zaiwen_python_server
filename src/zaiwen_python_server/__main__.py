import asyncio
import zaiwen_python_server
import sys

# 启动主包的main
if __name__ == "__main__":
    sys.exit(asyncio.run(zaiwen_python_server.main()))

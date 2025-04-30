from typing import Any, Mapping, Optional
from fastapi.responses import JSONResponse
from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
import uvicorn

from zaiwen_python_server.zaiwenai.utils import killAppByPort

# uvicorn入口
main = FastAPI()


# 应用配置信息类
class ZaiwenaiConfig(BaseModel):
    app: str | None = None
    host: str | None = None
    port: int | None = None
    reload: bool | None = None
    workers: int | None = None

    def __init__(
        self,
        app: str = "zaiwen_python_server",
        host: str = "0.0.0.0",
        port: int = 8000,
        reload: bool = False,
        workers: int = 1,
    ):
        super().__init__(
            app=f"{app}.zaiwenai:main",
            host=host,
            port=port,
            reload=reload,
            workers=workers,
        )


class ResponseInfo:
    def __init__(self, code: int, msg: str, data: Any):
        self.code = code
        self.msg = msg
        self.data = data

    def model_dump(self):
        return {
            "code": self.code,
            "msg": self.msg,
            "data": self.data,
        }


class JsonResp(JSONResponse):
    def __init__(
        self,
        code: int = 0,
        msg: str = "",
        data: Any = None,
        status: int = 200,
        headers: Mapping[str, str] | None = None,
    ):
        content = ResponseInfo(code=code, msg=msg, data=data).model_dump()
        super().__init__(  # 正确调用父类构造函数
            content=content,
            headers=headers,
            status_code=status,  # status_code 设置响应状态码
        )


# 应用实体类
class ZaiwenaiApplication:
    app: FastAPI | None = None  # 直接创建 FastAPI 实例作为默认值
    prefix: str = ""  # 全局路由前缀
    options: Optional[ZaiwenaiConfig] = None

    # 初始化
    def __init__(self, prefix: str = "", options: ZaiwenaiConfig = ZaiwenaiConfig()):
        """
        初始化 ZaiwenaiApplication
        """
        self.options = options
        self.app = (
            main  # 因为需要配置Reload和Worker所以不能使用对象类型app入参给Uvicorn
        )
        self.prefix = prefix

    # 配置路由
    def route(self, routers: APIRouter = None):
        if routers is not None:
            self.app.include_router(routers, prefix=self.prefix)

    # 设置中间件
    def addMiddleware(self, middleware: Any = None):
        if middleware is not None:
            self.app.add_middleware(middleware)

    # 启动Application
    def run(self):
        killAppByPort(self.options.port)
        uvicorn.run(**self.options.model_dump())

    # 获取FastAPI原始对象，如果需要使用的话
    def getApp(self):
        return self.app

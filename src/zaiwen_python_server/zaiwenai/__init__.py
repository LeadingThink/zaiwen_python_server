from datetime import datetime
import inspect
from logging import shutdown
import logging
import signal
from typing import Any, Mapping
from fastapi.responses import JSONResponse
from fastapi import APIRouter, FastAPI, Request
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware

import uvicorn

from .xlog import XlogOptions, ZaiwenaiXlog
from .config import ZaiwenaiConfig
from .utils import killAppByPort


class ZaiwenaiException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


# 应用配置信息类
class Options(BaseModel):
    app: str | None = None
    host: str | None = None
    port: int | None = None
    reload: bool | None = None
    workers: int | None = None

    def __init__(
        self,
    ):
        super().__init__(
            app=f"{config.get('APP_NAME')}.zaiwenai:main",
            host=config.get("HOST"),
            port=config.get("PORT"),
            reload=config.get("RELOAD"),
            workers=int(config.get("WORKERS")),
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


# uvicorn入口
main = FastAPI()


# 暴露配置和日志对象
config = ZaiwenaiConfig()
xlog = ZaiwenaiXlog(
    XlogOptions(
        appid=config.get("APPID") or "",
        app=config.get("XLOG_NAME") or config.get("APPNAME"),
        mode=config.get("XLOG_MODE"),
        level=logging.getLevelName(config.get("XLOG_LEVEL")),
        path=config.get("XLOG_PATH"),
        retention=int(config.get("XLOG_RETENTION")),
        interval=config.get("XLOG_INTERVAL"),
    )
)


@main.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    status_code = getattr(exc, "status_code", 500)
    xlog.error(str(exc))
    return JsonResp(
        status=status_code,
        code=status_code,
        msg=str(exc),
        data=None,
    )


class DefaultMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = datetime.now()  # 记录开始时间
        xlog.info({"method": request.method, "url": str(request.url.path)})
        response = await call_next(request)
        duration_milliseconds = (datetime.now() - start_time).total_seconds() * 1000
        xlog.info(
            {
                "method": request.method,
                "url": str(request.url.path),
                "status": response.status_code,
                "dura": duration_milliseconds,
            }
        )
        if response.status_code == 404:
            # 404错误处理
            xlog.error(f"404 Not Found: {request.method} {request.url.path}")
            return JsonResp(
                status=404,
                code=404,
                msg="Not Found",
                data=None,
            )
        # 返回响应
        return response


main.add_middleware(DefaultMiddleware)


# 应用实体类
class Application:
    app: FastAPI | None = None  # 直接创建 FastAPI 实例作为默认值
    prefix: str = ""  # 全局路由前缀
    options: Options | None = None
    bootstrap: Any = None  # 启动函数

    # 初始化
    def __init__(self, prefix: str = "", options: Options = Options()):
        """
        初始化 ZaiwenaiApplication
        """
        self.options = options
        self.app = (
            main  # 因为需要配置Reload和Worker所以不能使用对象类型app入参给Uvicorn
        )
        self.prefix = prefix

    def setup(self, func: Any = None):
        if func is not None:
            self.bootstrap = func

    def addErrorHandler(self, exc: Exception, func: Any = None):
        if func is not None:
            self.app.add_exception_handler(exc, func)

    # 配置路由
    def route(self, routers: APIRouter = None):
        if routers is not None:
            self.app.include_router(routers, prefix=self.prefix)

    # 设置中间件
    def addMiddleware(self, middleware: Any = None):
        if middleware is not None:
            self.app.add_middleware(middleware)

    # 启动Application
    async def run(self):
        if (
            self.options.app is None
            or self.options.app == ""
            or self.options.app.startswith(".")
        ):
            raise ZaiwenaiException(
                "缺少options.app参数，请设置与pyproject.toml一致的app名称。"
            )
        killAppByPort(self.options.port)
        signal.signal(signal.SIGINT, lambda s, f: shutdown())
        xlog.info("应用服务器启动中。。。。。。")
        xlog.info(f"启动参数：{self.options.model_dump()}")
        if self.bootstrap is not None:
            if inspect.iscoroutinefunction(self.bootstrap):
                await self.bootstrap()
            else:
                self.bootstrap()

        uvicorn.run(**self.options.model_dump(), access_log=False)

    # 获取FastAPI原始对象，如果需要使用的话
    def getApp(self):
        return self.app

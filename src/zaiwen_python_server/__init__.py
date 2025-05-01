from fastapi import APIRouter, Request
from starlette.middleware.base import BaseHTTPMiddleware

from .zaiwenai import JsonResp, Application

# 初始化服务端框架
app = Application(
    prefix="/api/v1",
)

router = APIRouter()


@router.get("/")
async def aaa():
    return JsonResp(
        code=0,
        msg="",
        data={
            "name": "zaiwen-python-server",
        },
    )


app.route(router)


async def setup():
    print("setup")


app.setup(setup)


async def main():
    await app.run()
    print("")

from fastapi import APIRouter
from zaiwen_python_server.zaiwenai import JsonResp, ZaiwenaiApplication, ZaiwenaiConfig

# 初始化服务端框架
app = ZaiwenaiApplication(
    prefix="/api/v1", options=ZaiwenaiConfig(reload=True, port=8001)
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


def main():
    app.run()
    print("")

import os
import signal
import subprocess


# 清理之前如果可能存在的垃圾进程，防止因为端口被占用而启动失败。
def killAppByPort(port=None):
    if port is None:
        return

    try:
        output = (
            subprocess.check_output(["lsof", "-t", "-i", f"tcp:{port}"])
            .decode()
            .strip()
        )
        pids = [int(pid) for pid in output.split()]
    except subprocess.CalledProcessError:
        return

    if not pids:
        return

    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)  # 发送 SIGTERM
        except ProcessLookupError:
            continue
        except PermissionError:
            continue

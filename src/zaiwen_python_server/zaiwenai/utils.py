import inspect
import os
import signal
import subprocess


# 清理之前如果可能存在的垃圾进程，防止因为端口被占用而启动失败。
def killAppByPort(port=None):
    print(__package__)
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


def hasArgsKey(args, key):
    try:
        args.index(key)
        return True
    except ValueError:
        return False


def getEnv(key, default=None):
    return os.environ.get(key, default)


def split_numeric_alpha(input_str):
    # 检查输入字符串是否非空，并且最后一个字符是字母
    if not input_str or not input_str[-1].isalpha():
        raise ValueError(f"{get_caller_info()} - 输入参数不正确.")

    # 初始化结果数组
    result = [None, None]

    # 查找数字部分和字母部分的分隔点
    for index, char in enumerate(input_str):
        if char.isdigit():
            continue
        else:
            # 将数字部分和字母部分拆分
            result[0] = int(input_str[:index])  # 转换为数字
            result[1] = input_str[index:]  # 字母部分
            break

    # 确保第一个元素是数字，第二个元素是字母
    if isinstance(result[0], int) and result[1].isalpha() and len(result[1]) == 1:
        return result
    else:
        raise ValueError(f"{get_caller_info()} - 输入参数不正确.")


def get_caller_info():
    # 通过 inspect.stack() 获取调用栈
    stack = inspect.stack()

    # stack[1] 是当前函数的调用者
    caller_frame = stack[1]

    # 获取调用者的函数名
    caller_function_name = caller_frame.function
    # 获取调用者的文件名
    # caller_file_name = caller_frame.filename
    # 获取关联的包名（文件的 __package__ 属性）
    # 反射调用的代码所属模块时，使用其__module__，但需要导入该模块以获取其包信息
    module = inspect.getmodule(caller_frame[0])
    caller_package_name = module.__package__ if module else None

    return f"[{caller_package_name}][{caller_function_name}]"

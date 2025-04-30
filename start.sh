#!/bin/bash

# 检查是否提供了参数
if [ $# -eq 0 ]; then
  # 没有参数，运行 production 脚本
  echo "启动 production 模式..."
  ./scripts/start_production.sh
elif [ "$1" == "-dev" ]; then
  # 参数是 -dev，运行 development 脚本
  echo "启动 development 模式..."
  ./scripts/start_development.sh
else
  # 其他参数，显示用法
  echo "用法: ./start.sh [-dev: 开发模式]   默认生产模式"
  echo "用法: ./start.sh [-dev: 开发模式]"
  exit 1
fi

exit 0
#!/bin/bash
# RM-01 N305 SSD自动刷写软件启动脚本
# RM-01 N305 SSD Auto Flash Tool Launcher Script

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/flash_rm01_n305.py"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到python3，请先安装Python 3"
    echo "Error: python3 not found, please install Python 3 first"
    exit 1
fi

# 检查脚本文件是否存在
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "错误: 找不到刷写脚本: $PYTHON_SCRIPT"
    echo "Error: Flash script not found: $PYTHON_SCRIPT"
    exit 1
fi

# 检查是否有sudo权限
if [ "$EUID" -ne 0 ]; then
    echo "提示: 此脚本需要root权限，将使用sudo运行"
    echo "Note: This script requires root privileges, will run with sudo"
    echo ""
    # 使用sudo运行Python脚本，并传递所有参数
    sudo python3 "$PYTHON_SCRIPT" "$@"
else
    # 已经有root权限，直接运行
    python3 "$PYTHON_SCRIPT" "$@"
fi


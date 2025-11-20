#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RM-01 N305 SSD自动刷写软件
RM-01 N305 SSD Auto Flash Tool
"""

import subprocess
import sys
import os
import argparse
import time
import re
from pathlib import Path


class Colors:
    """终端颜色"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_info(msg):
    """打印信息"""
    print(f"{Colors.OKCYAN}[INFO]{Colors.ENDC} {msg}")


def print_success(msg):
    """打印成功信息"""
    print(f"{Colors.OKGREEN}[SUCCESS]{Colors.ENDC} {msg}")


def print_warning(msg):
    """打印警告信息"""
    print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} {msg}")


def print_error(msg):
    """打印错误信息"""
    print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} {msg}")


def print_logo():
    """打印RMinte LOGO"""
    logo = f"""
{Colors.HEADER}{Colors.BOLD}
██████╗ ███╗   ███╗██╗███╗   ██╗████████╗███████╗
██╔══██╗████╗ ████║██║████╗  ██║╚══██╔══╝██╔════╝
██████╔╝██╔████╔██║██║██╔██╗ ██║   ██║   █████╗  
██╔══██╗██║╚██╔╝██║██║██║╚██╗██║   ██║   ██╔══╝  
██║  ██║██║ ╚═╝ ██║██║██║ ╚████║   ██║   ███████╗
╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝
{Colors.ENDC}
"""
    print(logo)


def print_copyright():
    """打印版权信息"""
    copyright_text = f"""
{Colors.OKCYAN}{'=' * 60}
Copyright RMinte 泛灵人工智能
{'=' * 60}{Colors.ENDC}
"""
    print(copyright_text)


def run_command(cmd, check=True, shell=False, input_text=None, real_time=False):
    """执行命令"""
    print_info(f"执行命令: {cmd}")
    try:
        if real_time:
            # 实时显示输出（用于显示进度条等）
            result = subprocess.run(
                cmd,
                shell=shell,
                check=check,
                text=True
            )
            return result
        elif input_text:
            result = subprocess.run(
                cmd,
                shell=shell,
                check=check,
                input=input_text,
                text=True,
                capture_output=True
            )
        else:
            result = subprocess.run(
                cmd,
                shell=shell,
                check=check,
                capture_output=True,
                text=True
            )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"命令执行失败: {e}")
        if e.stderr:
            print_error(e.stderr)
        raise


def get_user_home():
    """获取原始用户的主目录（即使在sudo环境下）"""
    # 优先使用SUDO_USER环境变量（sudo运行时）
    sudo_user = os.environ.get('SUDO_USER')
    if sudo_user:
        # 获取sudo用户的主目录
        import pwd
        try:
            return pwd.getpwnam(sudo_user).pw_dir
        except KeyError:
            pass
    
    # 使用HOME环境变量（如果存在且不是/root）
    home = os.environ.get('HOME')
    if home and home != '/root':
        return home
    
    # 最后使用当前用户的主目录
    return os.path.expanduser('~')


def check_sudo():
    """检查是否有sudo权限"""
    if os.geteuid() != 0:
        print_error("此脚本需要root权限，请使用sudo运行")
        print_error("This script requires root privileges, please run with sudo")
        sys.exit(1)


def get_disk_name():
    """获取磁盘名称"""
    print_info("检查可用磁盘...")
    print_info("Checking available disks...")
    
    result = run_command(["lsblk"], check=False)
    print(result.stdout)
    
    disk_name = input("\n请输入要刷写的磁盘名称 (例如: sda): ").strip()
    if not disk_name:
        print_error("磁盘名称不能为空")
        sys.exit(1)
    
    return disk_name


def unmount_disk(disk):
    """卸载磁盘"""
    print_info(f"卸载磁盘 /dev/{disk}...")
    print_info(f"Unmounting disk /dev/{disk}...")
    
    # 尝试卸载所有挂载点
    result = run_command(["lsblk", "-n", "-o", "MOUNTPOINT", f"/dev/{disk}"], check=False)
    mount_points = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
    
    for mount_point in mount_points:
        if mount_point:
            print_info(f"卸载挂载点: {mount_point}")
            run_command(["umount", mount_point], check=False)
    
    # 尝试直接卸载设备
    run_command(["umount", f"/dev/{disk}"], check=False)
    print_success("磁盘卸载完成")


def wipe_disk(disk):
    """清除分区表和数据"""
    print_info(f"清除磁盘 /dev/{disk} 的分区表和数据...")
    print_info(f"Wiping partition table and data from /dev/{disk}...")
    
    confirm = input(f"\n警告: 这将清除 /dev/{disk} 上的所有数据！确认继续? (yes/no): ")
    if confirm.lower() != 'yes':
        print_warning("操作已取消")
        sys.exit(0)
    
    run_command(["wipefs", "-a", f"/dev/{disk}"])
    print_success("磁盘清除完成")


def flash_image(disk, image_path):
    """刷写镜像"""
    # 如果路径包含~，先展开它
    if image_path.startswith('~'):
        user_home = get_user_home()
        image_path = image_path.replace('~', user_home, 1)
    
    if not os.path.exists(image_path):
        print_error(f"镜像文件不存在: {image_path}")
        # 提示可能的路径
        user_home = get_user_home()
        suggested_path = os.path.join(user_home, 'n305rm01.img')
        print_info(f"提示: 请检查镜像文件路径，或使用 -i 参数指定完整路径")
        print_info(f"例如: -i {suggested_path}")
        sys.exit(1)
    
    print_info(f"开始刷写镜像到 /dev/{disk}...")
    print_info(f"Starting to flash image to /dev/{disk}...")
    print_warning("此过程可能需要较长时间，请耐心等待...")
    print_warning("This process may take a while, please be patient...")
    
    # 使用dd命令刷写，使用shell=True以确保参数格式正确，real_time=True以实时显示进度条
    cmd = f"dd if={image_path} of=/dev/{disk} bs=4M status=progress"
    run_command(cmd, real_time=True, shell=True)
    
    print_success("镜像刷写完成")


def sync_disk():
    """同步磁盘"""
    print_info("同步磁盘数据...")
    print_info("Syncing disk data...")
    run_command(["sync"])
    print_success("同步完成")


def check_partitions(disk):
    """检查分区"""
    print_info(f"检查磁盘 /dev/{disk} 的分区...")
    print_info(f"Checking partitions on /dev/{disk}...")
    result = run_command(["lsblk", f"/dev/{disk}"])
    return result.stdout


def resize_partition(disk):
    """扩展根分区"""
    print_info("扩展根分区...")
    print_info("Resizing root partition...")
    
    # 首先检查分区表（使用--script避免交互式提示）
    print_info("检查当前分区表...")
    check_cmd = ["parted", "--script", f"/dev/{disk}", "print"]
    run_command(check_cmd, real_time=True)
    
    # 扩展GPT分区表以使用所有可用空间（必须先扩展GPT，才能扩展分区）
    print_info("扩展GPT分区表以使用所有可用空间...")
    print_info("Expanding GPT partition table to use all available space...")
    
    # 尝试使用sgdisk扩展GPT（如果可用）
    sgdisk_available = False
    gpt_expanded = False
    try:
        # 检查sgdisk是否可用
        subprocess.run(["which", "sgdisk"], check=True, capture_output=True)
        sgdisk_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    if sgdisk_available:
        sgdisk_cmd = ["sgdisk", "-e", f"/dev/{disk}"]
        result = run_command(sgdisk_cmd, real_time=True, check=False)
        if result.returncode == 0:
            print_success("GPT分区表已扩展")
            gpt_expanded = True
        else:
            print_warning(f"sgdisk扩展GPT返回退出码 {result.returncode}，但继续尝试扩展分区...")
    else:
        print_warning("sgdisk不可用，跳过GPT扩展步骤...")
        print_warning("如果分区扩展失败，请安装sgdisk: sudo apt-get install gdisk")
    
    # 调整分区大小（必须在GPT扩展后执行）
    print_info("调整分区2的大小到100%...")
    print_info("Resizing partition 2 to 100%...")
    _resize_partition_with_parted(disk)
    
    # 再次检查分区以确认扩展成功
    print_info("确认分区大小...")
    print_info("Verifying partition size...")
    run_command(check_cmd, real_time=True)
    
    print_success("分区扩展完成")


def _resize_partition_with_parted(disk):
    """使用parted扩展分区"""
    # 直接使用100%（根据手动操作，这是最简单有效的方法）
    print_info("使用parted将分区2扩展到100%...")
    resize_cmd = ["parted", "--script", f"/dev/{disk}", "resizepart", "2", "100%"]
    result = run_command(resize_cmd, real_time=True, check=False)
    
    if result.returncode == 0:
        print_success("分区已成功扩展到100%")
        return
    
    # 如果100%失败，显示错误并尝试使用扇区数方法
    print_error(f"使用100%扩展分区失败（退出码: {result.returncode}）")
    # 注意：real_time=True 时 stderr 不会被捕获，错误信息已实时显示
    
    print_warning("尝试使用扇区数方法...")
    print_info("获取磁盘总大小...")
    unit_cmd = ["parted", "--script", f"/dev/{disk}", "unit", "s", "print"]
    result = run_command(unit_cmd, real_time=False)
    
    # 从输出中提取磁盘总扇区数
    # 输出格式: "Disk /dev/sda: 1000215216s"
    disk_size_match = re.search(rf'Disk /dev/{disk}: (\d+)s', result.stdout)
    if disk_size_match:
        disk_size_sectors = disk_size_match.group(1)
        # 减去34个扇区（GPT备份表占用），确保安全
        # GPT备份表通常占用最后33个扇区，我们留一些余量
        end_sector = str(int(disk_size_sectors) - 34) + "s"
        print_info(f"磁盘总大小: {disk_size_sectors} 扇区")
        print_info(f"设置分区2结束位置: {end_sector} (保留34个扇区给GPT备份表)")
        
        # 调整分区大小到磁盘末尾
        resize_cmd = ["parted", "--script", f"/dev/{disk}", "unit", "s", "resizepart", "2", end_sector]
        result = run_command(resize_cmd, real_time=True, check=False)
        if result.returncode == 0:
            print_success("分区已扩展到磁盘末尾")
        else:
            print_error("分区扩展失败，请检查错误信息")
            # 注意：real_time=True 时 stderr 不会被捕获，错误信息已实时显示
            raise subprocess.CalledProcessError(result.returncode, resize_cmd)
    else:
        print_error("无法解析磁盘大小，分区扩展失败")
        raise RuntimeError("无法解析磁盘大小")


def resize_filesystem(disk):
    """调整文件系统大小"""
    partition = f"{disk}2"
    print_info(f"调整文件系统大小 /dev/{partition}...")
    print_info(f"Resizing filesystem /dev/{partition}...")
    
    # 检查文件系统（使用-y自动确认）
    print_info("检查文件系统...")
    run_command(["e2fsck", "-f", "-y", f"/dev/{partition}"], real_time=True)
    
    # 调整文件系统大小
    print_info("调整文件系统大小...")
    run_command(["resize2fs", f"/dev/{partition}"], real_time=True)
    
    print_success("文件系统调整完成")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='RM-01 N305 SSD自动刷写工具 / RM-01 N305 SSD Auto Flash Tool'
    )
    parser.add_argument(
        '-i', '--image',
        type=str,
        default=None,
        help='镜像文件路径 / Image file path (默认: ~/n305rm01.img)'
    )
    parser.add_argument(
        '-d', '--disk',
        type=str,
        default=None,
        help='磁盘名称 (例如: sda) / Disk name (e.g., sda)'
    )
    parser.add_argument(
        '--skip-confirm',
        action='store_true',
        help='跳过确认提示 / Skip confirmation prompts'
    )
    
    args = parser.parse_args()
    
    # 显示LOGO
    print_logo()
    
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=" * 60)
    print("  RM-01 N305 SSD自动刷写软件")
    print("  RM-01 N305 SSD Auto Flash Tool")
    print("=" * 60)
    print(f"{Colors.ENDC}\n")
    
    # 检查sudo权限
    check_sudo()
    
    # 处理镜像文件路径
    if args.image:
        image_path = args.image
    else:
        # 使用原始用户的主目录（即使在sudo环境下）
        user_home = get_user_home()
        image_path = os.path.join(user_home, 'n305rm01.img')
        print_info(f"使用默认镜像路径: {image_path}")
    
    # 获取磁盘名称
    if args.disk:
        disk = args.disk
    else:
        disk = get_disk_name()
    
    # 确认操作
    if not args.skip_confirm:
        print_warning(f"\n即将对 /dev/{disk} 执行以下操作:")
        print_warning(f"About to perform the following operations on /dev/{disk}:")
        print("1. 卸载磁盘 / Unmount disk")
        print("2. 清除分区表和数据 / Wipe partition table and data")
        print("3. 刷写镜像 / Flash image")
        print("4. 扩展分区 / Resize partition")
        print("5. 调整文件系统 / Resize filesystem")
        
        confirm = input("\n确认继续? (yes/no): ")
        if confirm.lower() != 'yes':
            print_warning("操作已取消")
            sys.exit(0)
    
    try:
        # 步骤1: 卸载磁盘
        unmount_disk(disk)
        
        # 步骤2: 清除分区表和数据
        wipe_disk(disk)
        
        # 步骤3: 刷写镜像
        flash_image(disk, image_path)
        
        # 步骤4: 同步
        sync_disk()
        
        # 步骤5: 检查分区
        check_partitions(disk)
        
        # 步骤6: 扩展分区
        resize_partition(disk)
        
        # 步骤7: 调整文件系统
        resize_filesystem(disk)
        
        # 步骤8: 最终检查
        print_info("\n最终检查...")
        print_info("Final check...")
        check_partitions(disk)
        
        print_success("\n" + "=" * 60)
        print_success("刷写流程完成！")
        print_success("Flash process completed!")
        print_success("=" * 60)
        
        # 显示版权信息
        print_copyright()
        
    except KeyboardInterrupt:
        print_error("\n操作被用户中断")
        print_error("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n发生错误: {e}")
        print_error(f"An error occurred: {e}")
        # 即使出错也显示版权信息
        print_copyright()
        sys.exit(1)


if __name__ == '__main__':
    main()


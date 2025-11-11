# RM-01 N305 SSD自动刷写软件 / RM-01 N305 SSD Auto Flash Tool

[English](#english) | [中文](#中文)

---

<a name="english"></a>
## English

### Description

This is an automated flashing tool for RM-01 N305 module SSD. It automates the entire process of flashing the N305RM01 image to an SSD drive, including disk unmounting, partition wiping, image flashing, partition resizing, and filesystem resizing.

### Features

- ✅ Automatic disk detection and selection
- ✅ Safe disk unmounting
- ✅ Partition table wiping
- ✅ Image flashing with progress display
- ✅ Automatic partition resizing
- ✅ Filesystem resizing
- ✅ Bilingual support (English/Chinese)

### Requirements

- Linux operating system
- Python 3.6 or higher
- Root/sudo privileges
- Required system tools:
  - `lsblk`
  - `umount`
  - `wipefs`
  - `dd`
  - `sync`
  - `parted`
  - `e2fsck`
  - `resize2fs`

### Installation

1. Clone or download this repository:
```bash
cd ~/Desktop/RM-01-N305-Maker
```

2. Make the script executable:
```bash
chmod +x flash_rm01_n305.py
```

### Usage

#### Basic Usage

Run the script with sudo privileges:

```bash
sudo python3 flash_rm01_n305.py
```

The script will:
1. Display available disks
2. Prompt you to select the target disk
3. Ask for confirmation before proceeding
4. Execute the flashing process automatically

#### Advanced Usage

Specify the image file path:

```bash
sudo python3 flash_rm01_n305.py -i /path/to/n305rm01.img
```

Specify the disk name directly:

```bash
sudo python3 flash_rm01_n305.py -d sda -i /path/to/n305rm01.img
```

Skip confirmation prompts (use with caution):

```bash
sudo python3 flash_rm01_n305.py -d sda -i /path/to/n305rm01.img --skip-confirm
```

#### Command Line Options

- `-i, --image`: Path to the image file (default: `/home/rm01/image/n305rm01.img`)
- `-d, --disk`: Disk name (e.g., `sda`) - if not specified, will prompt for selection
- `--skip-confirm`: Skip confirmation prompts (use with extreme caution)

### Workflow

The tool performs the following steps automatically:

1. **Check sudo privileges** - Ensures the script has root access
2. **Detect disk** - Lists available disks and prompts for selection
3. **Unmount disk** - Safely unmounts all mount points on the target disk
4. **Wipe disk** - Clears partition table and data using `wipefs`
5. **Flash image** - Writes the image file to the disk using `dd` with progress display
6. **Sync** - Ensures all data is written to disk
7. **Check partitions** - Verifies partition creation
8. **Resize partition** - Expands partition 2 to 100% using `parted`
9. **Resize filesystem** - Adjusts the filesystem size using `e2fsck` and `resize2fs`
10. **Final verification** - Performs final check to confirm success

### Warning

⚠️ **WARNING**: This tool will **PERMANENTLY DELETE** all data on the target disk. Make sure you have selected the correct disk before proceeding. Double-check the disk name to avoid data loss.

### Troubleshooting

#### Permission Denied
Make sure you're running the script with `sudo`:
```bash
sudo python3 flash_rm01_n305.py
```

#### Disk Not Found
Verify the disk name using `lsblk`:
```bash
lsblk
```

#### Image File Not Found
Check the image file path:
```bash
ls -lh /path/to/n305rm01.img
```

#### Parted Errors
If you encounter GPT warnings, the script will attempt to fix them automatically. If issues persist, you may need to manually run:
```bash
sudo parted /dev/sda fix
sudo parted /dev/sda resizepart 2 100%
```

### License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Support

For issues or questions, please open an issue on the project repository.

---

<a name="中文"></a>
## 中文

### 简介

这是一个用于RM-01 N305模组SSD的自动刷写工具。它自动化了整个将N305RM01镜像刷写到SSD驱动器的过程，包括磁盘卸载、分区清除、镜像刷写、分区扩展和文件系统调整。

### 功能特性

- ✅ 自动磁盘检测和选择
- ✅ 安全磁盘卸载
- ✅ 分区表清除
- ✅ 带进度显示的镜像刷写
- ✅ 自动分区扩展
- ✅ 文件系统调整
- ✅ 双语支持（中文/英文）

### 系统要求

- Linux操作系统
- Python 3.6或更高版本
- Root/sudo权限
- 必需的系统工具：
  - `lsblk`
  - `umount`
  - `wipefs`
  - `dd`
  - `sync`
  - `parted`
  - `e2fsck`
  - `resize2fs`

### 安装

1. 克隆或下载此仓库：
```bash
cd ~/Desktop/RM-01-N305-Maker
```

2. 使脚本可执行：
```bash
chmod +x flash_rm01_n305.py
```

### 使用方法

#### 基本用法

使用sudo权限运行脚本：

```bash
sudo python3 flash_rm01_n305.py
```

脚本将：
1. 显示可用磁盘
2. 提示您选择目标磁盘
3. 在执行前请求确认
4. 自动执行刷写过程

#### 高级用法

指定镜像文件路径：

```bash
sudo python3 flash_rm01_n305.py -i /path/to/n305rm01.img
```

直接指定磁盘名称：

```bash
sudo python3 flash_rm01_n305.py -d sda -i /path/to/n305rm01.img
```

跳过确认提示（请谨慎使用）：

```bash
sudo python3 flash_rm01_n305.py -d sda -i /path/to/n305rm01.img --skip-confirm
```

#### 命令行选项

- `-i, --image`: 镜像文件路径（默认：`/home/rm01/image/n305rm01.img`）
- `-d, --disk`: 磁盘名称（例如：`sda`）- 如果未指定，将提示选择
- `--skip-confirm`: 跳过确认提示（请极其谨慎使用）

### 工作流程

工具自动执行以下步骤：

1. **检查sudo权限** - 确保脚本具有root访问权限
2. **检测磁盘** - 列出可用磁盘并提示选择
3. **卸载磁盘** - 安全卸载目标磁盘上的所有挂载点
4. **清除磁盘** - 使用`wipefs`清除分区表和数据
5. **刷写镜像** - 使用`dd`将镜像文件写入磁盘，并显示进度
6. **同步** - 确保所有数据写入磁盘
7. **检查分区** - 验证分区创建
8. **扩展分区** - 使用`parted`将分区2扩展到100%
9. **调整文件系统** - 使用`e2fsck`和`resize2fs`调整文件系统大小
10. **最终验证** - 执行最终检查以确认成功

### 警告

⚠️ **警告**：此工具将**永久删除**目标磁盘上的所有数据。在执行之前，请确保您选择了正确的磁盘。请仔细检查磁盘名称以避免数据丢失。

### 故障排除

#### 权限被拒绝
确保使用`sudo`运行脚本：
```bash
sudo python3 flash_rm01_n305.py
```

#### 找不到磁盘
使用`lsblk`验证磁盘名称：
```bash
lsblk
```

#### 找不到镜像文件
检查镜像文件路径：
```bash
ls -lh /path/to/n305rm01.img
```

#### Parted错误
如果遇到GPT警告，脚本将尝试自动修复。如果问题持续存在，您可能需要手动运行：
```bash
sudo parted /dev/sda fix
sudo parted /dev/sda resizepart 2 100%
```

### 许可证

本项目采用Apache License 2.0许可证 - 详情请参阅[LICENSE](LICENSE)文件。

### 贡献

欢迎贡献！请随时提交Pull Request。

### 支持

如有问题或疑问，请在项目仓库中提交issue。


# 批量自动剪辑工具 - AutoVideoEditor

![AutoVideoEditor Screenshot](screenshot.png) <!-- 如果有截图的话，可以放在这里 -->

本地批量自动剪辑工具,专为视频二创去重而生。支持30+种剪辑手法，包括裁剪、滤镜、镜像、变速、抖动、抽帧快剪等常见操作，可批量处理并保存模板。

## 主要功能

- **二创去重批量处理**：预设多级去重手法，一键批量去重。内置初级、中级、高级去重方案
- **拆分镜头&混剪**：支持短剧混剪、好物混剪、镜头拆分
- **AI镜头场景识别**：多视频批量拆分，重新组合成新视频，提高原创度
- **多种合成方案**：好物混剪合成、随机合成、顺序合成、场景重组
- **批量处理**：支持导入文件夹批量处理
- **模板管理**：保存和加载自定义处理模板

## 系统要求

- Windows 10/11, macOS 10.15+, Ubuntu 20.04+
- Python 3.10
- 需要FFmpeg支持（已包含在安装步骤中）

## 安装方法

### 通过GitHub Actions构建（推荐）

1. 前往项目的 [Actions 页面](https://github.com/yourname/AutoVideoEditor/actions)
2. 选择最新的成功构建
3. 下载对应平台的构建包：
   - `AutoVideoEditor_Windows.zip` (Windows)
   - `AutoVideoEditor_macOS.zip` (macOS)
   - `AutoVideoEditor_Linux.zip` (Linux)
4. 解压并运行可执行文件

### 从源代码运行

1. 克隆仓库：
   ```bash
   git clone https://github.com/yourname/AutoVideoEditor.git
   cd AutoVideoEditor
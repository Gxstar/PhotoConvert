# PhotoConvert

一款简洁实用的图片格式转换工具，支持多种图片格式之间的相互转换。

## 功能特性

- **多格式支持**：PNG、JPG、JPEG、GIF、BMP、TIFF、WebP、HEIF、HEIC、AVIF、JXL
- **批量转换**：支持选择多个文件或整个文件夹进行批量处理
- **智能优化**：源格式与目标格式相同时自动跳过转换，仅重命名或移动文件
- **文件重命名**：支持基于 EXIF 信息自定义命名格式（日期、相机型号、序号等）
- **替换源文件**：可选择转换后删除原文件
- **图像质量控制**：可调节输出图片质量（1-100%）
- **高级选项**：
  - 编码速度调节（最快 ↔ 最慢）
  - 并行线程数设置
  - 色度采样选择（4:4:4 / 4:2:2 / 4:2:0 / 4:1:1）
  - 位深度选择（8位 / 10位 / 16位）

## 环境要求

- Python >= 3.14
- [ImageMagick](https://imagemagick.org/)（Wand 库的依赖）
- Windows / macOS / Linux

## 安装

### 1. 安装 ImageMagick

下载并安装 [ImageMagick](https://imagemagick.org/script/download.php)，安装时勾选 "Install legacy utilities"。

### 2. 克隆项目

```bash
git clone https://github.com/Gxstar/PhotoConvert.git
cd PhotoConvert
```

### 3. 安装依赖

推荐使用 [uv](https://docs.astral.sh/uv/)：

```bash
uv sync
```

或使用 pip：

```bash
pip install -r requirements.txt
```

### 4. 配置 ImageMagick 路径

编辑 `main.py`，修改 ImageMagick 安装路径：

```python
os.environ['MAGICK_HOME'] = r'D:\software\ImageMagick-7.1.2-Q16-HDRI'
```

## 运行

```bash
uv run python main.py
```

或激活虚拟环境后：

```bash
python main.py
```

## 打包为可执行文件

使用 PyInstaller 打包为独立的 `.exe` 文件：

### 方法一：使用现有的 spec 文件

```bash
pyinstaller main.spec
```

### 方法二：使用命令行参数

```bash
pyinstaller -F -w --hidden-import=ttkbootstrap --name "PhotoConvert" main.py
```

参数说明：
- `-F`：打包为单个可执行文件
- `-w`：运行时不显示命令行窗口
- `--hidden-import=ttkbootstrap`：确保 ttkbootstrap 被正确打包
- `--name`：指定输出文件名

打包完成后，可执行文件位于 `dist/` 目录下。

## 使用说明

1. **选择文件**：点击"选择文件"或"选择文件夹"添加待转换图片
2. **设置输出格式**：从下拉菜单选择目标格式
3. **选择输出目录**（可选）：默认输出到源文件所在目录
4. **重命名选项**（可选）：勾选后可自定义命名格式
5. **调整质量**：拖动滑块设置输出质量
6. **开始转换**：点击按钮执行转换

### 命名格式变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `{date}` | 拍摄日期 | 20240115 |
| `{time}` | 拍摄时间 | 143025 |
| `{model}` | 相机型号 | Canon_EOS_R5 |
| `{seq}` | 序号 | 001 |
| `{orig}` | 原文件名 | IMG_1234 |

示例：`{date}_{model}_{seq}` → `20240115_Canon_EOS_R5_001.avif`

## 依赖说明

- [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap) - 现代化的 Tkinter 主题
- [Wand](https://docs.wand-py.org/) - ImageMagick 的 Python 绑定
- [piexif](https://github.com/hMatoba/Piexif) - EXIF 信息读取

## 许可证

MIT License

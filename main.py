import os
os.environ['MAGICK_HOME'] = r'D:\software\ImageMagick-7.1.2-Q16-HDRI'
os.environ['MAGICK_THREAD_LIMIT'] = '0'  # 0 表示自动

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from wand.image import Image
import multiprocessing

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import ToolTip


class PhotoConverter:
    """图片格式转换器"""

    SUPPORTED_FORMATS = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp', 'heif', 'heic', 'avif', 'jxl']
    IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp', '.heif', '.heic', '.avif', '.jxl'}

    def __init__(self, root):
        self.root = root
        self.root.title("图片格式转换器")
        self.root.geometry("520x510")
        self.root.resizable(False, False)

        self.selected_files = []

        self._create_widgets()

    def _create_widgets(self):
        """创建界面组件"""
        # 文件选择区域
        file_frame = ttk.Labelframe(self.root, text="文件选择", padding=10)
        file_frame.pack(fill='x', padx=10, pady=5)

        self.file_label = ttk.Label(file_frame, text="未选择文件")
        self.file_label.pack(side='left', fill='x', expand=True)

        btn_frame = ttk.Frame(file_frame)
        btn_frame.pack(side='right')

        select_files_btn = ttk.Button(btn_frame, text="选择文件", command=self._select_files, width=10)
        select_files_btn.pack(side='left', padx=(0, 5))

        select_folder_btn = ttk.Button(btn_frame, text="选择文件夹", command=self._select_folder, width=10)
        select_folder_btn.pack(side='left')

        # 输出选项（格式和目录）
        output_frame = ttk.Labelframe(self.root, text="输出选项", padding=10)
        output_frame.pack(fill='x', padx=10, pady=5)

        # 第一行：输出格式
        row1 = ttk.Frame(output_frame)
        row1.pack(fill='x', pady=2)
        ttk.Label(row1, text="输出格式:").pack(side='left')
        self.format_var = tk.StringVar(value='avif')
        format_combo = ttk.Combobox(
            row1,
            textvariable=self.format_var,
            values=self.SUPPORTED_FORMATS,
            state='readonly',
            width=10
        )
        format_combo.pack(side='left', padx=5)

        # 第二行：输出目录
        row2 = ttk.Frame(output_frame)
        row2.pack(fill='x', pady=2)
        ttk.Label(row2, text="输出目录:").pack(side='left')
        self.output_dir = None
        self.output_dir_label = ttk.Label(row2, text="源文件目录", foreground="gray")
        self.output_dir_label.pack(side='left', padx=5, fill='x', expand=True)
        select_dir_btn = ttk.Button(row2, text="选择", command=self._select_output_dir, width=6)
        select_dir_btn.pack(side='left', padx=(5, 0))
        clear_dir_btn = ttk.Button(row2, text="清除", command=self._clear_output_dir, width=6)
        clear_dir_btn.pack(side='left', padx=(5, 0))

        # 第三行：替换源文件
        self.replace_var = tk.BooleanVar(value=False)
        replace_check = ttk.Checkbutton(
            output_frame,
            text="替换源文件 (将删除原文件)",
            variable=self.replace_var
        )
        replace_check.pack(anchor='w', pady=(5, 0))
        quality_frame = ttk.Labelframe(self.root, text="图像质量", padding=10)
        quality_frame.pack(fill='x', padx=10, pady=5)

        self.quality_var = tk.IntVar(value=85)
        quality_scale = ttk.Scale(
            quality_frame,
            from_=1,
            to=100,
            variable=self.quality_var,
            orient='horizontal',
            command=self._update_quality_label
        )
        quality_scale.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.quality_label = ttk.Label(quality_frame, text="85%", width=5)
        self.quality_label.pack(side='right')

        # 高级选项
        advanced_frame = ttk.Labelframe(self.root, text="高级选项", padding=10)
        advanced_frame.pack(fill='x', padx=10, pady=5)

        # 使用 grid 布局让选项对齐
        # 第一行：速度 和 线程数
        ttk.Label(advanced_frame, text="速度:").grid(row=0, column=0, sticky='e', padx=(0, 5), pady=3)
        self.speed_var = tk.StringVar(value="均衡")
        speed_combo = ttk.Combobox(advanced_frame, textvariable=self.speed_var, 
                                   values=["最快", "较快", "均衡", "较慢", "最慢"], state='readonly', width=10)
        speed_combo.grid(row=0, column=1, sticky='w', pady=3)
        speed_help = ttk.Label(advanced_frame, text="?", foreground="#1E90FF", cursor="hand2")
        speed_help.grid(row=0, column=2, sticky='w', padx=(2, 20))
        ToolTip(speed_help, text="编码速度与压缩效率的权衡\n最快：速度快但文件大\n最慢：文件小但耗时久\n推荐：一般选「均衡」")

        ttk.Label(advanced_frame, text="线程数:").grid(row=0, column=3, sticky='e', padx=(0, 5), pady=3)
        self.threads_var = tk.StringVar(value="自动")
        threads_combo = ttk.Combobox(advanced_frame, textvariable=self.threads_var,
                                     values=["自动", "1", "2", "4", "8", "16"], state='readonly', width=10)
        threads_combo.grid(row=0, column=4, sticky='w', pady=3)
        threads_help = ttk.Label(advanced_frame, text="?", foreground="#1E90FF", cursor="hand2")
        threads_help.grid(row=0, column=5, sticky='w', padx=(2, 0))
        ToolTip(threads_help, text="并行处理线程数\n自动：使用CPU核心数\n多线程可加速处理，但占用更多内存\n推荐：一般选「自动」")

        # 第二行：色度采样 和 位深度
        ttk.Label(advanced_frame, text="色度采样:").grid(row=1, column=0, sticky='e', padx=(0, 5), pady=3)
        self.chroma_var = tk.StringVar(value="4:2:0")
        chroma_combo = ttk.Combobox(advanced_frame, textvariable=self.chroma_var,
                                    values=["4:4:4", "4:2:2", "4:2:0", "4:1:1"], state='readonly', width=10)
        chroma_combo.grid(row=1, column=1, sticky='w', pady=3)
        chroma_help = ttk.Label(advanced_frame, text="?", foreground="#1E90FF", cursor="hand2")
        chroma_help.grid(row=1, column=2, sticky='w', padx=(2, 20))
        ToolTip(chroma_help, text="色度子采样方式，影响色彩精度与文件大小\n4:4:4：无压缩，色彩最准，文件最大\n4:2:0：常用压缩，文件小，肉眼差异小\n推荐：网页图片选4:2:0，专业编辑选4:4:4")

        ttk.Label(advanced_frame, text="位深度:").grid(row=1, column=3, sticky='e', padx=(0, 5), pady=3)
        self.depth_var = tk.StringVar(value="自动")
        depth_combo = ttk.Combobox(advanced_frame, textvariable=self.depth_var,
                                   values=["自动", "8位", "10位", "16位"], state='readonly', width=10)
        depth_combo.grid(row=1, column=4, sticky='w', pady=3)
        depth_help = ttk.Label(advanced_frame, text="?", foreground="#1E90FF", cursor="hand2")
        depth_help.grid(row=1, column=5, sticky='w', padx=(2, 0))
        ToolTip(depth_help, text="每个通道的位深度\n8位：标准，1670万色\n10位/16位：HDR、专业编辑\n推荐：普通用途选8位，HDR选10位")

        # 转换按钮和进度条
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill='x', padx=10, pady=10)

        convert_btn = ttk.Button(action_frame, text="开始转换", command=self._convert, width=12, bootstyle=PRIMARY)
        convert_btn.pack(side='left', padx=(0, 10))

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            action_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            length=200,
            bootstyle=STRIPED
        )
        self.progress_bar.pack(side='left', fill='x', expand=True, padx=(0, 10))

        self.progress_label = ttk.Label(action_frame, text="0/0", width=8)
        self.progress_label.pack(side='right')

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(self.root, textvariable=self.status_var, bootstyle=INFO, padding=5)
        status_label.pack(fill='x', padx=10, pady=5, side='bottom')

    def _update_quality_label(self, value):
        """更新质量显示标签"""
        self.quality_label.config(text=f"{int(float(value))}%")

    def _select_files(self):
        """选择文件"""
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.webp *.heif *.heic *.avif *.jxl"),
                ("所有文件", "*.*")
            ]
        )
        if files:
            self.selected_files = list(files)
            count = len(self.selected_files)
            self.file_label.config(text=f"已选择 {count} 个文件")
            self.status_var.set(f"已选择 {count} 个文件")

    def _select_folder(self):
        """选择文件夹"""
        folder = filedialog.askdirectory(title="选择包含图片的文件夹")
        if folder:
            # 扫描文件夹中的所有图片文件
            folder_path = Path(folder)
            image_files = []
            for ext in self.IMAGE_EXTENSIONS:
                image_files.extend(folder_path.glob(f'*{ext}'))
                image_files.extend(folder_path.glob(f'*{ext.upper()}'))
            
            # 去重并排序
            image_files = sorted(set(str(f) for f in image_files))
            
            if image_files:
                self.selected_files = image_files
                count = len(self.selected_files)
                self.file_label.config(text=f"已选择文件夹 ({count} 个图片)")
                self.status_var.set(f"已选择文件夹，共 {count} 个图片")
            else:
                messagebox.showinfo("提示", "所选文件夹中没有找到图片文件")

    def _select_output_dir(self):
        """选择输出目录"""
        folder = filedialog.askdirectory(title="选择输出目录")
        if folder:
            self.output_dir = folder
            # 显示缩短的路径
            if len(folder) > 35:
                display_path = "..." + folder[-32:]
            else:
                display_path = folder
            self.output_dir_label.config(text=display_path, foreground="black")

    def _clear_output_dir(self):
        """清除输出目录设置"""
        self.output_dir = None
        self.output_dir_label.config(text="源文件目录", foreground="gray")

    def _convert(self):
        """执行转换"""
        if not self.selected_files:
            messagebox.showwarning("提示", "请先选择文件")
            return

        output_format = self.format_var.get()
        replace_source = self.replace_var.get()

        # 设置线程数
        threads = self.threads_var.get()
        if threads == "自动":
            thread_count = multiprocessing.cpu_count()
        else:
            thread_count = int(threads)
        os.environ['MAGICK_THREAD_LIMIT'] = str(thread_count)

        # 映射速度选项到质量范围
        speed_map = {
            "最快": 10,
            "较快": 30,
            "均衡": 50,
            "较慢": 75,
            "最慢": 100
        }

        total_count = len(self.selected_files)
        success_count = 0
        fail_count = 0

        # 重置进度条
        self.progress_var.set(0)
        self.progress_label.config(text=f"0/{total_count}")

        for idx, file_path in enumerate(self.selected_files, 1):
            try:
                self.status_var.set(f"正在转换: {Path(file_path).name}")
                # 更新进度
                self.progress_var.set((idx / total_count) * 100)
                self.progress_label.config(text=f"{idx}/{total_count}")
                self.root.update()

                with Image(filename=file_path) as img:
                    # 设置图像质量（对有损压缩格式有效）
                    quality = self.quality_var.get()
                    if output_format.lower() in ['jpg', 'jpeg', 'webp', 'avif', 'heif', 'heic', 'jxl']:
                        img.compression_quality = quality

                    # 设置位深度
                    depth = self.depth_var.get()
                    if depth != "自动":
                        depth_map = {"8位": 8, "10位": 10, "16位": 16}
                        if depth in depth_map:
                            img.depth = depth_map[depth]

                    # 设置色度采样（通过 options 传递）
                    chroma = self.chroma_var.get()
                    if chroma != "4:4:4":
                        chroma_map = {
                            "4:2:2": "4:2:2",
                            "4:2:0": "4:2:0",
                            "4:1:1": "4:1:1"
                        }
                        if chroma in chroma_map:
                            img.options['jpeg:sampling-factor'] = chroma_map[chroma]

                    # 设置速度（通过 quality 调整）
                    speed = self.speed_var.get()
                    if speed in speed_map and output_format.lower() in ['jpg', 'jpeg', 'webp', 'avif', 'heif', 'heic', 'jxl']:
                        # 速度越快，质量越低
                        base_quality = self.quality_var.get()
                        speed_factor = speed_map[speed] / 100.0
                        img.compression_quality = int(base_quality * (0.5 + 0.5 * speed_factor))

                    if replace_source:
                        # 替换源文件
                        output_path = Path(file_path).with_suffix(f'.{output_format}')
                        img.save(filename=str(output_path))

                        # 删除原文件（如果扩展名不同）
                        if Path(file_path) != output_path:
                            Path(file_path).unlink()
                    else:
                        # 根据输出目录设置决定输出路径
                        if self.output_dir:
                            output_path = Path(self.output_dir) / (Path(file_path).stem + f'.{output_format}')
                        else:
                            output_path = Path(file_path).with_suffix(f'.{output_format}')
                        img.save(filename=str(output_path))

                success_count += 1
            except Exception as e:
                fail_count += 1
                print(f"转换失败: {file_path}, 错误: {e}")

        # 显示结果
        message = f"转换完成！成功: {success_count}，失败: {fail_count}"
        self.status_var.set(message)
        self.progress_label.config(text=f"{total_count}/{total_count}")
        messagebox.showinfo("完成", message)


def main():
    root = ttk.Window(themename="minty")
    app = PhotoConverter(root)
    root.mainloop()


if __name__ == "__main__":
    main()

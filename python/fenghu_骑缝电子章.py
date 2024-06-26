import fitz  # PyMuPDF
from PIL import Image
import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox

# 计算缩放因子
def calculate_scale_factor(png_width, a4_width=2480):
    return png_width / a4_width

# 将PDF文件拆分为单页PNG图像（保持原始分辨率）
def pdf_to_png(pdf_path, output_dir, dpi):
    doc = fitz.open(pdf_path)
    images = []

    for i in range(len(doc)):
        page = doc.load_page(i)
        pix = page.get_pixmap(dpi=dpi)  # 获取指定 DPI 的Pixmap，确保高分辨率
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)

        print(f"PDF Page {i + 1} Dimensions: {pix.width} x {pix.height}")

    doc.close()

    # 保存每一页为单独的PNG文件
    png_paths = []
    for idx, img in enumerate(images):
        png_path = os.path.join(output_dir, f"page_{idx + 1}.png")
        img.save(png_path, "PNG", compress_level=0, quality=100)  # 设置最高质量参数
        png_paths.append(png_path)

        print(f"Output PNG Dimensions: {img.width} x {img.height}")

    return png_paths, images[0].width, images[0].height

# 将电子章按页数等分并返回图像列表
def split_stamp(stamp_path, num_splits):
    stamp = Image.open(stamp_path)
    width, height = stamp.size
    split_width = width // num_splits
    splits = []
    for i in range(num_splits):
        box = (i * split_width, 0, (i + 1) * split_width, height)
        split_stamp = stamp.crop(box)
        splits.append(split_stamp)
    
    print(f"Original Stamp Dimensions: {width} x {height}")

    return splits

# 添加电子章到PNG图像并调整大小（保持相对比例）
def add_stamp_to_png(png_path, stamp, output_path, scale_factor, position="right_bottom", full_stamp_position=None):
    img = Image.open(png_path)
    
    # 计算电子章的新大小
    new_width = int(stamp.width * scale_factor)
    new_height = int(stamp.height * scale_factor)
    
    # 调整电子章大小
    scaled_stamp = stamp.resize((new_width, new_height), Image.LANCZOS)
    
    if position == "right_bottom":
        x = img.width - scaled_stamp.width
        y = img.height - scaled_stamp.height
    elif position == "full_bottom_right" and full_stamp_position:
        x, y = full_stamp_position
    else:
        # 计算电子章的位置（右对齐靠下三分之一）
        x = img.width - scaled_stamp.width
        y = img.height - scaled_stamp.height - img.height // 3
    
    # 添加电子章到PNG图像
    img.paste(scaled_stamp, (x, y), scaled_stamp)
    img.save(output_path, "PNG", compress_level=0, quality=100)  # 设置最高质量参数
    
    print(f"Scaled Stamp Dimensions: {scaled_stamp.width} x {scaled_stamp.height}")
    print(f"Stamp Position on PNG: (x={x}, y={y})")

# 将PNG图像合成为PDF文件
def png_to_pdf(png_paths, output_path):
    doc = fitz.open()
    for png_path in png_paths:
        page = doc.new_page()
        pix = fitz.Pixmap(png_path)
        page.insert_image(page.rect, pixmap=pix)
        pix = None  # 清理资源
    doc.save(output_path)
    doc.close()

# 主程序入口
def process_pdf_with_stamp(pdf_path, stamp_path, output_dir, dpi, full_stamp_position):
    # 创建临时目录存放中间PNG文件
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 将PDF转换为单页PNG图像
    png_paths, png_width, png_height = pdf_to_png(pdf_path, output_dir, dpi)

    # 获取PDF页数
    num_pages = len(png_paths)
    
    # 加载并切分电子章
    stamps = split_stamp(stamp_path, num_pages)

    # 获取PNG图像宽度，并计算缩放因子
    scale_factor = calculate_scale_factor(png_width)

    print(f"Output PNG Width: {png_width}")
    print(f"Scale Factor: {scale_factor}")

    # 为每个PNG图像添加电子章并保存
    stamped_png_paths = []
    for idx, png_path in enumerate(png_paths):
        if idx == num_pages - 1:
            # 最后一页添加完整电子章
            full_stamp = Image.open(stamp_path)
            stamped_png_path = os.path.join(output_dir, f"stamped_page_{idx + 1}.png")
            add_stamp_to_png(png_path, full_stamp, stamped_png_path, scale_factor, position="full_bottom_right", full_stamp_position=full_stamp_position)
            stamped_png_paths.append(stamped_png_path)
        else:
            # 其他页添加分割电子章
            stamped_png_path = os.path.join(output_dir, f"stamped_page_{idx + 1}.png")
            add_stamp_to_png(png_path, stamps[idx], stamped_png_path, scale_factor, position="right_third")
            stamped_png_paths.append(stamped_png_path)

    # 将带有电子章的PNG图像合成为新的PDF文件
    timestamp = time.strftime("%Y%m%d%H%M%S")
    output_pdf = os.path.join(output_dir, f"stamped_pdf_{timestamp}.pdf")
    png_to_pdf(stamped_png_paths, output_pdf)

    return output_pdf, png_width, png_height

# 选择PDF文件路径
def select_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    pdf_path_entry.delete(0, tk.END)
    pdf_path_entry.insert(0, file_path)

# 选择电子章路径
def select_stamp():
    file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
    if file_path:
        stamp_path_entry.delete(0, tk.END)
        stamp_path_entry.insert(0, file_path)

# 开始处理
def start_processing():
    pdf_path = pdf_path_entry.get()
    stamp_path = stamp_path_entry.get()
    dpi = int(dpi_entry.get())
    output_dir = os.path.dirname(pdf_path)
    full_stamp_x = int(full_stamp_x_entry.get())
    full_stamp_y = int(full_stamp_y_entry.get())
    full_stamp_position = (full_stamp_x, full_stamp_y)

    if not os.path.isfile(pdf_path):
        messagebox.showerror("错误", "请选择有效的PDF文件")
        return

    if not os.path.isfile(stamp_path):
        messagebox.showerror("错误", "请选择有效的电子章文件")
        return

    try:
        output_pdf, png_width, png_height = process_pdf_with_stamp(pdf_path, stamp_path, output_dir, dpi, full_stamp_position)
        result_label.config(text=f"生成图片分辨率：{png_width} x {png_height}")
        messagebox.showinfo("成功", f"已生成带有电子章的PDF文件：{output_pdf}")
    except Exception as e:
        messagebox.showerror("错误", f"处理过程中出现错误：{str(e)}")

# 预览生成图片分辨率
def preview_resolution():
    pdf_path = pdf_path_entry.get()
    dpi = int(dpi_entry.get())
    output_dir = os.path.dirname(pdf_path)

    if not os.path.isfile(pdf_path):
        messagebox.showerror("错误", "请选择有效的PDF文件")
        return

    try:
        _, png_width, png_height = pdf_to_png(pdf_path, output_dir, dpi)
        result_label.config(text=f"生成图片分辨率：{png_width} x {png_height}")
    except Exception as e:
        messagebox.showerror("错误", f"预览过程中出现错误：{str(e)}")


# 继续创建GUI
root = tk.Tk()
root.title("PDF添加骑缝章")
root.geometry("700x400")

# PDF路径选择
tk.Label(root, text="PDF文件路径:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
pdf_path_entry = tk.Entry(root, width=50)
pdf_path_entry.insert(0, "/Users/chenglei/Desktop/test/test4ye.pdf")
pdf_path_entry.grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="选择", command=select_pdf).grid(row=0, column=2, padx=10, pady=10)

# 电子章路径选择
tk.Label(root, text="电子章路径:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
stamp_path_entry = tk.Entry(root, width=50)
stamp_path_entry.insert(0, "/Users/chenglei/Desktop/test/全章(圆).png")
stamp_path_entry.grid(row=1, column=1, padx=10, pady=10)
tk.Button(root, text="选择", command=select_stamp).grid(row=1, column=2, padx=10, pady=10)

# DPI设置
tk.Label(root, text="DPI分辨率:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
dpi_entry = tk.Entry(root, width=10)
dpi_entry.insert(0, "72")
dpi_entry.grid(row=2, column=1, padx=10, pady=10)

# 结尾页全章位置设置
tk.Label(root, text="结尾页全章位置 (X):").grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
full_stamp_x_entry = tk.Entry(root, width=10)
full_stamp_x_entry.insert(0, "0")
full_stamp_x_entry.grid(row=3, column=1, padx=10, pady=10)

tk.Label(root, text="结尾页全章位置 (Y):").grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)
full_stamp_y_entry = tk.Entry(root, width=10)
full_stamp_y_entry.insert(0, "0")
full_stamp_y_entry.grid(row=4, column=1, padx=10, pady=10)

# 预览生成图片分辨率按钮
tk.Button(root, text="预览生成图片分辨率", command=preview_resolution).grid(row=5, column=0, columnspan=3, padx=10, pady=10)

# 结束按钮
tk.Button(root, text="开始处理", command=start_processing).grid(row=6, column=0, columnspan=3, padx=10, pady=10)

# 结果显示标签
result_label = tk.Label(root, text="")
result_label.grid(row=7, column=0, columnspan=3, padx=10, pady=10)

# 运行主循环
root.mainloop()

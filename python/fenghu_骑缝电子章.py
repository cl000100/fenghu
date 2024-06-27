import fitz  # PyMuPDF
from PIL import Image, ImageTk
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

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

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

        print(f"Output PNG Path: {png_path} Dimensions: {img.width} x {img.height}")

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
    for i, split in enumerate(splits):
        print(f"Split {i + 1} Dimensions: {split.size}")

    return splits

# 添加电子章到PNG图像并调整大小（保持相对比例）
def add_stamp_to_png(png_path, stamp, output_path, scale_factor, position="custom", custom_position=None):
    img = Image.open(png_path)
    
    # 计算电子章的新大小
    new_width = int(stamp.width * scale_factor)
    new_height = int(stamp.height * scale_factor)
    
    # 调整电子章大小
    scaled_stamp = stamp.resize((new_width, new_height), Image.LANCZOS)
    
    # 根据指定位置添加电子章
    if position == "custom" and custom_position:
        x, y = custom_position
    elif position == "right_bottom":
        x = img.width - scaled_stamp.width
        y = img.height - scaled_stamp.height
    elif position == "right_third":
        x = img.width - scaled_stamp.width
        y = img.height - scaled_stamp.height - img.height // 3
    
    # 添加电子章到PNG图像
    img.paste(scaled_stamp, (x, y), scaled_stamp)
    print(f"Added stamp to PNG: {png_path}, position: {position}, coordinates: (x={x}, y={y})")
    
    img.save(output_path, "PNG", compress_level=0, quality=100)  # 设置最高质量参数
    print(f"Saved stamped PNG to: {output_path}")

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
# 修改process_pdf_with_stamp函数，传递正确的位置参数
def process_pdf_with_stamp(pdf_path, stamp_path, output_dir, dpi, full_stamp_pages, seam_stamp_pages):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    png_paths, png_width, png_height = pdf_to_png(pdf_path, output_dir, dpi)
    num_pages = len(png_paths)
    scale_factor = calculate_scale_factor(png_width)
    stamped_png_paths = list(png_paths)  # 复制一份原始PNG路径列表，用于储存处理后的PNG路径

    # 处理全章
    for idx, png_path in enumerate(png_paths):
        if (idx + 1) in full_stamp_pages:
            print(f"Processing full stamp for page {idx + 1}")
            full_stamp = Image.open(stamp_path)
            stamped_png_path = os.path.join(output_dir, f"full_stamped_page_{idx + 1}.png")
            position = stamp_positions.get(idx + 1, (0, 0))  # 获取对应页码的全章位置
            add_stamp_to_png(png_path, full_stamp, stamped_png_path, scale_factor, position="custom", custom_position=position)
            stamped_png_paths[idx] = stamped_png_path  # 更新处理后的PNG路径
            print(f"Added full stamp to page {idx + 1}, saved to {stamped_png_path}")

    # 处理骑缝章
    seam_stamps = split_stamp(stamp_path, len(seam_stamp_pages))
    for idx, page_num in enumerate(seam_stamp_pages):
        if page_num <= num_pages:
            print(f"Processing seam stamp for page {page_num}")
            original_png_path = stamped_png_paths[page_num - 1] if stamped_png_paths[page_num - 1] != png_paths[page_num - 1] else png_paths[page_num - 1]
            stamped_png_path = os.path.join(output_dir, f"seam_stamped_page_{page_num}.png")
            add_stamp_to_png(original_png_path, seam_stamps[idx], stamped_png_path, scale_factor, position="right_third")
            stamped_png_paths[page_num - 1] = stamped_png_path  # 更新处理后的PNG路径
            print(f"Added seam stamp to page {page_num}, saved to {stamped_png_path}")

    base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    timestamp = time.strftime("%Y%m%d%H%M%S")
    output_pdf = os.path.join(output_dir, f"{base_filename}_{timestamp}.pdf")
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
    full_stamp_pages = list(map(int, full_stamp_page_entry.get().split(',')))
    seam_stamp_pages = list(map(int, seam_stamp_page_entry.get().split(',')))

    if not os.path.isfile(pdf_path):
        messagebox.showerror("错误", "请选择有效的PDF文件")
        return

    if not os.path.isfile(stamp_path):
        messagebox.showerror("错误", "请选择有效的电子章文件")
        return

    try:
        output_pdf, png_width, png_height = process_pdf_with_stamp(pdf_path, stamp_path, output_dir, dpi, full_stamp_pages, seam_stamp_pages)
        result_label.config(text=f"生成图片分辨率：{png_width} x {png_height}")
        messagebox.showinfo("成功", f"已生成带有电子章的PDF文件：{output_pdf}")
    except Exception as e:
        messagebox.showerror("错误", f"处理过程中出现错误：{str(e)}")

# 预览生成图片分辨率
def preview_resolution():
    pdf_path = pdf_path_entry.get()
    dpi = int(dpi_entry.get())
    output_dir = os.path.dirname(pdf_path)
    full_stamp_pages = list(map(int, full_stamp_page_entry.get().split(',')))
    seam_stamp_pages = list(map(int, seam_stamp_page_entry.get().split(',')))

    if not os.path.isfile(pdf_path):
        messagebox.showerror("错误", "请选择有效的PDF文件")
        return

    try:
        global png_width, png_height, stamp_positions
        png_paths, png_width, png_height = pdf_to_png(pdf_path, output_dir, dpi)
        result_label.config(text=f"生成图片分辨率：{png_width} x {png_height}")

        valid_pages = [p for p in full_stamp_pages if 1 <= p <= len(png_paths)]
        if not valid_pages:
            messagebox.showerror("错误", "请输入有效的页码")
            return
        
        for page in valid_pages:
            preview_png_path = png_paths[page - 1]
            preview_last_page(preview_png_path)
            messagebox.showinfo("提示", f"请点击画布选择第 {page} 页的全章位置")
            canvas_clicked.set(False)  # 重置为False，等待用户点击
            root.wait_variable(canvas_clicked)  # 等待用户选择位置
            stamp_positions[page] = (int(full_stamp_x_entry.get()), int(full_stamp_y_entry.get()))

    except Exception as e:
        messagebox.showerror("错误", f"预览过程中出现错误：{str(e)}")

def preview_last_page(last_png_path):
    img = Image.open(last_png_path)
    scale_factor_canvas = 300 / img.width
    preview_img = img.resize((300, int(img.height * scale_factor_canvas)), Image.LANCZOS)
    preview_img_tk = ImageTk.PhotoImage(preview_img)
    canvas.create_image(0, 0, anchor=tk.NW, image=preview_img_tk)
    canvas.image = preview_img_tk

# 处理画布点击事件
def on_canvas_click(event):
    global png_width, png_height
    scale_factor = 300 / png_width
    original_x = int(event.x / scale_factor)
    original_y = int(event.y / scale_factor)
    
    full_stamp_x_entry.delete(0, tk.END)
    full_stamp_y_entry.delete(0, tk.END)
    full_stamp_x_entry.insert(0, original_x)
    full_stamp_y_entry.insert(0, original_y)
    
    canvas_clicked.set(True)  # 设置变量值为True以继续执行

    
# 创建GUI
root = tk.Tk()
root.title("PDF电子章工具")

# 定义全局变量
global png_width, png_height, stamp_positions, canvas_clicked
stamp_positions = {}
canvas_clicked = tk.BooleanVar()  # 用于等待用户点击画布
canvas_clicked.set(False)  # 初始化为False

# 输入文件路径部分
tk.Label(root, text="PDF文件路径:").grid(row=0, column=0, padx=10, pady=5)
pdf_path_entry = tk.Entry(root, width=50)
pdf_path_entry.grid(row=0, column=1, padx=10, pady=5)
pdf_path_entry.insert(0, "/Users/chenglei/Desktop/test.pdf")
tk.Button(root, text="选择文件", command=select_pdf).grid(row=0, column=2, padx=10, pady=5)

# 电子章路径部分
tk.Label(root, text="电子章路径:").grid(row=1, column=0, padx=10, pady=5)
stamp_path_entry = tk.Entry(root, width=50)
stamp_path_entry.grid(row=1, column=1, padx=10, pady=5)
stamp_path_entry.insert(0, "/Users/chenglei/Library/Mobile Documents/com~apple~CloudDocs/VSCode/source/全章(圆).png")
tk.Button(root, text="选择文件", command=select_stamp).grid(row=1, column=2, padx=10, pady=5)

# DPI输入部分
tk.Label(root, text="DPI:").grid(row=2, column=0, padx=10, pady=5)
dpi_entry = tk.Entry(root, width=20)
dpi_entry.grid(row=2, column=1, padx=10, pady=5)
dpi_entry.insert(0, "72")

# 全章位置输入部分
tk.Label(root, text="全章位置X:").grid(row=3, column=0, padx=10, pady=5)
full_stamp_x_entry = tk.Entry(root, width=20)
full_stamp_x_entry.grid(row=3, column=1, padx=10, pady=5)
full_stamp_x_entry.insert(0, "0")

tk.Label(root, text="全章位置Y:").grid(row=4, column=0, padx=10, pady=5)
full_stamp_y_entry = tk.Entry(root, width=20)
full_stamp_y_entry.grid(row=4, column=1, padx=10, pady=5)
full_stamp_y_entry.insert(0, "0")

# 全章页码输入部分
tk.Label(root, text="全章页码(用逗号分隔):").grid(row=5, column=0, padx=10, pady=5)
full_stamp_page_entry = tk.Entry(root, width=20)
full_stamp_page_entry.grid(row=5, column=1, padx=10, pady=5)
full_stamp_page_entry.insert(0, "1,3")

# 骑缝章页码输入部分
tk.Label(root, text="骑缝章页码(用逗号分隔):").grid(row=6, column=0, padx=10, pady=5)
seam_stamp_page_entry = tk.Entry(root, width=20)
seam_stamp_page_entry.grid(row=6, column=1, padx=10, pady=5)
seam_stamp_page_entry.insert(0, "2,4")

# 开始处理按钮
tk.Button(root, text="开始处理", command=start_processing).grid(row=7, column=1, padx=10, pady=10)

# 预览生成图片分辨率按钮
tk.Button(root, text="预览生成图片分辨率", command=preview_resolution).grid(row=8, column=1, padx=10, pady=10)

# 结果标签
result_label = tk.Label(root, text="")
result_label.grid(row=9, column=0, columnspan=3, padx=10, pady=10)

# 创建画布
canvas = tk.Canvas(root, width=300, height=3508 * (300 / 2480), bg='white')
canvas.grid(row=10, column=0, columnspan=3, padx=10, pady=10)
canvas.bind("<Button-1>", on_canvas_click)

root.mainloop()

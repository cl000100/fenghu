import fitz  # PyMuPDF
from PIL import Image, ImageTk
import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox
# 定义全局变量
global png_width, png_height
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
def add_stamp_to_png(png_path, stamp, output_path, scale_factor, position="right_bottom", additional_stamp=None, additional_position=None):
    img = Image.open(png_path)
    
    # 计算电子章的新大小
    new_width = int(stamp.width * scale_factor)
    new_height = int(stamp.height * scale_factor)
    
    # 调整电子章大小
    scaled_stamp = stamp.resize((new_width, new_height), Image.LANCZOS)
    
    if position == "right_bottom":
        x = img.width - scaled_stamp.width
        y = img.height - scaled_stamp.height
    elif position == "right_third":
        x = img.width - scaled_stamp.width
        y = img.height - scaled_stamp.height - img.height // 3
    
    # 添加电子章到PNG图像
    img.paste(scaled_stamp, (x, y), scaled_stamp)

    # 如果有额外的电子章，添加到指定位置
    if additional_stamp and additional_position:
        add_x, add_y = additional_position
        add_scale_factor = img.width / 2480
        additional_new_width = int(additional_stamp.width * add_scale_factor)
        additional_new_height = int(additional_stamp.height * add_scale_factor)
        additional_stamp_resized = additional_stamp.resize((additional_new_width, additional_new_height), Image.LANCZOS)
        add_x -= additional_stamp_resized.width // 2
        add_y -= additional_stamp_resized.height // 2
        img.paste(additional_stamp_resized, (add_x, add_y), additional_stamp_resized)
    
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
# 更新 process_pdf_with_stamp 函数
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
        stamped_png_path = os.path.join(output_dir, f"stamped_page_{idx + 1}.png")
        if idx == num_pages - 1:
            # 最后一页添加骑缝章和完整电子章
            full_stamp = Image.open(stamp_path)
            add_stamp_to_png(png_path, stamps[idx], stamped_png_path, scale_factor, position="right_third", additional_stamp=full_stamp, additional_position=full_stamp_position)
        else:
            # 其他页添加分割电子章
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
        global png_width, png_height  # 声明全局变量
        png_paths, png_width, png_height = pdf_to_png(pdf_path, output_dir, dpi)
        result_label.config(text=f"生成图片分辨率：{png_width} x {png_height}")
        
        # 预览最后一页
        last_png_path = png_paths[-1]
        last_img = Image.open(last_png_path)
        
        # 缩放因子
        canvas_width = 300
        k_scale2 = canvas_width / png_width
        canvas_height = int(png_height * k_scale2)
        
        # 调整画布尺寸
        canvas.config(width=canvas_width, height=canvas_height)
        
        # 缩放并显示图像
        scaled_img = last_img.resize((canvas_width, canvas_height), Image.LANCZOS)
        canvas_img = ImageTk.PhotoImage(scaled_img)
        canvas.create_image(0, 0, anchor='nw', image=canvas_img)
        canvas.image = canvas_img
        
        # 将 on_canvas_click 函数绑定到画布点击事件中
        canvas.bind("<Button-1>", on_canvas_click)
        
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
# 修改 on_canvas_click 函数
def on_canvas_click(event):
    global png_width, png_height
    # 更新电子章位置
    scale_factor = 300 / png_width
    original_x = int(event.x / scale_factor)
    original_y = int(event.y / scale_factor)
    
    full_stamp_x_entry.delete(0, tk.END)
    full_stamp_y_entry.delete(0, tk.END)
    full_stamp_x_entry.insert(0, original_x)
    full_stamp_y_entry.insert(0, original_y)


# 创建GUI
root = tk.Tk()
root.title("PDF电子章工具")

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
dpi_entry.insert(0, "300")

# 全章位置输入部分
tk.Label(root, text="全章位置X:").grid(row=3, column=0, padx=10, pady=5)
full_stamp_x_entry = tk.Entry(root, width=20)
full_stamp_x_entry.grid(row=3, column=1, padx=10, pady=5)
full_stamp_x_entry.insert(0, "0")

tk.Label(root, text="全章位置Y:").grid(row=4, column=0, padx=10, pady=5)
full_stamp_y_entry = tk.Entry(root, width=20)
full_stamp_y_entry.grid(row=4, column=1, padx=10, pady=5)
full_stamp_y_entry.insert(0, "0")

# 开始处理按钮
tk.Button(root, text="开始处理", command=start_processing).grid(row=5, column=1, padx=10, pady=10)

# 预览生成图片分辨率按钮
tk.Button(root, text="预览生成图片分辨率", command=preview_resolution).grid(row=6, column=1, padx=10, pady=10)

# 结果标签
result_label = tk.Label(root, text="")
result_label.grid(row=7, column=0, columnspan=3, padx=10, pady=10)

# 创建画布
canvas = tk.Canvas(root, width=300, height=3508 * (300 / 2480), bg='white')
canvas.grid(row=8, column=0, columnspan=3, padx=10, pady=10)
canvas.bind("<Button-1>", on_canvas_click)

root.mainloop()

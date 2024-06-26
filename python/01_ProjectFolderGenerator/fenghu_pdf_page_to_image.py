import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import fitz  # PyMuPDF
from PIL import Image
import io
import os

def pdf_page_to_image(pdf_path, output_image_path, page_number=0, zoom=2.0):
    # 打开PDF文件
    pdf_document = fitz.open(pdf_path)
    
    # 获取指定页
    page = pdf_document.load_page(page_number)
    
    # 设置缩放级别
    mat = fitz.Matrix(zoom, zoom)
    
    # 渲染页面为图像
    pix = page.get_pixmap(matrix=mat, alpha=False)
    
    # 将图像数据转换为PIL Image对象
    image = Image.open(io.BytesIO(pix.tobytes()))
    
    # 保存图像
    image.save(output_image_path, format='PNG')

def select_pdf():
    pdf_path = filedialog.askopenfilename(
        filetypes=[("PDF files", "*.pdf")],
        title="选择一个PDF文件"
    )
    if pdf_path:
        try:
            page_range = simpledialog.askstring(
                "输入页码范围",
                "请输入页码范围（例如1-3, 5）："
            )
            if page_range:
                page_numbers = parse_page_range(page_range)
                for page_number in page_numbers:
                    output_image_path = os.path.splitext(pdf_path)[0] + f"_page{page_number}.png"
                    pdf_page_to_image(pdf_path, output_image_path, page_number-1)
                messagebox.showinfo("完成", "图像已成功保存")
        except Exception as e:
            messagebox.showerror("错误", f"无法将PDF转换为图像: {str(e)}")

def parse_page_range(page_range):
    pages = set()
    for part in page_range.split(','):
        if '-' in part:
            start, end = part.split('-')
            pages.update(range(int(start), int(end) + 1))
        else:
            pages.add(int(part))
    return sorted(pages)

# 创建主窗口
root = tk.Tk()
root.title("PDF转换器")

# 设置窗口大小和背景颜色
root.geometry("400x200")
root.configure(bg='#f0f0f0')

# 标题标签
title_label = tk.Label(root, text="PDF 转换器", font=("Helvetica", 16, "bold"), bg='#f0f0f0')
title_label.pack(pady=10)

# 说明标签
instruction_label = tk.Label(root, text="选择PDF文件并输入页码范围", font=("Helvetica", 12), bg='#f0f0f0')
instruction_label.pack(pady=5)

# 添加选择按钮
select_button = tk.Button(root, text="选择PDF文件", command=select_pdf, font=("Helvetica", 12), bg='#4caf50', fg='black')
select_button.pack(pady=20)

# 运行主循环
root.mainloop()
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import time

class StampApp:
    def __init__(self, root):
        self.root = root
        self.root.title("电子章添加工具")
        self.root.geometry("800x800")  # 固定窗口大小为 800x800

        self.input_image_path = "/Users/chenglei/Desktop/240626_KFC宵夜/正常大小_副本.png"  # 默认输入图片路径
        self.stamp_image_path = "/Users/chenglei/Desktop/240626_KFC宵夜/全章(圆).png"  # 默认电子章路径
        self.stamp_preview_position = None

        # 创建并放置组件
        self.create_widgets()

        # 加载默认输入图片和默认电子章图片
        self.load_default_input_image()
        self.load_default_stamp_image()

    def load_default_input_image(self):
        if self.input_image_path:
            self.input_button.config(text="已选择输入图片")

            original_image = Image.open(self.input_image_path)
            self.input_image_size = original_image.size
            self.display_image(original_image)
            self.update_debug_info()

    def load_default_stamp_image(self):
        if self.stamp_image_path:
            self.stamp_button.config(text="已选择电子章图片")

            stamp_image = Image.open(self.stamp_image_path)
            self.stamp_image_size = stamp_image.size
            self.update_debug_info()

    def load_input_image(self):
        self.input_image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if self.input_image_path:
            self.input_button.config(text="已选择输入图片")

            original_image = Image.open(self.input_image_path)
            self.input_image_size = original_image.size
            self.display_image(original_image)
            self.update_debug_info()

    def load_stamp_image(self):
        self.stamp_image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png")])
        if self.stamp_image_path:
            self.stamp_button.config(text="已选择电子章图片")

            stamp_image = Image.open(self.stamp_image_path)
            self.stamp_image_size = stamp_image.size
            self.update_debug_info()

    def create_widgets(self):
        self.label = tk.Label(self.root, text="选择输入图片和电子章图片，并在Canvas上选择电子章位置")
        self.label.pack()

        self.input_button = tk.Button(self.root, text="选择输入图片", command=self.load_input_image)
        self.input_button.pack()

        self.stamp_button = tk.Button(self.root, text="选择电子章图片", command=self.load_stamp_image)
        self.stamp_button.pack()

        self.canvas = tk.Canvas(self.root, bg="white", width=800, height=600)
        self.canvas.pack(expand=True, fill=tk.BOTH)

        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.process_button = tk.Button(self.root, text="生成带电子章的图片", command=self.add_stamp_to_image)
        self.process_button.pack()

        self.output_label = tk.Label(self.root, text="")
        self.output_label.pack()

    def on_canvas_click(self, event):
        if self.stamp_image_path:
            self.stamp_preview_position = (event.x, event.y)
            self.canvas.delete("stamp_preview")
            stamp_image = Image.open(self.stamp_image_path)

            scale_factor = self.get_scale_factor()

            preview_width = int(stamp_image.width * scale_factor * self.image_scale)
            preview_height = int(stamp_image.height * scale_factor * self.image_scale)
            preview_image = stamp_image.resize((preview_width, preview_height), Image.LANCZOS)

            self.stamp_tk = ImageTk.PhotoImage(preview_image)
            preview_x = event.x - preview_width // 2
            preview_y = event.y - preview_height // 2
            self.canvas.create_image(preview_x, preview_y, anchor=tk.NW, image=self.stamp_tk, tags="stamp_preview")
            self.update_debug_info()

    def display_image(self, image):
        self.canvas.delete("all")

        self.image_width, self.image_height = image.size
        max_canvas_width = 800
        max_canvas_height = 600

        self.image_scale = min(max_canvas_width / self.image_width, max_canvas_height / self.image_height)
        canvas_width = int(self.image_width * self.image_scale)
        canvas_height = int(self.image_height * self.image_scale)

        self.image_tk = ImageTk.PhotoImage(image.resize((canvas_width, canvas_height), Image.LANCZOS))
        self.canvas.config(width=max_canvas_width, height=max_canvas_height)
        self.canvas.create_image(max_canvas_width // 2, max_canvas_height // 2, anchor=tk.CENTER, image=self.image_tk)
        self.update_debug_info()

    def get_scale_factor(self):
        if self.input_image_path:
            base_image = Image.open(self.input_image_path)
            return base_image.width / 2480
        return 1.0

    def update_debug_info(self, output_stamp_position=None):
        debug_info = [
            f"输入图片尺寸: {getattr(self, 'image_width', '未选择')}x{getattr(self, 'image_height', '未选择')}",
            f"输入电子章尺寸: {getattr(self, 'stamp_image_size', '未选择')}",
            f"预览窗口输入图片尺寸及缩放系数: {getattr(self, 'image_width', '未选择')}x{getattr(self, 'image_height', '未选择')} (缩放系数: {getattr(self, 'image_scale', '未选择'):.2f})",
            f"预览窗口电子章尺寸及缩放系数: {getattr(self, 'stamp_preview_position', '未选择')} (缩放系数: {self.get_scale_factor() * getattr(self, 'image_scale', 1):.2f})",
            f"预览窗口鼠标点击位置: {getattr(self, 'stamp_preview_position', '未选择')}",
            f"预览窗口电子章位置: {getattr(self, 'stamp_preview_position', '未选择')}",
        ]

        if output_stamp_position:
            debug_info.append(f"输出图片电子章位置: {output_stamp_position}")

        print("\n".join(debug_info))

    def add_stamp_to_image(self):
        if not self.input_image_path or not self.stamp_image_path or not self.stamp_preview_position:
            self.output_label.config(text="请先选择输入图片、电子章图片，并在Canvas上选择电子章位置")
            return

        input_folder = os.path.dirname(self.input_image_path)
        input_filename = os.path.basename(self.input_image_path)
        filename_without_ext, ext = os.path.splitext(input_filename)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_filename = f"{filename_without_ext}_{timestamp}.png"
        output_path = os.path.join(input_folder, output_filename)

        base_image = Image.open(self.input_image_path)
        stamp = Image.open(self.stamp_image_path)

        if stamp.mode != 'RGBA':
            stamp = stamp.convert('RGBA')

        scale_factor = self.get_scale_factor()

        # 计算电子章在预览窗口中的实际位置
        preview_x = self.stamp_preview_position[0]
        preview_y = self.stamp_preview_position[1]

        # 将预览窗口中的坐标转换为原始图片中的坐标
        scaled_x = (preview_x - (800 - int(self.image_width * self.image_scale)) / 2) / self.image_scale
        scaled_y = (preview_y - (600 - int(self.image_height * self.image_scale)) / 2) / self.image_scale

        # 计算修正后的电子章位置，确保与预览位置一致
        stamp_width = int(stamp.width * scale_factor)
        stamp_height = int(stamp.height * scale_factor)

        # 确保比例转换
        scaled_x = scaled_x - stamp_width / 2
        scaled_y = scaled_y - stamp_height / 2

        # 计算修正后的电子章位置，确保与预览位置一致
        stamp_position = (
            round(scaled_x),
            round(scaled_y)
        )

        # 调整电子章大小，确保与预览中的比例相同
        scaled_stamp = stamp.resize((stamp_width, stamp_height), Image.LANCZOS)

        # 将电子章粘贴到图片中
        base_image.paste(scaled_stamp, stamp_position, scaled_stamp)

        base_image.save(output_path)

        self.output_label.config(text=f"生成的图片已保存到: {output_path}")
        self.update_debug_info(output_stamp_position=stamp_position)

if __name__ == "__main__":
    root = tk.Tk()
    app = StampApp(root)
    root.mainloop()
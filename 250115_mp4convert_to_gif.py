import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

def convert_to_gif(input_dir, output_dir, fps, scale_width, setpts):
    # 确保输出文件夹存在
    os.makedirs(output_dir, exist_ok=True)

    # 获取输入文件夹中所有 MP4 文件
    video_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".mp4")]

    if not video_files:
        messagebox.showinfo("信息", "输入文件夹中没有找到 MP4 文件。")
        return

    for video in video_files:
        try:
            video_path = os.path.join(input_dir, video)
            filename, _ = os.path.splitext(video)

            palette_path = os.path.join(output_dir, f"{filename}_palette.png")
            base_output_name = os.path.join(
                output_dir, f"{filename}_fps{fps}_width{scale_width}_setpts{setpts.replace('*', 'x')}"
            )

            file_index = 1
            while os.path.exists(f"{base_output_name}_{file_index}.gif"):
                file_index += 1

            output_gif = f"{base_output_name}_{file_index}.gif"

            # 生成调色板
            subprocess.run([
                "ffmpeg", "-i", video_path,
                "-vf", f"setpts={setpts},fps={fps},scale={scale_width}:-1:flags=lanczos,palettegen=max_colors=256:stats_mode=full",
                "-y", palette_path
            ], check=True)

            # 生成 GIF
            subprocess.run([
                "ffmpeg", "-i", video_path, "-i", palette_path,
                "-filter_complex", f"setpts={setpts},fps={fps},scale={scale_width}:-1:flags=lanczos,eq=saturation=0.95[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3",
                output_gif
            ], check=True)

            if os.path.exists(palette_path):
                os.remove(palette_path)

            messagebox.showinfo("完成", f"文件 {video} 处理完成，输出到 {output_gif}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("错误", f"处理文件 {video} 时发生错误：{e}")
        except Exception as e:
            messagebox.showerror("未知错误", f"未知错误：{e}")

def browse_input():
    input_dir = filedialog.askdirectory()
    input_entry.delete(0, tk.END)
    input_entry.insert(0, input_dir)

def browse_output():
    output_dir = filedialog.askdirectory()
    output_entry.delete(0, tk.END)
    output_entry.insert(0, output_dir)

def start_conversion():
    input_dir = input_entry.get()
    output_dir = output_entry.get()
    fps = fps_entry.get()
    scale_width = scale_width_entry.get()
    setpts = setpts_entry.get()

    if not input_dir or not output_dir:
        messagebox.showwarning("警告", "请确保输入和输出目录已选择。")
        return

    try:
        fps = int(fps)
        scale_width = int(scale_width)
    except ValueError:
        messagebox.showwarning("警告", "帧速率和宽度必须是整数。")
        return

    convert_to_gif(input_dir, output_dir, fps, scale_width, setpts)

# 创建主窗口
root = tk.Tk()
root.title("MP4 转 GIF")

# 输入目录
tk.Label(root, text="输入目录:").grid(row=0, column=0, padx=10, pady=10)
input_entry = tk.Entry(root, width=50)
input_entry.grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="浏览", command=browse_input).grid(row=0, column=2, padx=10, pady=10)

# 输出目录
tk.Label(root, text="输出目录:").grid(row=1, column=0, padx=10, pady=10)
output_entry = tk.Entry(root, width=50)
output_entry.grid(row=1, column=1, padx=10, pady=10)
tk.Button(root, text="浏览", command=browse_output).grid(row=1, column=2, padx=10, pady=10)

# 帧速率
tk.Label(root, text="帧速率:").grid(row=2, column=0, padx=10, pady=10)
fps_entry = tk.Entry(root)
fps_entry.grid(row=2, column=1, padx=10, pady=10)
fps_entry.insert(0, "8")  # 默认值

# GIF 宽度
tk.Label(root, text="GIF 宽度:").grid(row=3, column=0, padx=10, pady=10)
scale_width_entry = tk.Entry(root)
scale_width_entry.grid(row=3, column=1, padx=10, pady=10)
scale_width_entry.insert(0, "750")  # 默认值

# 视频加速因子
tk.Label(root, text="视频加速因子:").grid(row=4, column=0, padx=10, pady=10)
setpts_entry = tk.Entry(root)
setpts_entry.grid(row=4, column=1, padx=10, pady=10)
setpts_entry.insert(0, "1*PTS")  # 默认值

# 开始转换按钮
tk.Button(root, text="开始转换", command=start_conversion).grid(row=5, column=1, padx=10, pady=20)

# 运行主循环
root.mainloop()

import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD


def convert_to_gif(input_files, output_dir, fps, scale_width, setpts):
    os.makedirs(output_dir, exist_ok=True)

    successful_conversions = 0
    for video_path in input_files:
        if not (video_path.lower().endswith(".mp4") or video_path.lower().endswith(".mov")):
            messagebox.showwarning("警告", f"文件 {video_path} 不是 MP4 或 MOV 格式，已跳过。")
            continue

        try:
            filename = os.path.basename(video_path)
            name, _ = os.path.splitext(filename)

            palette_path = os.path.join(output_dir, f"{name}_palette.png")
            base_output_name = os.path.join(
                output_dir, f"{name}_fps{fps}_width{scale_width}_setpts{setpts.replace('*', 'x')}"
            )

            file_index = 1
            while os.path.exists(f"{base_output_name}_{file_index}.gif"):
                file_index += 1

            output_gif = f"{base_output_name}_{file_index}.gif"

            subprocess.run([
                "ffmpeg", "-i", video_path,
                "-vf", f"setpts={setpts},fps={fps},scale={scale_width}:-1:flags=lanczos,palettegen=max_colors=256:stats_mode=full",
                "-y", palette_path
            ], check=True)

            subprocess.run([
                "ffmpeg", "-i", video_path, "-i", palette_path,
                "-filter_complex", f"setpts={setpts},fps={fps},scale={scale_width}:-1:flags=lanczos,eq=saturation=0.95[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3",
                output_gif
            ], check=True)

            if os.path.exists(palette_path):
                os.remove(palette_path)

            successful_conversions += 1
        except subprocess.CalledProcessError as e:
            messagebox.showerror("错误", f"处理文件 {filename} 时发生错误：{e}")
        except Exception as e:
            messagebox.showerror("未知错误", f"未知错误：{e}")

    if successful_conversions > 0:
        messagebox.showinfo("完成", f"成功转换 {successful_conversions} 个文件。")
    else:
        messagebox.showinfo("完成", "没有成功转换任何文件。")


def browse_output():
    output_dir = filedialog.askdirectory()
    output_entry.delete(0, tk.END)
    output_entry.insert(0, output_dir)


def start_conversion():
    output_dir = output_entry.get()
    fps = fps_entry.get()
    scale_width = scale_width_entry.get()
    setpts = setpts_entry.get()

    if not input_files:
        messagebox.showwarning("警告", "请拖放 MP4 或 MOV 文件进行转换。")
        return

    if not output_dir:
        messagebox.showwarning("警告", "请确保输出目录已选择。")
        return

    try:
        fps = int(fps)
        scale_width = int(scale_width)
    except ValueError:
        messagebox.showwarning("警告", "帧速率和宽度必须是整数。")
        return

    convert_to_gif(input_files, output_dir, fps, scale_width, setpts)


def drop(event):
    global input_files
    input_files.extend(event.data.split())
    file_list.delete(0, tk.END)
    for file in input_files:
        file_list.insert(tk.END, file)


def clear_list():
    global input_files
    input_files = []
    file_list.delete(0, tk.END)


def delete_selected():
    global input_files
    selected_indices = file_list.curselection()
    for index in reversed(selected_indices):
        del input_files[index]
        file_list.delete(index)


# 创建主窗口
root = TkinterDnD.Tk()
root.title("MP4/MOV 转 GIF")

# 文件列表和操作按钮
file_frame = tk.Frame(root)
file_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

file_list = tk.Listbox(file_frame, width=50, height=10)
file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

file_scroll = tk.Scrollbar(file_frame, orient=tk.VERTICAL, command=file_list.yview)
file_scroll.pack(side=tk.RIGHT, fill=tk.Y)
file_list.config(yscrollcommand=file_scroll.set)

file_list.drop_target_register(DND_FILES)
file_list.dnd_bind('<<Drop>>', drop)

operation_frame = tk.Frame(root)
operation_frame.grid(row=1, column=0, columnspan=3, pady=10)

tk.Button(operation_frame, text="清空列表", command=clear_list).pack(side=tk.LEFT, padx=5)
tk.Button(operation_frame, text="删除选中文件", command=delete_selected).pack(side=tk.LEFT, padx=5)

# 输出目录
output_frame = tk.Frame(root)
output_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

tk.Label(output_frame, text="输出目录:").pack(side=tk.LEFT, padx=5)
output_entry = tk.Entry(output_frame, width=35)
output_entry.pack(side=tk.LEFT, padx=5)
tk.Button(output_frame, text="浏览", command=browse_output).pack(side=tk.LEFT, padx=5)

# 转换参数设置
settings_frame = tk.Frame(root)
settings_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

tk.Label(settings_frame, text="帧速率:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
fps_entry = tk.Entry(settings_frame, width=10)
fps_entry.grid(row=0, column=1, padx=5, pady=5)
fps_entry.insert(0, "8")

tk.Label(settings_frame, text="GIF 宽度:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
scale_width_entry = tk.Entry(settings_frame, width=10)
scale_width_entry.grid(row=1, column=1, padx=5, pady=5)
scale_width_entry.insert(0, "750")

tk.Label(settings_frame, text="视频加速因子:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
setpts_entry = tk.Entry(settings_frame, width=10)
setpts_entry.grid(row=2, column=1, padx=5, pady=5)
setpts_entry.insert(0, "1*PTS")

# 开始转换按钮
action_frame = tk.Frame(root)
action_frame.grid(row=4, column=0, columnspan=3, pady=20)

tk.Button(action_frame, text="开始转换", command=start_conversion, width=15).pack(side=tk.LEFT, padx=10)

# 初始化文件列表
input_files = []

# 运行主循环
root.mainloop()

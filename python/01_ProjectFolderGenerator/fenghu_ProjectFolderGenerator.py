import tkinter as tk
from tkinter import messagebox
import os
import subprocess
import datetime

# 常量定义
DEFAULT_FOLDERS = [
    "客户资料",
    "PR工程",
    "PR_out",
    "AE工程",
    "AE_out",
    "PSAi工程",
    "png",
    "gif",
    "音乐",
    "音效",
    "3D工程",
    "3D_out",
    "协作",
    "归档"
]

def create_folders():
    project_name = entry_project_name.get() or DEFAULT_PROJECT_NAME
    custom_path = entry_custom_path.get()
    parent_folder_path = os.path.join(custom_path or os.path.expanduser("~/Desktop"), 
                                     f"{datetime.datetime.now().strftime('%Y%m%d')}_{project_name}")
    
    try:
        os.makedirs(parent_folder_path)
    except FileExistsError:
        messagebox.showerror("错误", "文件夹已存在")
        return

    folder_count = 1
    for idx, (checkbox_var, entry_var, subfolder_var) in enumerate(zip(checkbox_vars, entry_vars, subfolder_vars), start=1):
        if checkbox_var.get():
            folder_name = entry_var.get() or DEFAULT_FOLDERS[idx - 1]
            folder_path = os.path.join(parent_folder_path, f"{folder_count:02d} {folder_name}")
            os.makedirs(folder_path)
            if subfolder_var.get():
                subfolders = [name for name in entry_subfolders[idx-1].get().split() if name]
                for sub_idx, subfolder in enumerate(subfolders, start=1):
                    os.makedirs(os.path.join(folder_path, f"{sub_idx:02d} {subfolder}"))
            folder_count += 1

    # 成功创建后尝试打开文件夹
    try:
        subprocess.run(["open", parent_folder_path])
    except Exception as e:
        messagebox.showerror("错误", f"无法打开文件夹: {e}")

app = tk.Tk()
app.title("高级文件夹创建工具")

tk.Label(app, text="请输入项目名称:").grid(row=0, column=0, padx=10, pady=5)
entry_project_name = tk.Entry(app)
entry_project_name.grid(row=0, column=1, padx=10, pady=5)

checkbox_vars = []
entry_vars = []
subfolder_vars = []
entry_subfolders = []

# 初始化复选框变量，为特定项设置默认未选中状态
for idx, folder_name in enumerate(DEFAULT_FOLDERS, start=1):
    checkbox_var = tk.BooleanVar(value=(folder_name not in ["png", "gif", "3D工程", "3D_out"]))
    checkbox_vars.append(checkbox_var)
    entry_var = tk.Entry(app)
    entry_var.insert(0, folder_name)
    entry_vars.append(entry_var)
    subfolder_var = tk.BooleanVar()
    subfolder_vars.append(subfolder_var)
    entry_subfolder = tk.Entry(app)
    entry_subfolders.append(entry_subfolder)
# text=folder_name改为“”，可以实现标签为空
    tk.Checkbutton(app, text="", variable=checkbox_var).grid(row=idx, column=0, padx=10, pady=5)
    entry_var.grid(row=idx, column=1, padx=10, pady=5)
    tk.Checkbutton(app, text="包含子文件夹", variable=subfolder_var).grid(row=idx, column=2, padx=10, pady=5)
    entry_subfolder.grid(row=idx, column=3, padx=10, pady=5)

tk.Label(app, text="指定文件夹路径 (可选):").grid(row=len(DEFAULT_FOLDERS)+1, column=0, padx=10, pady=5)
entry_custom_path = tk.Entry(app)
entry_custom_path.grid(row=len(DEFAULT_FOLDERS)+1, column=1, columnspan=3, padx=10, pady=5)

tk.Button(app, text="创建文件夹目录", command=create_folders).grid(row=len(DEFAULT_FOLDERS)+2, column=0, columnspan=4, padx=10, pady=20)

app.mainloop()
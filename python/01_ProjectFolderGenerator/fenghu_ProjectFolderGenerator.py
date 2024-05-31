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
DEFAULT_PROJECT_NAME = "默认项目名称"  # 定义默认项目名称
CURRENT_MONTH_PATH = f"/Volumes/2024/{datetime.datetime.now().strftime('%m')}"

def ensure_monthly_directory_exists(monthly_path):
    """确保月份文件夹存在，如果不存在则创建"""
    if not os.path.exists(monthly_path):
        try:
            os.makedirs(monthly_path)
        except OSError as e:
            messagebox.showerror("错误", f"创建月份文件夹失败: {e}")

def create_folders():
    project_name = entry_project_name.get() or DEFAULT_PROJECT_NAME
    date_prefix = datetime.datetime.now().strftime('%y%m%d') + '_'
    project_name_with_date = date_prefix + project_name
    custom_path = entry_custom_path.get()  # 获取用户输入的路径
    if not custom_path:  # 如果用户未输入，则使用默认路径
        custom_path = CURRENT_MONTH_PATH
    ensure_monthly_directory_exists(custom_path)  # 确保路径存在
    # 不再需要重新设置entry_custom_path的值，允许用户自定义
    
    parent_folder_path = os.path.join(custom_path, project_name_with_date)
    
    try:
        os.makedirs(parent_folder_path)
    except FileExistsError:
        messagebox.showerror("错误", "项目文件夹已存在")
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
    if auto_open_var.get():
        try:
            if os.name == 'nt':
                os.startfile(parent_folder_path)
            else:
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

# 初始化复选框、输入框等组件...
for idx, folder_name in enumerate(DEFAULT_FOLDERS, start=1):
    checkbox_var = tk.BooleanVar(value=(folder_name not in ["png", "gif", "3D工程", "3D_out"]))
    checkbox_vars.append(checkbox_var)
    entry_var = tk.Entry(app)
    entry_var.insert(0, folder_name)
    entry_vars.append(entry_var)
    # 根据文件夹名称决定子文件夹复选框的默认值
    subfolder_default = folder_name in ["客户资料", "PR工程", "PR_out", "AE工程", "AE_out", "3D工程", "3D_out"]
    subfolder_var = tk.BooleanVar(value=subfolder_default)
    subfolder_vars.append(subfolder_var)
    entry_subfolder = tk.Entry(app)
    entry_subfolders.append(entry_subfolder)
    tk.Checkbutton(app, text="", variable=checkbox_var).grid(row=idx, column=0, padx=10, pady=5)
    entry_var.grid(row=idx, column=1, padx=10, pady=5)
    tk.Checkbutton(app, text="包含子文件夹", variable=subfolder_var).grid(row=idx, column=2, padx=10, pady=5)
    entry_subfolder.grid(row=idx, column=3, padx=10, pady=5)

tk.Label(app, text="指定文件夹路径 (可选):").grid(row=len(DEFAULT_FOLDERS)+1, column=0, padx=10, pady=5)
entry_custom_path = tk.Entry(app)
entry_custom_path.grid(row=len(DEFAULT_FOLDERS)+1, column=1, columnspan=3, padx=10, pady=5)

auto_open_var = tk.BooleanVar(value=True)
tk.Checkbutton(app, text="创建后自动打开文件夹", variable=auto_open_var).grid(row=len(DEFAULT_FOLDERS)+2, column=0, columnspan=4, padx=10, pady=20)

tk.Button(app, text="创建文件夹目录", command=create_folders).grid(row=len(DEFAULT_FOLDERS)+3, column=0, columnspan=4, padx=10, pady=20)

# 程序启动时设置默认路径
ensure_monthly_directory_exists(CURRENT_MONTH_PATH)
entry_custom_path.insert(0, CURRENT_MONTH_PATH)  # 设置默认路径

app.mainloop()
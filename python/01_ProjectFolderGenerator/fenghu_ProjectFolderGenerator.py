import tkinter as tk
from tkinter import messagebox, filedialog
import os
import subprocess
import datetime
import configparser
import platform
from tkinter import simpledialog



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
DEFAULT_PROJECT_NAME = ""

# 检查操作系统类型并设置 CURRENT_MONTH_PATH
if platform.system() == "Windows":
    CURRENT_MONTH_PATH = f"\\\\fenghu\\2024\\{datetime.datetime.now().strftime('%m')}"
else:
    CURRENT_MONTH_PATH = f"/Volumes/2024/{datetime.datetime.now().strftime('%m')}"

CONFIG_DIR = os.path.join(os.path.expanduser('~'), 'fenghuini')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'folder_settings.ini')  # 将配置文件存储在用户主目录中的 fenghuini 文件夹里

# 确保配置目录存在
os.makedirs(CONFIG_DIR, exist_ok=True)

# 打印配置文件路径
print(f"Config file path: {CONFIG_FILE}")

# 初始化配置文件
config = configparser.ConfigParser()

def save_as_preset():
    # 获取用户输入的预设名称
    preset_name = simpledialog.askstring("另存预设", "请输入预设名称:")
    if not preset_name:
        return

    # 创建一个新的配置文件，文件名为 preset_name.ini
    preset_file = os.path.join(CONFIG_DIR, f'{preset_name}.ini')

    # 将当前设置保存到新配置文件
    if 'folders' not in config:
        config['folders'] = {}
    if 'subfolders' not in config:
        config['subfolders'] = {}
    if 'folder_names' not in config:
        config['folder_names'] = {}
    if 'subfolders_names' not in config:
        config['subfolders_names'] = {}
    if 'custom_path' not in config:
        config['custom_path'] = {}

    for idx, folder_name in enumerate(DEFAULT_FOLDERS):
        config['folders'][folder_name] = str(checkbox_vars[idx].get())
        config['subfolders'][folder_name] = str(subfolder_vars[idx].get())
        config['folder_names'][folder_name] = entry_vars[idx].get()
        config['subfolders_names'][folder_name] = entry_subfolders[idx].get()

    config['custom_path']['path'] = entry_custom_path.get()

    with open(preset_file, 'w') as configfile:
        config.write(configfile)

    # messagebox.showinfo("保存预设", f"预设 '{preset_name}' 已保存。")

def load_preset():
    # 获取所有预设文件
    preset_files = [f for f in os.listdir(CONFIG_DIR) if f.endswith('.ini')]
    if not preset_files:
        messagebox.showwarning("加载预设", "没有找到任何预设文件。")
        return

    # 弹出对话框供用户选择预设
    preset_name = simpledialog.askstring("加载预设", "请输入预设名称:", initialvalue=preset_files[0])
    if not preset_name:
        return

    preset_file = os.path.join(CONFIG_DIR, f'{preset_name}.ini')
    if not os.path.exists(preset_file):
        messagebox.showwarning("加载预设", f"预设 '{preset_name}' 不存在。")
        return

    # 读取并加载预设文件
    config.read(preset_file)

    for idx, folder_name in enumerate(DEFAULT_FOLDERS):
        checkbox_vars[idx].set(config.getboolean('folders', folder_name, fallback=False))
        subfolder_vars[idx].set(config.getboolean('subfolders', folder_name, fallback=False))
        entry_vars[idx].delete(0, tk.END)
        entry_vars[idx].insert(0, config.get('folder_names', folder_name, fallback=folder_name))
        entry_subfolders[idx].delete(0, tk.END)
        entry_subfolders[idx].insert(0, config.get('subfolders_names', folder_name, fallback=''))

    entry_custom_path.delete(0, tk.END)
    entry_custom_path.insert(0, config.get('custom_path', 'path', fallback=''))

    # 在文本框中显示预设名称
    preset_name_display.config(state='normal')
    preset_name_display.delete(0, tk.END)
    preset_name_display.insert(0, preset_name)
    preset_name_display.config(state='readonly')

    # messagebox.showinfo("加载预设", f"预设 '{preset_name}' 已加载。")
def ensure_monthly_directory_exists(monthly_path):
    """确保月份文件夹存在，如果不存在则创建"""
    if not os.path.exists(monthly_path):
        try:
            os.makedirs(monthly_path)
        except OSError as e:
            messagebox.showerror("错误", f"创建月份文件夹失败: {e}")

def load_settings():
    """加载配置文件中的设置"""
    # 检查是否存在预设配置文件
    preset_file1 = os.path.join(CONFIG_DIR, 'preset_without_path.ini')
    preset_file2 = os.path.join(CONFIG_DIR, 'preset_with_path.ini')
    if os.path.exists(preset_file1):
        config.read(preset_file1)
        preset_name1 = config.get('preset_name', 'name', fallback="预设1")
        btn_save_load_preset1.config(text=f"加载{preset_name1}预设")
    else:
        btn_save_load_preset1.config(text="保存预设1（无路径）")
    
    if os.path.exists(preset_file2):
        config.read(preset_file2)
        preset_name2 = config.get('preset_name', 'name', fallback="预设2")
        btn_save_load_preset2.config(text=f"加载{preset_name2}预设")
    else:
        btn_save_load_preset2.config(text="保存预设2（含路径）")

    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        auto_open = config.getboolean('settings', 'auto_open', fallback=True)
        auto_open_var.set(auto_open)

        for idx, folder_name in enumerate(DEFAULT_FOLDERS, start=1):
            checkbox_vars[idx - 1].set(config.getboolean('folders', folder_name, fallback=False))
            subfolder_vars[idx - 1].set(config.getboolean('subfolders', folder_name, fallback=False))
            entry_vars[idx - 1].delete(0, tk.END)
            entry_vars[idx - 1].insert(0, config.get('folder_names', folder_name, fallback=folder_name))
            entry_subfolders[idx - 1].delete(0, tk.END)
            entry_subfolders[idx - 1].insert(0, config.get('subfolders_names', folder_name, fallback=''))
def save_settings():
    """保存当前设置到配置文件"""
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)

    if 'settings' not in config:
        config['settings'] = {}
    if 'folders' not in config:
        config['folders'] = {}
    if 'subfolders' not in config:
        config['subfolders'] = {}
    if 'folder_names' not in config:
        config['folder_names'] = {}
    if 'subfolders_names' not in config:
        config['subfolders_names'] = {}

    config['settings']['auto_open'] = str(auto_open_var.get())

    for idx, folder_name in enumerate(DEFAULT_FOLDERS):
        config['folders'][folder_name] = str(checkbox_vars[idx].get())
        config['subfolders'][folder_name] = str(subfolder_vars[idx].get())
        config['folder_names'][folder_name] = entry_vars[idx].get()
        config['subfolders_names'][folder_name] = entry_subfolders[idx].get()

    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

def reset_to_defaults():
    """重置设置为默认值"""
    entry_project_name.delete(0, tk.END)
    entry_project_name.insert(0, DEFAULT_PROJECT_NAME)
    entry_custom_path.delete(0, tk.END)
    entry_custom_path.insert(0, CURRENT_MONTH_PATH)
    auto_open_var.set(True)

    for idx, folder_name in enumerate(DEFAULT_FOLDERS, start=1):
        checkbox_vars[idx - 1].set(folder_name not in ["png", "gif", "3D工程", "3D_out"])
        subfolder_default = folder_name in ["客户资料", "PR工程", "PR_out", "AE工程", "AE_out", "3D工程", "3D_out"]
        subfolder_vars[idx - 1].set(subfolder_default)
        entry_vars[idx - 1].delete(0, tk.END)
        entry_vars[idx - 1].insert(0, folder_name)
        entry_subfolders[idx - 1].delete(0, tk.END)

def create_folders():
    project_name = entry_project_name.get() or DEFAULT_PROJECT_NAME
    date_prefix = datetime.datetime.now().strftime('%y%m%d') + '_'
    project_name_with_date = date_prefix + project_name
    custom_path = entry_custom_path.get() or CURRENT_MONTH_PATH  # 获取用户输入的路径
    ensure_monthly_directory_exists(custom_path)  # 确保路径存在
    
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

    save_settings()  # 创建文件夹后保存设置

    # 成功创建后尝试打开文件夹
    if auto_open_var.get():
        try:
            if os.name == 'nt':
                os.startfile(parent_folder_path)
            else:
                subprocess.run(["open", parent_folder_path])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件夹: {e}")

def handle_preset(include_path, event=None):
    if include_path:
        preset_file = os.path.join(CONFIG_DIR, 'preset_with_path.ini')
        button = btn_save_load_preset2
    else:
        preset_file = os.path.join(CONFIG_DIR, 'preset_without_path.ini')
        button = btn_save_load_preset1

    if os.path.exists(preset_file):
        load_preset(include_path)
    else:
        preset_name = simpledialog.askstring("保存预设", "请输入预设名称:")
        if preset_name:
            save_preset(include_path, preset_name)
            button.config(text=f"加载{preset_name}预设")

def save_preset(include_path, preset_name):
    preset_file = os.path.join(CONFIG_DIR, 'preset_with_path.ini' if include_path else 'preset_without_path.ini')
    if os.path.exists(preset_file):
        config.read(preset_file)

    if 'folders' not in config:
        config['folders'] = {}
    if 'subfolders' not in config:
        config['subfolders'] = {}
    if 'folder_names' not in config:
        config['folder_names'] = {}
    if 'subfolders_names' not in config:
        config['subfolders_names'] = {}
    if include_path and 'custom_path' not in config:
        config['custom_path'] = {}

    for idx, folder_name in enumerate(DEFAULT_FOLDERS):
        config['folders'][folder_name] = str(checkbox_vars[idx].get())
        config['subfolders'][folder_name] = str(subfolder_vars[idx].get())
        config['folder_names'][folder_name] = entry_vars[idx].get()
        config['subfolders_names'][folder_name] = entry_subfolders[idx].get()

    if include_path:
        config['custom_path']['path'] = entry_custom_path.get()

    # 保存按钮文本
    if 'preset_name' not in config:
        config['preset_name'] = {}
    config['preset_name']['name'] = preset_name

    with open(preset_file, 'w') as configfile:
        config.write(configfile)
    
    # 更新按钮文本
    if include_path:
        btn_save_load_preset2.config(text=f"加载{preset_name}预设")
    else:
        btn_save_load_preset1.config(text=f"加载{preset_name}预设")

def load_preset():
    # 获取所有预设文件
    preset_files = [f for f in os.listdir(CONFIG_DIR) if f.endswith('.ini')]
    if not preset_files:
        messagebox.showwarning("加载预设", "没有找到任何预设文件。")
        return

    # 弹出选择框供用户选择预设文件
    chosen_file = filedialog.askopenfilename(initialdir=CONFIG_DIR, title="选择预设文件",
                                             filetypes=(("INI files", "*.ini"), ("All files", "*.*")))
    if not chosen_file:
        return

    preset_name = os.path.splitext(os.path.basename(chosen_file))[0]

    if not preset_name:
        messagebox.showwarning("加载预设", "请选择一个有效的预设文件。")
        return

    preset_file = os.path.join(CONFIG_DIR, f'{preset_name}.ini')
    if not os.path.exists(preset_file):
        messagebox.showwarning("加载预设", f"预设 '{preset_name}' 不存在。")
        return

    # 读取并加载预设文件
    config.read(preset_file)

    for idx, folder_name in enumerate(DEFAULT_FOLDERS):
        checkbox_vars[idx].set(config.getboolean('folders', folder_name, fallback=False))
        subfolder_vars[idx].set(config.getboolean('subfolders', folder_name, fallback=False))
        entry_vars[idx].delete(0, tk.END)
        entry_vars[idx].insert(0, config.get('folder_names', folder_name, fallback=folder_name))
        entry_subfolders[idx].delete(0, tk.END)
        entry_subfolders[idx].insert(0, config.get('subfolders_names', folder_name, fallback=''))

    entry_custom_path.delete(0, tk.END)
    entry_custom_path.insert(0, config.get('custom_path', 'path', fallback=''))

    # 在文本框中显示预设名称
    preset_name_display.config(state='normal')
    preset_name_display.delete(0, tk.END)
    preset_name_display.insert(0, preset_name)
    preset_name_display.config(state='readonly')

    messagebox.showinfo("加载预设", f"预设 '{preset_name}' 已加载。")
def delete_preset(include_path):
    preset_file = os.path.join(CONFIG_DIR, 'preset_with_path.ini' if include_path else 'preset_without_path.ini')
    if os.path.exists(preset_file):
        os.remove(preset_file)
    if include_path:
        btn_save_load_preset2.config(text="保存预设2（含路径）")
    else:
        btn_save_load_preset1.config(text="保存预设1（无路径）")

def select_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry_custom_path.delete(0, tk.END)
        entry_custom_path.insert(0, folder_selected)

app = tk.Tk()
app.title("风乎-文件夹创建助手V1.0")

# 项目名称和路径选择部分
frame_top = tk.Frame(app)
frame_top.pack(fill=tk.X, padx=10, pady=10)

tk.Label(frame_top, text="请输入项目名称:").grid(row=0, column=0, padx=5, pady=5)
entry_project_name = tk.Entry(frame_top)
entry_project_name.grid(row=0, column=1, padx=5, pady=5)
entry_project_name.insert(0, DEFAULT_PROJECT_NAME)  # 设置默认项目名称

tk.Label(frame_top, text="指定文件夹路径 (可选):").grid(row=1, column=0, padx=5, pady=5)
entry_custom_path = tk.Entry(frame_top)
entry_custom_path.grid(row=1, column=1, padx=5, pady=5)
entry_custom_path.insert(0, CURRENT_MONTH_PATH)  # 设置默认路径

btn_select_path = tk.Button(frame_top, text="选择路径", command=select_folder)
btn_select_path.grid(row=1, column=2, padx=5, pady=5)

btn_reset_path = tk.Button(frame_top, text="恢复默认路径", command=lambda: entry_custom_path.delete(0, tk.END) or entry_custom_path.insert(0, CURRENT_MONTH_PATH))
btn_reset_path.grid(row=1, column=3, padx=5, pady=5)

# 文件夹和子文件夹选项部分
frame_middle = tk.Frame(app)
frame_middle.pack(fill=tk.X, padx=10, pady=10)

checkbox_vars = []
entry_vars = []
subfolder_vars = []
entry_subfolders = []

for idx, folder_name in enumerate(DEFAULT_FOLDERS, start=1):
    checkbox_var = tk.BooleanVar(value=(folder_name not in ["png", "gif", "3D工程", "3D_out"]))
    checkbox_vars.append(checkbox_var)
    entry_var = tk.Entry(frame_middle)
    entry_var.insert(0, folder_name)
    entry_vars.append(entry_var)
    subfolder_default = folder_name in ["客户资料", "PR工程", "PR_out", "AE工程", "AE_out", "3D工程", "3D_out"]
    subfolder_var = tk.BooleanVar(value=subfolder_default)
    subfolder_vars.append(subfolder_var)
    entry_subfolder = tk.Entry(frame_middle)
    entry_subfolders.append(entry_subfolder)
    
    tk.Checkbutton(frame_middle, text="", variable=checkbox_var).grid(row=idx, column=0, padx=5, pady=5)
    entry_var.grid(row=idx, column=1, padx=5, pady=5)
    tk.Checkbutton(frame_middle, text="Sub-folder", variable=subfolder_var).grid(row=idx, column=2, padx=5, pady=5)
    entry_subfolder.grid(row=idx, column=3, padx=5, pady=5)


# 操作按钮部分
frame_bottom = tk.Frame(app)
frame_bottom.pack(fill=tk.X, padx=10, pady=10)
# 创建文件夹目录 按钮较大，创建后自动打开文件夹 放右边
frame_create_open = tk.Frame(frame_bottom)
frame_create_open.pack(fill=tk.X, padx=5, pady=5)

btn_create = tk.Button(frame_create_open, text="创建文件夹目录", command=create_folders, height=2, width=20)
btn_create.pack(side=tk.LEFT, padx=5, pady=10)

auto_open_var = tk.BooleanVar(value=True)
tk.Checkbutton(frame_create_open, text="创建后自动打开文件夹", variable=auto_open_var).pack(side=tk.LEFT, padx=5, pady=10)

# 恢复默认参数 单独一行左对齐
btn_reset_width = 20  # 固定按钮宽度为20个字符的宽度
btn_reset = tk.Button(frame_bottom, text="恢复默认参数", command=reset_to_defaults, width=btn_reset_width)
btn_reset.pack(side=tk.TOP, padx=5, pady=10, anchor="w")

# 保存预设1 和 删除预设1
frame_preset1 = tk.Frame(frame_bottom)
frame_preset1.pack(fill=tk.X, padx=5, pady=5)

btn_save_load_preset1 = tk.Button(frame_preset1, text="保存预设1（无路径）", command=lambda: handle_preset(False), width=20)
btn_save_load_preset1.pack(side=tk.LEFT, padx=5, pady=10)

btn_delete_preset1 = tk.Button(frame_preset1, text="删除预设1", command=lambda: delete_preset(False), width=20)
btn_delete_preset1.pack(side=tk.LEFT, padx=5, pady=10)

# 保存预设2 和 删除预设2
frame_preset2 = tk.Frame(frame_bottom)
frame_preset2.pack(fill=tk.X, padx=5, pady=5)

btn_save_load_preset2 = tk.Button(frame_preset2, text="保存预设2（含路径）", command=lambda: handle_preset(True), width=20)
btn_save_load_preset2.pack(side=tk.LEFT, padx=5, pady=10)

btn_delete_preset2 = tk.Button(frame_preset2, text="删除预设2", command=lambda: delete_preset(True), width=20)
btn_delete_preset2.pack(side=tk.LEFT, padx=5, pady=10)


# 在 frame_bottom 内调整布局
frame_preset_actions = tk.Frame(frame_bottom)
frame_preset_actions.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

# 添加另存预设按钮，单独一行，居左对齐
btn_save_as_preset = tk.Button(frame_preset_actions, text="另存预设", command=save_as_preset, width=20)
btn_save_as_preset.pack(side=tk.LEFT, padx=5, pady=5)

# 添加加载预设按钮和文本框，放在下一行，居左对齐
frame_load_preset = tk.Frame(frame_bottom)
frame_load_preset.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

btn_load_preset = tk.Button(frame_load_preset, text="加载预设", command=load_preset, width=20)
btn_load_preset.pack(side=tk.LEFT, padx=5, pady=5)

preset_name_display = tk.Entry(frame_load_preset, state='readonly', width=20)  # 调整文本框大小
preset_name_display.pack(side=tk.LEFT, padx=5, pady=5)


# 程序启动时设置默认路径并加载设置
ensure_monthly_directory_exists(CURRENT_MONTH_PATH)
load_settings()

app.mainloop()
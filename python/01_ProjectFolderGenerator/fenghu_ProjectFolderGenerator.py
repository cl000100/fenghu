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
    "拍摄素材",
    "PR工程",
    "PR_out",
    "AE工程",
    "AE_out",
    "平面工程",
    "png",
    "gif_out",
    "音乐",
    "音效",
    "3D工程",
    "3D_out",
    "协作",
    "归档"
]


# 需要创建子文件夹的文件夹名称
SUBFOLDER_FOLDERS = {
    "客户资料","PR工程", "PR_out", "AE工程", "AE_out",
    "3D工程", "3D_out"
}

# 需要选中的文件夹名称
SELECTED_FOLDERS = {
    "客户资料","PR工程", "PR_out", "AE工程", "AE_out",
    "平面工程", "音乐", "音效", "协作", "归档"
}

# 初始化变量列表
checkbox_vars = []
entry_vars = []
subfolder_vars = []
entry_subfolders = []
DEFAULT_PROJECT_NAME = ""

# # 检查操作系统类型并设置 CURRENT_MONTH_PATH
# if platform.system() == "Windows":
#     CURRENT_MONTH_PATH = f"\\\\fenghu\\2025\\{datetime.datetime.now().strftime('%m')}"
# else:
# #    CURRENT_MONTH_PATH = f"/Users/chenglei/Desktop/2025/{datetime.datetime.now().strftime('%m')}"
#     CURRENT_MONTH_PATH = f"/Volumes/2025/{datetime.datetime.now().strftime('%m')}"

# 检查操作系统类型并设置 CURRENT_MONTH_PATH
current_year = datetime.datetime.now().year
if platform.system() == "Windows":
    CURRENT_MONTH_PATH = f"\\\\fenghu\\{current_year}\\{datetime.datetime.now().strftime('%m')}"
else:
#    CURRENT_MONTH_PATH = f"/Users/chenglei/Desktop/{current_year}/{datetime.datetime.now().strftime('%m')}"
    CURRENT_MONTH_PATH = f"/Volumes/{current_year}/{datetime.datetime.now().strftime('%m')}"

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

    # 新增逻辑以读取并更新预设按钮的文本
    for preset_key, button, default_text in [
        ('preset_with_path.ini', btn_save_load_preset2, "保存预设2（含路径）"),
        ('preset_without_path.ini', btn_save_load_preset1, "保存预设1（无路径）")
    ]:
        preset_file = os.path.join(CONFIG_DIR, preset_key)
        if os.path.exists(preset_file):
            config.read(preset_file)
            preset_name = config.get('preset_name', 'name', fallback="")
            button.config(text=f"加载{preset_name}预设" if preset_name else default_text)
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

    for idx, folder_name in enumerate(DEFAULT_FOLDERS):
        is_selected = folder_name in SELECTED_FOLDERS
        checkbox_vars[idx].set(is_selected)

        subfolder_default = folder_name in SUBFOLDER_FOLDERS
        subfolder_vars[idx].set(subfolder_default)

        entry_vars[idx].delete(0, tk.END)
        entry_vars[idx].insert(0, folder_name)
        entry_subfolders[idx].delete(0, tk.END)

    # 清空 preset_name_display 文本框的值
    preset_name_display.config(state='normal')
    preset_name_display.delete(0, tk.END)
    preset_name_display.config(state='readonly')
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
# 保存预设1和预设2的处理函数
def handle_preset(include_path, event=None):
    preset_file = os.path.join(CONFIG_DIR, 'preset_with_path.ini' if include_path else 'preset_without_path.ini')
    if os.path.exists(preset_file):
        load_preset_from_file(preset_file)
    else:
        save_preset(include_path)

def save_preset(include_path):
    preset_name = simpledialog.askstring("输入预设名称", "请输入预设的名称:")
    if not preset_name:
        return

    preset_file = os.path.join(CONFIG_DIR, 'preset_with_path.ini' if include_path else 'preset_without_path.ini')

    config.read(preset_file)
    
    # 确保 'preset_name' section 存在
    if 'preset_name' not in config:
        config.add_section('preset_name')
    
    config.set('preset_name', 'name', preset_name)  # 写入预设名称到配置文件



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

    with open(preset_file, 'w') as configfile:
        config.write(configfile)

    if include_path:
        btn_save_load_preset2.config(text=f"加载{preset_name}预设")
    else:
        btn_save_load_preset1.config(text=f"加载{preset_name}预设")

   # 设置 preset_name_display 文本框的值.这个感觉可加可不加。

    preset_name_display.config(state='normal')
    preset_name_display.delete(0, tk.END)
    preset_name_display.insert(0, preset_name)
    preset_name_display.config(state='readonly')
def load_preset_from_file(preset_file):
    """从文件加载预设"""
    if os.path.exists(preset_file):
        config.read(preset_file)
        for idx, folder_name in enumerate(DEFAULT_FOLDERS, start=1):
            checkbox_vars[idx - 1].set(config.getboolean('folders', folder_name, fallback=False))
            subfolder_vars[idx - 1].set(config.getboolean('subfolders', folder_name, fallback=False))
            entry_vars[idx - 1].delete(0, tk.END)
            entry_vars[idx - 1].insert(0, config.get('folder_names', folder_name, fallback=folder_name))
            entry_subfolders[idx - 1].delete(0, tk.END)
            entry_subfolders[idx - 1].insert(0, config.get('subfolders_names', folder_name, fallback=''))

        if 'custom_path' in config:
            entry_custom_path.delete(0, tk.END)
            entry_custom_path.insert(0, config.get('custom_path', 'path', fallback=CURRENT_MONTH_PATH))
        
        # 设置 preset_name_display 文本框的值
        preset_name_display.config(state='normal')
        preset_name_display.delete(0, tk.END)
        preset_name_display.insert(0, os.path.basename(preset_file))
        preset_name_display.config(state='readonly')

# 将原来的 load_preset 函数内容改名为 load_preset_from_file 函数，然后调用它
def load_preset():
    preset_file = filedialog.askopenfilename(initialdir=CONFIG_DIR, title="选择预设文件",
                                             filetypes=(("INI files", "*.ini"), ("All files", "*.*")))
    if preset_file:
        load_preset_from_file(preset_file)

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

def clear_all_content():
    # 清空复选框状态
    for var in checkbox_vars:
        var.set(False)
    for subfolder_var in subfolder_vars:
        subfolder_var.set(False)
    # 清空文本框内容
    for entry in entry_vars:
        entry.delete(0, tk.END)
    for entry_subfolder in entry_subfolders:
        entry_subfolder.delete(0, tk.END)
    entry_project_name.delete(0, tk.END)
    entry_custom_path.delete(0, tk.END)
    preset_name_display.delete(0, tk.END)
    # 清空显示已加载的预设名称的文本框
    preset_name_display.config(state='normal')
    preset_name_display.delete(0, tk.END)
    preset_name_display.config(state='readonly')


app = tk.Tk()
app.title("风乎-文件夹创建助手V1.0")

# 项目名称和路径选择部分
frame_top = tk.Frame(app)
frame_top.pack(fill=tk.X, padx=10, pady=5)

tk.Label(frame_top, text="请输入项目名称:").grid(row=0, column=0, padx=5, pady=5)
entry_project_name = tk.Entry(frame_top)
entry_project_name.grid(row=0, column=1, padx=5, pady=5)
entry_project_name.insert(0, DEFAULT_PROJECT_NAME)  # 设置默认项目名称

tk.Label(frame_top, text="指定文件夹路径:").grid(row=1, column=0, padx=5, pady=5)
entry_custom_path = tk.Entry(frame_top)
entry_custom_path.grid(row=1, column=1, padx=5, pady=5)
entry_custom_path.insert(0, CURRENT_MONTH_PATH)  # 设置默认路径

btn_select_path = tk.Button(frame_top, text="选择路径", command=select_folder)
btn_select_path.grid(row=1, column=2, padx=5, pady=5)

btn_reset_path = tk.Button(frame_top, text="恢复默认路径", command=lambda: entry_custom_path.delete(0, tk.END) or entry_custom_path.insert(0, CURRENT_MONTH_PATH))
btn_reset_path.grid(row=1, column=3, padx=5, pady=5)

# 文件夹和子文件夹选项部分
frame_middle = tk.Frame(app)
frame_middle.pack(fill=tk.X, padx=10, pady=5)

checkbox_vars = []
entry_vars = []
subfolder_vars = []
entry_subfolders = []

# 创建复选框和输入框
for idx, folder_name in enumerate(DEFAULT_FOLDERS, start=1):
    is_selected = folder_name in SELECTED_FOLDERS
    checkbox_var = tk.BooleanVar(value=is_selected)
    checkbox_vars.append(checkbox_var)

    entry_var = tk.Entry(frame_middle)
    entry_var.insert(0, folder_name)
    entry_vars.append(entry_var)

    subfolder_default = folder_name in SUBFOLDER_FOLDERS
    subfolder_var = tk.BooleanVar(value=subfolder_default)
    subfolder_vars.append(subfolder_var)

    entry_subfolder = tk.Entry(frame_middle)
    entry_subfolders.append(entry_subfolder)
    
    # 将组件添加到网格布局
    tk.Checkbutton(frame_middle, text="", variable=checkbox_var).grid(row=idx, column=0, padx=5, pady=5)
    entry_var.grid(row=idx, column=1, padx=5, pady=5)
    tk.Checkbutton(frame_middle, text="Sub-folder", variable=subfolder_var).grid(row=idx, column=2, padx=5, pady=5)
    entry_subfolder.grid(row=idx, column=3, padx=5, pady=5)

# 操作按钮部分
frame_bottom = tk.Frame(app)
frame_bottom.pack(fill=tk.X, padx=10, pady=3)

# 创建文件夹目录
frame_create_open = tk.Frame(frame_bottom)
frame_create_open.pack(fill=tk.X, padx=5, pady=3)

btn_create = tk.Button(frame_create_open, text="创建文件夹目录", command=create_folders, height=2, width=20)
btn_create.pack(side=tk.LEFT, padx=5, pady=3)

auto_open_var = tk.BooleanVar(value=True)
tk.Checkbutton(frame_create_open, text="创建后自动打开文件夹", variable=auto_open_var).pack(side=tk.LEFT, padx=5, pady=3)

# 恢复默认参数 和 清空所有内容按钮
frame_reset_clear = tk.Frame(frame_bottom)
frame_reset_clear.pack(fill=tk.X, padx=5, pady=3)

btn_reset_width = 20
btn_reset = tk.Button(frame_reset_clear, text="恢复默认参数", command=reset_to_defaults, width=btn_reset_width)
btn_reset.pack(side=tk.LEFT, padx=5, pady=3)

btn_clear_all = tk.Button(frame_reset_clear, text="清空所有内容", command=clear_all_content, width=btn_reset_width)
btn_clear_all.pack(side=tk.LEFT, padx=5, pady=3)

# 保存预设1 和 删除预设1
frame_preset1 = tk.Frame(frame_bottom)
frame_preset1.pack(fill=tk.X, padx=5, pady=3)

btn_save_load_preset1 = tk.Button(frame_preset1, text="保存预设1（无路径）", command=lambda: handle_preset(False), width=btn_reset_width)
btn_save_load_preset1.pack(side=tk.LEFT, padx=5, pady=3)

btn_delete_preset1 = tk.Button(frame_preset1, text="删除预设1", command=lambda: delete_preset(False), width=btn_reset_width)
btn_delete_preset1.pack(side=tk.LEFT, padx=5, pady=3)

# 保存预设2 和 删除预设2
frame_preset2 = tk.Frame(frame_bottom)
frame_preset2.pack(fill=tk.X, padx=5, pady=3)

btn_save_load_preset2 = tk.Button(frame_preset2, text="保存预设2（含路径）", command=lambda: handle_preset(True), width=btn_reset_width)
btn_save_load_preset2.pack(side=tk.LEFT, padx=5, pady=3)

btn_delete_preset2 = tk.Button(frame_preset2, text="删除预设2", command=lambda: delete_preset(True), width=btn_reset_width)
btn_delete_preset2.pack(side=tk.LEFT, padx=5, pady=3)

# 另存预设按钮
frame_save_preset = tk.Frame(frame_bottom)
frame_save_preset.pack(fill=tk.X, padx=5, pady=3)

btn_save_as_preset = tk.Button(frame_save_preset, text="另存预设", command=save_as_preset, width=btn_reset_width)
btn_save_as_preset.pack(side=tk.LEFT, padx=5, pady=3)

# 加载预设按钮和文本框
frame_load_preset = tk.Frame(frame_bottom)
frame_load_preset.pack(fill=tk.X, padx=5, pady=3)

btn_load_preset = tk.Button(frame_load_preset, text="加载预设", command=load_preset, width=btn_reset_width)
btn_load_preset.pack(side=tk.LEFT, padx=5, pady=3)

preset_name_display = tk.Entry(frame_load_preset, state='readonly', width=btn_reset_width)
preset_name_display.pack(side=tk.LEFT, padx=5, pady=3)

# 添加空白框架，增加底部空白
frame_bottom_padding = tk.Frame(frame_bottom, height=20)
frame_bottom_padding.pack(fill=tk.X)

# 程序启动时设置默认路径并加载设置
ensure_monthly_directory_exists(CURRENT_MONTH_PATH)
load_settings()

app.mainloop()
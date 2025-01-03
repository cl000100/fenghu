import os
import re

def rename_gif_files(directory):
    # 切换到指定目录
    os.chdir(directory)

    # 更新的正则表达式，匹配文件名中的模式，允许有额外的后缀
    pattern = re.compile(r"^(.*?)(_fps\d+_width\d+_setpts[0-9.]+xPTS_\d+)(.*)\.gif$")
    
    # 获取文件列表并计算总数
    files = os.listdir(directory)
    total_files = len(files)
    processed_files = 0
    
    # 遍历目录中的所有文件
    for filename in files:
        # 输出当前检查的文件名
        print(f"Checking file: {filename}")
        
        # 检查文件是否匹配所需的格式
        match = pattern.match(filename)
        if match:
            # 提取文件前缀部分和附加的后缀部分
            prefix = match.group(1)
            suffix = match.group(3)  # 这是可能存在的额外后缀，比如 '_副本'
            
            # 生成新文件名
            # new_name = prefix + suffix + '.gif'
            new_name = prefix + '.gif'

            # 如果文件名已经存在，防止覆盖
            counter = 1
            original_new_name = new_name
            while os.path.exists(new_name):
                new_name = f"{original_new_name.split('.gif')[0]}_{counter}.gif"
                counter += 1
            
            # 打印正在处理的文件信息
            print(f"Processing file {processed_files + 1}/{total_files}: {filename} -> {new_name}")
            
            # 重命名文件
            os.rename(filename, new_name)
            print(f"Renamed: {filename} -> {new_name}")
            
        else:
            # 打印出文件未匹配的情况
            print(f"File does not match pattern: {filename}")
            
        # 增加已处理文件数
        processed_files += 1
    
    # 完成后提示
    print("Renaming process completed.")


# 示例：将路径改为你需要的文件夹路径
directory = '/Users/chenglei/Desktop/output'
rename_gif_files(directory)
#!/bin/bash

# 提示用户输入目录路径
read -p "请输入要处理的目录路径: " DIR

# 去除路径前后的空格
DIR=$(echo "$DIR" | xargs)

# 检查目录是否存在
if [ ! -d "$DIR" ]; then
    echo "目录不存在: $DIR"
    read -p "按任意键退出..."
    exit 1
else
    echo "成功读取目录: $DIR"
fi

# 遍历目录中的所有mp4文件并重命名
for file in "$DIR"/*.mp4; do
    # 检查是否有匹配的文件
    if [ -e "$file" ]; then
        mv "$file" "${file%.mp4}.m4v"
        echo "重命名: $file -> ${file%.mp4}.m4v"
    fi
done

echo "所有文件转换完成。"
read -p "按任意键退出..."
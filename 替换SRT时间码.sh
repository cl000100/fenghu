#!/bin/zsh

echo "请将要转换的文件拖入到终端中："
read file_path

if [[ -f "$file_path" ]]; then
    output_file="${file_path%.*}_converted.txt"
    
    # 使用正则表达式处理文件内容
    awk 'BEGIN{RS=""; FS="\n"} {for (i=3; i<=NF; i+=4) print $i}' "$file_path" > "$output_file"
    
    echo "转换完成，结果保存为 $output_file"
else
    echo "文件不存在，请重试。"
fi

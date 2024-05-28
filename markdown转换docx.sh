#!/bin/bash

# 提示用户将文件拖入终端
echo "请将要转换的Markdown文件拖入此终端并按回车："
read input_file

# 去掉文件名两端的空白字符
input_file=$(echo "$input_file" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

# 检查输入文件是否存在
if [ ! -f "$input_file" ]; then
  echo "错误: 输入文件 $input_file 不存在。"
  exit 1
fi

# 获取当前日期时间戳（年份后两位+月份+日期）
timestamp=$(date +"%y%m%d")

# 提取文件名和扩展名
filename=$(basename -- "$input_file")
extension="${filename##*.}"
filename="${filename%.*}"

# 设置输出文件路径
output_file=~/Desktop/"${timestamp}_${filename}.docx"
temp_file="/tmp/temp_adjusted.md"

# 去掉图片描述，只保留图片路径，并确保每张图片前后有空行
sed -E 's/!\[.*\]\(([^)]+)\)/!\[\]\(\1\)/' "$input_file" | \
sed -E 's/!\[.*\]\(.*\)/\n&\n/' > "$temp_file"

# 确保每个Markdown元素之间有空行分隔
sed -i -E ':a;N;$!ba;s/([^\n])\n([^\n])/\1\n\n\2/g' "$temp_file"

# 使用pandoc进行转换并启用样式支持
pandoc "$temp_file" -o "$output_file" --from markdown --to docx

# 检查转换是否成功
if [ $? -eq 0 ]; then
  echo "转换完成：$output_file"
  # 删除临时文件
  rm "$temp_file"
else
  echo "错误: 转换失败。"
fi
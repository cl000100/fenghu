#!/bin/bash
# -*- coding: utf-8 -*-

# 参数设置
INPUT_DIR="/Users/chenglei/Desktop/临时处理/input"
OUTPUT_DIR="/Users/chenglei/Desktop/临时处理/output"
FPS=8               # 帧速率
SCALE_WIDTH=750      # GIF 宽度（高度会根据视频的宽高比自动调整）
SETPTS="1*PTS"     # 视频加速因子

# 确保输出文件夹存在
mkdir -p "$OUTPUT_DIR"

# 遍历输入文件夹中的所有 MP4 文件
for video in "$INPUT_DIR"/*.mp4; do
  # 获取文件名（不包括路径和扩展名）
  filename=$(basename "$video" .mp4)
  
  # 生成调色板
  ffmpeg -i "$video" -vf "setpts=$SETPTS,fps=$FPS,scale=$SCALE_WIDTH:-1:flags=lanczos,palettegen=max_colors=256:stats_mode=full" -y "$OUTPUT_DIR/palette.png"
  
  # 生成 GIF 文件的基本名称
  base_output_name="$OUTPUT_DIR/${filename}_fps${FPS}_width${SCALE_WIDTH}_setpts${SETPTS//[*]/x}"
  
  # 初始化文件序号
  file_index=1
  
  # 生成文件名，并检查是否已存在，处理重复文件
  while [ -f "${base_output_name}_${file_index}.gif" ]; do
    file_index=$((file_index + 1))
  done
  
  # 完整的 GIF 文件名
  output_gif="${base_output_name}_${file_index}.gif"
  
  # 生成 GIF
  ffmpeg -i "$video" -i "$OUTPUT_DIR/palette.png" -filter_complex "setpts=$SETPTS,fps=$FPS,scale=$SCALE_WIDTH:-1:flags=lanczos,eq=saturation=0.95[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3" "$output_gif"
  
  # 删除调色板文件
  rm "$OUTPUT_DIR/palette.png"
done
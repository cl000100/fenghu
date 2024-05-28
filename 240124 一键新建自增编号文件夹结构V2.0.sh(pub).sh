#!/bin/bash
# -*- coding: utf-8 -*-

# 获取当前年份和月份
current_year=$(date +%Y)
current_month=$(date +%m)

# 获取当天日期,%y代表两位数的年份（例如，20）
current_date=$(date +%y%m%d)

# 提示用户输入内容
read -p "请输入文件夹的内容(如KFC)：" folder_content

# 路径
directory="/Volumes/2024/$current_month"

# 目标文件夹名
target_folder="$directory/$current_date $folder_content"

# 如果目标文件夹已存在，添加重命名后缀
if [ -d "$target_folder" ]; then
    suffix=1
    while [ -d "${target_folder}_重命名${suffix}" ]; do
        ((suffix++))
    done
    target_folder="${target_folder}_重命名${suffix}"
fi

# 创建文件夹
mkdir -p "$target_folder"

# 在这个文件夹中创建下面一系列新的文件夹

all_folder_names=("客户资料" "PR工程" "PR_out" "AE工程" "AE_out" "PSAi工程" "png" "gif" "音乐" "音效" "3D工程" "3D_out"  "协作"  "归档")

# 在 "AE工程"、"PR工程"、"3D工程" 文件夹中要创建的子文件夹名称
ae_pr_3d_subfolder_names=("01 程磊工程" "02 xx工程")

# 在 "Ae_out"、"PR_out"、"3D_out" 文件夹中要创建的子文件夹名称
aeout_prout_3dout_subfolder_names=("01 程磊out" "02 xxout")

index=1
created_folders=()
created_folders_index=1

while true; do
    # 让用户选择要创建的文件夹
    echo "请选择要创建的文件夹（按Ctrl+C退出）："

    # 添加 "all" 选项
    echo "0 all"

    # 过滤掉已经创建过的文件夹名称
    remaining_folders=()
    for folder_name in "${all_folder_names[@]}"; do
        if [[ ! " ${created_folders[@]} " =~ " $folder_name " ]]; then
            remaining_folders+=("$folder_name")
        fi
    done

    # 显示剩余的文件夹选项
    echo "可选文件夹："
    for ((i=0; i<${#remaining_folders[@]}; i++)); do
        echo "$((i+1)) ${remaining_folders[$i]}"
    done

    # 提示用户输入选择的文件夹序号，以空格分隔
    read -p "请输入选择的文件夹序号（以空格分隔）: " choices_input

    # 处理空格分隔的多选
    IFS=' ' read -ra selected_choices <<< "$choices_input"

    # 用于存储用户选择的文件夹名称
    selected_folders=()

    for choice in "${selected_choices[@]}"; do
        # 检查选择是否为有效数字
        if [[ $choice =~ ^[0-9]+$ ]]; then
            # 将用户选择的数字转换为索引
            index=$((choice-1))

            if [ $index -ge 0 ] && [ $index -lt ${#remaining_folders[@]} ]; then
                selected_folders+=("${remaining_folders[$index]}")
            elif [ $index -eq -1 ]; then
                # 如果选择是 "all"，则选择所有文件夹
                selected_folders=("${all_folder_names[@]}")
                break
            else
                echo "选择的数字超出范围。"
            fi
        else
            echo "请选择有效的数字。"
        fi
    done

    # 按用户选择的文件夹名称创建文件夹
    for folder_name in "${selected_folders[@]}"; do
        # 使用递增的序号作为文件夹序号
        folder_index_padded=$(printf "%02d" $created_folders_index)
        folder_path="$target_folder/$folder_index_padded $folder_name"

        # 检查目录是否已经存在
        if [ ! -d "$folder_path" ]; then
            # 创建文件夹
            mkdir "$folder_path"
            echo "创建文件夹：$folder_path"

            # 将已创建的文件夹名称加入列表
            created_folders+=("$folder_name")
            ((created_folders_index++))

            # 如果创建的是 "AE工程"、"PR工程"、"3D工程" 文件夹，再在里面创建 "A工程" 和 "B工程"
            if [[ "$folder_name" == "AE工程" || "$folder_name" == "PR工程" || "$folder_name" == "3D工程" ]]; then
                for subfolder_name in "${ae_pr_3d_subfolder_names[@]}"; do
                    subfolder_path="$folder_path/$subfolder_name"
                    mkdir "$subfolder_path"
                    echo "创建子文件夹：$subfolder_path"
                done
            fi

            # 如果创建的是 "AE_out"、"PR_out"、"3D_out" 文件夹，再在里面创建 "A out" 和 "B out"
            if [[ "$folder_name" == "AE_out" || "$folder_name" == "PR_out" || "$folder_name" == "3D_out" ]]; then
                for subfolder_name in "${aeout_prout_3dout_subfolder_names[@]}"; do
                    subfolder_path="$folder_path/$subfolder_name"
                    mkdir "$subfolder_path"
                    echo "创建子文件夹：$subfolder_path"
                done
            fi
            # 如果创建的是客户资料或者 GIF 文件夹，再在里面创建当天日期文件夹
            if [[ "$folder_name" == "客户资料" || "$folder_name" == "gif" ]]; then
                today_folder="$folder_path/$(date +%y%m%d)"
                mkdir "$today_folder"
                echo "创建当天日期文件夹：$today_folder"
            fi
        else
            echo "文件夹已存在：$folder_path"
        fi
    done

    # 检查是否还有未创建的文件夹
    if [ "${#created_folders[@]}" -eq "${#all_folder_names[@]}" ]; then
        echo "所有文件夹都已创建。"
        break
    fi

    # 询问用户是否选择新的文件夹
    read -p "是否选择新的文件夹？ (y/n): " new_choice
    if [ "$new_choice" != "y" ] && [ "$new_choice" != "n" ]; then
        echo "请输入 y 或 n"
        continue
    fi
    if [ "$new_choice" != "y" ]; then
        break
    fi
done

open "${target_folder}/01 客户资料"

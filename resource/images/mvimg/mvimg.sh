#!/bin/bash

# 定义图片存放的主文件夹路径
src_folder="."

# 遍历图片文件夹中的所有文件
for file in "$src_folder"/*; do
    # 获取文件名（不带路径）
    filename=$(basename "$file")
    
    # 提取角色名，假设角色名是文件名的第一个部分，直到第一个数字或文件扩展名为止
    role_name=$(echo "$filename" | sed -r 's/^([a-zA-Z一-龥]+).*/\1/')
    
    # 如果角色名字为空（防止没有匹配到），就跳过
    if [ -z "$role_name" ]; then
        echo "无法提取角色名，跳过文件: $filename"
        continue
    fi
    
    # 创建角色名字对应的子文件夹（如果不存在的话）
    mkdir -p "$src_folder/$role_name"
    
    # 将文件移动到对应角色的文件夹中
    mv "$file" "$src_folder/$role_name/"
    
    echo "移动 $filename 到 $role_name 文件夹"
done

echo "所有文件已整理完毕！"
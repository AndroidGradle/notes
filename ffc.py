#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import re
import time  # 添加time模块

def get_base_filename():
    """获取用户输入的基础文件名"""
    print("请输入基础文件名（例如：/storage/emulated/0/Download/ADM2/stream-407189911113564988_or420260304.flv）:")
    base_file = input().strip()
    
    # 去除可能的引号
    base_file = base_file.strip('"\'')
    
    if not base_file:
        print("错误：文件名为空")
        sys.exit(1)
    
    return base_file

def find_related_files(base_file):
    """查找所有相关的分片文件"""
    directory = os.path.dirname(base_file)
    base_name = os.path.basename(base_file)
    
    # 分离文件名和扩展名
    name_without_ext, ext = os.path.splitext(base_name)
    
    # 构建匹配模式
    pattern = re.compile(rf"^{re.escape(name_without_ext)}(\d*[a-z]?)?{re.escape(ext)}$")
    
    related_files = []
    
    try:
        if os.path.exists(directory):
            for filename in os.listdir(directory):
                if pattern.match(filename):
                    full_path = os.path.join(directory, filename)
                    related_files.append(full_path)
    except Exception as e:
        print(f"查找文件时出错：{e}")
        sys.exit(1)
    
    # 排序文件
    def sort_key(file_path):
        filename = os.path.basename(file_path)
        # 提取后缀部分
        suffix = filename.replace(name_without_ext, '').replace(ext, '')
        if not suffix:  # 基础文件没有后缀
            return (0, '')
        elif suffix.isdigit():  # 数字后缀
            return (1, int(suffix))
        else:  # 字母后缀
            return (2, suffix)
    
    related_files.sort(key=sort_key)
    
    return related_files, name_without_ext, ext, directory

def process_with_ffmpeg(files, base_name_without_ext, ext, directory):
    """使用ffmpeg处理每个文件"""
    
    for i, input_file in enumerate(files):
        # 构建输出文件名 - 直接在原文件名后面加0
        input_filename = os.path.basename(input_file)
        input_name_without_ext, _ = os.path.splitext(input_filename)
        
        # 输出文件名 = 输入文件名 + "0" + 扩展名
        output_filename = f"{input_name_without_ext}0{ext}"
        output_file = os.path.join(directory, output_filename)
        
        # 构建ffmpeg命令
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', input_file,
            '-c', 'copy',
            output_file
        ]
        
        print(f"\n处理文件 {i+1}/{len(files)}: {input_filename} -> {output_filename}")
        print(f"执行命令: {' '.join(ffmpeg_cmd)}")
        print("-" * 50)
        
        try:
            # 使用subprocess.run替代Popen，直接与终端交互
            result = subprocess.run(
                ffmpeg_cmd,
                check=False  # 不主动抛出异常，让ffmpeg自己处理交互
            )
            
            if result.returncode == 0:
                print(f"✓ 成功处理: {output_filename}")
            else:
                print(f"✗ 处理失败: {input_filename}")
            
            # 添加1秒停顿，但最后一个文件不需要停顿
            if i < len(files) - 1:
                print("等待1秒后继续下一个文件...")
                time.sleep(1)
                
        except FileNotFoundError:
            print("错误：未找到ffmpeg命令，请确保已安装ffmpeg并添加到系统路径")
            sys.exit(1)
        except Exception as e:
            print(f"执行ffmpeg时出错：{e}")
            sys.exit(1)
        
        print("-" * 50)

def main():
    """主函数"""
    print("=" * 60)
    print("FFC - FFmpeg 文件处理器")
    print("=" * 60)
    
    # 获取基础文件名
    base_file = get_base_filename()
    
    # 检查基础文件是否存在
    if not os.path.exists(base_file):
        print(f"警告：基础文件不存在：{base_file}")
        response = input("是否继续处理可能存在的其他文件？(y/n): ").strip().lower()
        if response != 'y':
            sys.exit(0)
    
    # 查找相关文件
    print(f"\n正在查找相关文件...")
    related_files, base_name_without_ext, ext, directory = find_related_files(base_file)
    
    if not related_files:
        print("未找到任何相关文件")
        sys.exit(1)
    
    # 显示找到的文件
    print(f"\n找到 {len(related_files)} 个相关文件：")
    for i, file_path in enumerate(related_files):
        print(f"  {i+1}. {os.path.basename(file_path)}")
    
    # 确认处理
    print(f"\n文件将保存到：{directory}")
    response = input("\n是否开始处理？(y/n): ").strip().lower()
    if response != 'y':
        print("已取消")
        sys.exit(0)
    
    # 开始处理
    print("\n开始处理文件...")
    process_with_ffmpeg(related_files, base_name_without_ext, ext, directory)
    
    print(f"\n✨ 处理完成！共处理 {len(related_files)} 个文件")

if __name__ == "__main__":
    main()

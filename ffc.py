import os
import subprocess
import sys

# 配置路径
input_dir = "/storage/emulated/0/Download/ADM2/"
output_dir = "/storage/emulated/0/Download/ADM2/"  # 可以修改为其他输出目录

# 基础文件名（不含序号部分）
base_name = "stream-407189911113564988_or420260304"

# 序号字符列表（按你的规律：1-9, a-g）
# 注意：原始文件第一个没有序号（.flv），然后依次是1,2,3...9,a,b,c,d,e,f,g
suffixes = ['', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
            'a', 'b', 'c', 'd', 'e', 'f', 'g']

def process_files():
    print("开始处理文件...")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for i, suffix in enumerate(suffixes):
        # 构建输入文件名
        if suffix == '':
            input_filename = f"{base_name}.flv"
        else:
            input_filename = f"{base_name}{suffix}.flv"
        
        # 构建输出文件名（在原序号后加0）
        if suffix == '':
            output_filename = f"{base_name}0.flv"
        else:
            output_filename = f"{base_name}{suffix}0.flv"
        
        # 完整的输入输出路径
        input_path = os.path.join(input_dir, input_filename)
        output_path = os.path.join(output_dir, output_filename)
        
        print(f"\n[{i+1}/{len(suffixes)}] 处理文件:")
        print(f"  输入: {input_path}")
        print(f"  输出: {output_path}")
        print("-" * 60)
        
        # 检查输入文件是否存在
        if not os.path.exists(input_path):
            print(f"❌ 错误: 输入文件不存在!")
            print(f"   路径: {input_path}")
            fail_count += 1
            continue
        
        # 检查输出目录是否存在，不存在则创建
        os.makedirs(output_dir, exist_ok=True)
        
        # 构建ffmpeg命令
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-c', 'copy',
            '-y',  # 自动覆盖输出文件
            output_path
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        print("\n--- ffmpeg 详细输出 ---")
        
        try:
            # 执行命令并实时显示输出
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,  # 将stderr合并到stdout
                universal_newlines=True,
                bufsize=1  # 行缓冲
            )
            
            # 实时打印输出
            for line in process.stdout:
                print(line, end='')
            
            # 等待进程结束
            return_code = process.wait()
            
            if return_code == 0:
                print("\n✅ 命令执行成功!")
                
                # 验证输出文件
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    print(f"   输出文件大小: {file_size} 字节")
                    success_count += 1
                else:
                    print(f"❌ 警告: 输出文件未生成!")
                    fail_count += 1
            else:
                print(f"\n❌ 命令执行失败，返回码: {return_code}")
                fail_count += 1
                
        except Exception as e:
            print(f"\n❌ 执行出错: {str(e)}")
            fail_count += 1
        
        print("-" * 60)
    
    # 统计报告
    print("\n" + "=" * 60)
    print("处理完成！统计信息：")
    print(f"  总计文件: {len(suffixes)}")
    print(f"  成功: {success_count}")
    print(f"  失败: {fail_count}")
    print("=" * 60)

def generate_ffmpeg_commands():
    """只生成命令，不执行（预览模式）"""
    print("将执行的ffmpeg命令：")
    print("=" * 60)
    
    for suffix in suffixes:
        if suffix == '':
            input_file = f"{base_name}.flv"
            output_file = f"{base_name}0.flv"
        else:
            input_file = f"{base_name}{suffix}.flv"
            output_file = f"{base_name}{suffix}0.flv"
        
        input_path = os.path.join(input_dir, input_file)
        output_path = os.path.join(output_dir, output_file)
        
        cmd = f"ffmpeg -i {input_path} -c copy -y {output_path}"
        print(cmd)
        print()
    
    print("-" * 60)
    print(f"总计 {len(suffixes)} 条命令")
    print("=" * 60)

def list_files():
    """列出目录中的相关文件"""
    print(f"扫描目录: {input_dir}")
    print("=" * 60)
    
    try:
        files = os.listdir(input_dir)
        related_files = [f for f in files if base_name in f]
        
        if related_files:
            print(f"找到 {len(related_files)} 个相关文件:")
            for f in sorted(related_files):
                file_path = os.path.join(input_dir, f)
                size = os.path.getsize(file_path)
                print(f"  - {f} ({size} 字节)")
        else:
            print("没有找到相关文件")
            
    except Exception as e:
        print(f"扫描目录出错: {e}")
    
    print("=" * 60)

if __name__ == "__main__":
    print("批量视频处理工具")
    print("1. 预览要执行的命令")
    print("2. 执行所有命令（显示详细输出）")
    print("3. 列出目录中的相关文件")
    
    choice = input("请选择 (1/2/3): ").strip()
    
    if choice == '1':
        generate_ffmpeg_commands()
    elif choice == '2':
        print("\n⚠️  即将执行ffmpeg命令，将显示完整输出")
        confirm = input("确认要执行所有命令？(y/n): ").strip().lower()
        if confirm == 'y':
            process_files()
        else:
            print("已取消")
    elif choice == '3':
        list_files()
    else:
        print("无效选择")

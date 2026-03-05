import os
import subprocess

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
    print("-" * 50)
    
    for i, suffix in enumerate(suffixes):
        # 构建输入文件名
        if suffix == '':
            input_filename = f"{base_name}.flv"
        else:
            input_filename = f"{base_name}{suffix}.flv"
        
        # 构建输出文件名（在原序号后加0）
        # 特殊情况：第一个文件（无序号）变成加"0"
        if suffix == '':
            output_filename = f"{base_name}0.flv"
        else:
            output_filename = f"{base_name}{suffix}0.flv"
        
        # 完整的输入输出路径
        input_path = os.path.join(input_dir, input_filename)
        output_path = os.path.join(output_dir, output_filename)
        
        # 检查输入文件是否存在
        if not os.path.exists(input_path):
            print(f"❌ 文件不存在，跳过: {input_filename}")
            continue
        
        # 构建ffmpeg命令
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-c', 'copy',  # 直接复制，不重新编码
            output_path
        ]
        
        print(f"\n处理文件 {i+1}/{len(suffixes)}:")
        print(f"  输入: {input_filename}")
        print(f"  输出: {output_filename}")
        
        try:
            # 执行命令
            # 如果想看到详细输出，去掉 stdout/stderr 的重定向
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✅ 成功")
            else:
                print(f"  ❌ 失败: {result.stderr[:100]}...")  # 只显示前100个错误字符
                
        except Exception as e:
            print(f"  ❌ 执行出错: {str(e)}")
    
    print("\n" + "=" * 50)
    print("批量处理完成！")

def generate_ffmpeg_commands():
    """只生成命令，不执行（预览模式）"""
    print("将执行的ffmpeg命令：")
    print("-" * 50)
    
    for suffix in suffixes:
        if suffix == '':
            input_file = f"{base_name}.flv"
            output_file = f"{base_name}0.flv"
        else:
            input_file = f"{base_name}{suffix}.flv"
            output_file = f"{base_name}{suffix}0.flv"
        
        cmd = f"ffmpeg -i {os.path.join(input_dir, input_file)} -c copy {os.path.join(output_dir, output_file)}"
        print(cmd)
    
    print("-" * 50)
    print(f"总计 {len(suffixes)} 条命令")

if __name__ == "__main__":
    print("批量视频处理工具")
    print("1. 预览要执行的命令")
    print("2. 执行所有命令")
    
    choice = input("请选择 (1/2): ").strip()
    
    if choice == '1':
        generate_ffmpeg_commands()
    elif choice == '2':
        confirm = input("确认要执行所有命令？(y/n): ").strip().lower()
        if confirm == 'y':
            process_files()
        else:
            print("已取消")
    else:
        print("无效选择")

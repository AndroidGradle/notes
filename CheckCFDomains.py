#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import subprocess
import re

# 可配置参数
PING_COUNT = 4          # 发送ping包数量
PING_TIMEOUT = 10       # 单个包超时时间(秒)
FAST_THRESHOLD = 100    # fast阈值(毫秒)，可修改此值

def ping_domain(domain, count=PING_COUNT, timeout=PING_TIMEOUT):
    """发送多个ping包，返回平均延迟(ms)或None"""
    try:
        result = subprocess.run(['ping', '-c', str(count), '-W', str(timeout), domain], 
                              capture_output=True, timeout=timeout+2)
        if result.returncode == 0:
            output = result.stdout.decode()
            
            # 提取平均值 (格式: rtt min/avg/max/mdev = 143.811/150.337/167.360/9.863 ms)
            match = re.search(r'rtt.*= (\d+\.?\d*)/(\d+\.?\d*)/(\d+\.?\d*)/(\d+\.?\d*)', output)
            if match:
                return float(match.group(2))
            
            # 备用方案: 提取avg字段
            match = re.search(r'avg[ =](\d+\.?\d*)/(\d+\.?\d*)/(\d+\.?\d*)/(\d+\.?\d*)', output)
            if match:
                return float(match.group(2))
            
            # 最后的备用方案: 手动计算
            times = re.findall(r'time[= ](\d+\.?\d*)\s*ms', output)
            if times:
                times = [float(t) for t in times]
                return sum(times) / len(times)
    except:
        pass
    return None

def main():
    # 读取文件
    with open('CFDomains.json', 'r') as f:
        data = json.load(f)
    
    # 获取要测试的域名（valid数组）
    domains = data.get('valid', [])
    if not domains:
        print("valid数组为空，无需测试")
        return
    
    print(f"测试 {len(domains)} 个域名（每个发{PING_COUNT}个包取平均）...")
    print(f"fast阈值: {FAST_THRESHOLD}ms\n")
    
    results = []
    
    for i, domain in enumerate(domains, 1):
        print(f"[{i}/{len(domains)}] {domain}...", end=' ', flush=True)
        ping_ms = ping_domain(domain)
        
        if ping_ms:
            results.append((domain, ping_ms))
            if ping_ms <= FAST_THRESHOLD:
                print(f"✓ {ping_ms:.1f}ms (fast)")
            else:
                print(f"✓ {ping_ms:.1f}ms (valid)")
        else:
            results.append((domain, None))
            print("✗ 超时")
    
    # 分类本次测试结果
    new_fast = [d for d, ms in results if ms and ms <= FAST_THRESHOLD]
    new_valid = [d for d, ms in results if ms and ms > FAST_THRESHOLD]
    new_invalid = [d for d, ms in results if ms is None]
    
    # 保留原有的fast和invalid数据（去重）
    existing_fast = data.get('fast', [])
    existing_invalid = data.get('invalid', [])
    
    # fast按ping值排序（只对本次测试的fast排序，原有的保持不变）
    fast_sorted = [d for d, ms in sorted([(d, ms) for d, ms in results if ms and ms <= FAST_THRESHOLD], key=lambda x: x[1])]
    # 将原有fast中不在本次测试中的域名追加到末尾
    for d in existing_fast:
        if d not in new_fast:
            fast_sorted.append(d)
    
    # valid替换为本次测试的valid（覆盖）
    valid_sorted = sorted(new_valid)
    
    # invalid合并原有和新增（去重）
    invalid_sorted = sorted(list(set(existing_invalid + new_invalid)))
    
    # 更新数据
    data['fast'] = fast_sorted
    data['valid'] = valid_sorted
    data['invalid'] = invalid_sorted
    
    # 保存结果
    with open('CFDomains.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n完成！")
    print(f"  fast (≤{FAST_THRESHOLD}ms): {len(fast_sorted)} 个 (新增: {len(new_fast)})")
    print(f"  valid: {len(valid_sorted)} 个 (已更新)")
    print(f"  invalid: {len(invalid_sorted)} 个 (新增: {len(new_invalid)})")

if __name__ == "__main__":
    main()

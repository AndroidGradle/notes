#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import subprocess
import re

def ping_domain(domain, count=4):
    """发送多个ping包，返回平均延迟(ms)或None"""
    try:
        result = subprocess.run(['ping', '-c', str(count), '-W', '10', domain], 
                              capture_output=True, timeout=12)
        if result.returncode == 0:
            output = result.stdout.decode()
            
            # 方法1: 提取所有time=值
            times = re.findall(r'time[= ](\d+\.?\d*)\s*ms', output)
            if times:
                times = [float(t) for t in times]
                return sum(times) / len(times)
            
            # 方法2: 提取avg平均值
            avg_match = re.search(r'avg[ =](\d+\.?\d*)/(\d+\.?\d*)/(\d+\.?\d*)/(\d+\.?\d*)', output)
            if avg_match:
                return float(avg_match.group(2))
            
            # 方法3: 提取rtt行
            rtt_match = re.search(r'rtt.*= (\d+\.?\d*)/(\d+\.?\d*)/(\d+\.?\d*)/(\d+\.?\d*)', output)
            if rtt_match:
                return float(rtt_match.group(2))
    except Exception as e:
        print(f"错误: {e}")
    return None

def main():
    # 读取文件
    with open('CFDomains.json', 'r') as f:
        data = json.load(f)
    
    domains = data.get('valid', [])
    print(f"测试 {len(domains)} 个域名（每个发4个包取平均）...\n")
    
    results = []
    
    for i, domain in enumerate(domains, 1):
        print(f"[{i}/{len(domains)}] {domain}...", end=' ', flush=True)
        ping_ms = ping_domain(domain)
        
        if ping_ms:
            results.append((domain, ping_ms))
            if ping_ms <= 100:
                print(f"✓ {ping_ms:.1f}ms (fast)")
            else:
                print(f"✓ {ping_ms:.1f}ms (valid)")
        else:
            results.append((domain, None))
            print("✗ 超时")
    
    # 分类并排序
    fast = [d for d, ms in results if ms and ms <= 100]
    valid = [d for d, ms in results if ms and ms > 100]
    invalid = [d for d, ms in results if ms is None]
    
    # fast按ping值排序
    fast_sorted = [d for d, ms in sorted([(d, ms) for d, ms in results if ms and ms <= 100], key=lambda x: x[1])]
    
    # valid和invalid按原域名排序
    valid_sorted = sorted(valid)
    invalid_sorted = sorted(invalid)
    
    # 更新数据
    data['fast'] = fast_sorted
    data['valid'] = valid_sorted
    data['invalid'] = invalid_sorted
    
    # 保存结果
    with open('CFDomains.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n完成！")
    print(f"  fast (≤100ms): {len(fast_sorted)} 个")
    print(f"  valid (>100ms): {len(valid_sorted)} 个")
    print(f"  invalid: {len(invalid_sorted)} 个")

if __name__ == "__main__":
    main()

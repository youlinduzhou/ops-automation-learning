# 运维日志分析脚本 Day3 统计各级别出现次数

import re

def count_log_levels(file_path):
    """读取日志文件，统计每个级别的出现次数"""
    counter = {}  # 空字典，计分板
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, start=1):
                match = re.search(r'ERROR|WARNING|INFO|DEBUG', line)
                if match:
                    level = match.group()
                else:
                    level = 'UNKNOWN'
                print(f"{line_number}: {level}")
                counter[level] = counter.get(level, 0) + 1  # 计数+1
    except FileNotFoundError:
        print(f"错误：文件 '{file_path}' 不存在，请检查文件路径！")
        return {}

    print("\n--- 统计结果 ---")
    for level, count in counter.items():
        print(f"{level}: {count}次")

    return counter  # 返回统计结果，为Day5做准备

if __name__ == '__main__':
    count_log_levels('sample.log')

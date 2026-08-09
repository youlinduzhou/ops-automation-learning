# 运维日志分析脚本 Day4 按问题类型归类

import re

CATEGORIES = {
    '网络错误': ['connection', 'DNS', 'SSH', 'network'],
    '权限错误': ['denied', 'permission', 'Authentication'],
    '服务异常': ['service', 'nginx', 'MySQL', 'Redis'],
}

def classify_error(line):
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword.lower() in line.lower():
                return category
    return '其他错误' 

def count_log_levels(file_path):
    """读取日志文件，统计每个级别的出现次数"""
    counter = {}  # 空字典，计分板
    error_counter = {}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, start=1):
                match = re.search(r'ERROR|WARNING|INFO|DEBUG', line, re.IGNORECASE)
                if match:
                    level = match.group().upper() # 提取后统一转大写
                else:
                    level = 'UNKNOWN'
                print(f"{line_number}: {level}")
                counter[level] = counter.get(level, 0) + 1  # 级别计数+1

                if level == 'ERROR':
                    category = classify_error(line)

                    error_counter[category] = error_counter.get(category, 0) + 1  # 类别计数+1

                    print(f' → {category}', end='')

                print()
    except FileNotFoundError:
        print(f"错误：文件 '{file_path}' 不存在，请检查文件路径！")
        return {}

    print("\n--- 级别统计 ---")
    for level, count in counter.items():
        print(f"{level}: {count}次")

    print("\n--- 错误分类统计 ---")
    for category, count in error_counter.items():
        print(f"{category}: {count}个")

    return counter  # 返回统计结果

if __name__ == '__main__':
    count_log_levels('sample.log')

# 运维日志分析脚本 Day2 提取日志级别

import re  # 引入正则表达式模块

def extract_log_levels(file_path):
    """读取日志文件，提取每行的日志级别"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, start=1):  # enumerate给每行编号，从1开始
                # 用正则在每行中搜索 ERROR 或 WARNING 或 INFO 或 DEBUG
                match = re.search(r'ERROR|WARNING|INFO|DEBUG', line)
                if match:
                    # 匹配到了，提取匹配到的文字
                    level = match.group()
                else:
                    # 没匹配到，标记为 UNKNOWN
                    level = 'UNKNOWN'
                print(f"{line_number}: {level}")
    except FileNotFoundError:
        print(f"错误：文件 '{file_path}' 不存在，请检查文件路径！")

if __name__ == '__main__':
    extract_log_levels('sample.log')



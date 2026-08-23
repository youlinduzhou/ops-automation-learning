# 运维日志分析脚本 Day7 按模块重构

import re  #正则表达式模块
import argparse #命令行参数解析模块
from datetime import datetime   #时间模块


CATEGORIES = {
    '网络错误': ['connection', 'DNS', 'SSH', 'network'],
    '权限错误': ['denied', 'permission', 'Authentication'],
    '服务异常': ['service', 'nginx', 'MySQL', 'Redis'],
}

def classify_error(line): # 定义错误分类函数
    for category, keywords in CATEGORIES.items(): # 遍历每个错误类别
        for keyword in keywords: # 遍历每个关键词
            if keyword.lower() in line.lower(): # 如果关键词在日志行中（不区分大小写）
                return category # 返回匹配到的类别
    return '其他错误' 

def read_log_lines(file_path): # 读取日志文件，返回所有行
    """读取日志文件
       file_path: 日志文件路径(必填)
    """
    lines =[] # 在函数开头创建空列表，用来存所有行

    try:
        with open(file_path, 'r', encoding='utf-8') as f: # 打开日志文件
            for line in f:   
                lines.append(line)
        return lines # 循环结束后返回存好的列表
        
    except FileNotFoundError: # 如果文件不存在
        print(f"错误：文件 '{file_path}' 不存在，请检查文件路径！")
        return [] # 返回空列表，表示没有统计结果

def extract_level(line):
    """从日志行中提取日志级别,返回字符串
       line: 日志行(必填)
    """
    match = re.search(r'ERROR|WARNING|INFO|DEBUG', line, re.IGNORECASE)
    if match:
        level = match.group().upper()
    else:
        level = 'UNKNOWN'
    return level

def count_levels(lines):
    """统计日志级别出现次数
       lines: 所有日志行(必填)
    """
    counter = {} # 创建空字典，用来存每个日志级别出现次数
    for line_number, line in enumerate(lines, start=1):
        level = extract_level(line) # 提取日志级别
        print(f"{line_number}: {level}") # 打印日志级别和行号，方便调试用
        counter[level] = counter.get(level, 0) + 1  # 级别计数+1

    print("\n--- 级别统计 ---")
    for level, count in counter.items(): # 遍历每个日志级别
        print(f"{level}: {count}次") # 打印每个级别的出现次数

    return counter # 返回每个日志级别出现次数的字典

def classify_errors(lines):
    """遍历所有行，把ERROR行按类型归类，返回字典"""
    error_counter = {} # 创建空字典，用来存每个错误类别出现次数
    for line in lines:
        level = extract_level(line) # 提取日志级别
        if level == 'ERROR': # 如果日志级别是ERROR
            category = classify_error(line) # 分类错误类别
            error_counter[category] = error_counter.get(category, 0) + 1  # 类别计数+1
            print(f' → {category}') # 打印错误类别
    
    print("\n--- 错误分类统计 ---")
    for category, count in error_counter.items(): # 遍历每个错误类别
        print(f"{category}: {count}个") # 打印每个类别的出现次数    
    return error_counter   # 返回每个错误类别出现次数的字典

def generate_report(counter, error_counter, file_path, total_lines, output_path): 
    """生成日志分析报告,包含级别统计和错误分类统计
       counter: 级别统计字典(必填)
       error_counter: 错误分类字典(必填)
       file_path: 日志文件路径(必填)
       total_lines: 总行数(必填)
       output_path: 输出文件路径(可选)
    """
    now = datetime.now()  # 获取当前时间
    if output_path is None:  # 没传 --output → 用默认日期文件名
        report_file = f"report_{now.strftime('%Y%m%d')}.txt"
        print(f"\n未指定 --output，使用默认文件名：{report_file}") # 打印默认文件名
    else:  # 传了 --output → 用用户指定的文件名
        report_file = output_path
        print(f"\n使用用户指定的文件名：{report_file}") # 打印用户指定的文件名
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"============运维日志分析报告============\n")
        f.write(f"分析时间：{now.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"日志文件：{file_path}\n")
        f.write(f"总行数：{total_lines}\n")
        f.write(f"\n")
        f.write(f"=============级别统计：============\n")
        for level, count in counter.items():
            f.write(f"{level}: {count}次\n")
        f.write(f"\n")
        f.write(f"=============错误分类统计：============\n")
        for category, count in error_counter.items():
            f.write(f"{category}: {count}个\n")
        f.write(f"============================\n")
    print(f"✅ 报告已生成：{report_file}") # 写完后告诉用户文件在哪



    
if __name__ == '__main__':  # 主函数入口
    parser = argparse.ArgumentParser(description='运维日志分析工具：分析日志文件，统计级别与错误分类，生成结构化报告',
        epilog='示例：\n'
               '  python log_analyzer.py --file sample.log\n'
               '  python log_analyzer.py --file sample.log --output my_report.txt',
        formatter_class=argparse.RawDescriptionHelpFormatter)  # 1.创建解析器
    parser.add_argument('--file', required=True, help='日志文件路径（必填）')  # 2.登记--file
    parser.add_argument('--output', help='输出报告文件路径（可选，不传则用默认 report_日期.txt）')  # 3.登记--output
    args = parser.parse_args()  # 4.解析 → args对象此时才存在

    lines = read_log_lines(args.file)
    if lines:
        counter = count_levels(lines)
        error_counter = classify_errors(lines)
        total_lines = len(lines)
        generate_report(counter, error_counter, args.file, total_lines, args.output)

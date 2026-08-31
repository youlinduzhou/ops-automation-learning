# 运维日志分析脚本 Day9 时间过滤

import re  #正则表达式模块
import argparse #命令行参数解析模块
import os #操作系统模块
import glob #文件匹配模块
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

def filter_lines_by_time(lines, start_time, end_time):
    """根据时间范围过滤日志行
       lines: 所有日志行(必填)
       start_time: 开始时间(必填)
       end_time: 结束时间(必填)
       返回: 过滤后的日志行列表
    """

    start_data = datetime.strptime(start_time, '%Y-%m-%d') # 转换为时间对象
    end_data = datetime.strptime(end_time, '%Y-%m-%d') .replace(hour=23, minute=59, second=59) # 转换为时间对象

    filtered_lines = [] # 创建空列表，用来存过滤后的日志行

    for line in lines: # 遍历所有日志行

        try:
            parts = line.split() # 按空格分割日志行，得到每个字段
            time_str = parts[0] + ' ' + parts[1] # 提取时间字段
            log_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S') # 转换为时间对象
        except ( IndexError, ValueError): # 如果时间字段格式错误，跳过
            print(f"警告：时间字段格式错误，已跳过行 {line.strip()}")
            # 打印错误行，方便调试用
            continue # 跳过当前循环，继续下一行
            
        if start_data <= log_time <= end_data: 
            filtered_lines.append(line) # 时间在范围内，加入过滤后的列表
            
    return filtered_lines # 返回过滤后的日志行列表


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

def find_log_files(dir_path):
    """找出目录下所有 .log 文件
       dir_path: 目录路径(必填)
       返回: .log 文件路径列表
    """
    if os.path.isdir(dir_path):  # 目录存在
        return glob.glob(os.path.join(dir_path, '*.log'))
    print(f"错误：目录 '{dir_path}' 不存在，请检查路径是否正确")
    return []  # 目录不存在 → 返回空列表（替代exit(1)，和read_log_lines风格一致）

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

def generate_batch_report(batch_results, output_path):
    """生成批量分析汇总报告：每个文件一段
       batch_results: 列表，每个元素是 (文件路径, counter, error_counter, 总行数)
    """
    now = datetime.now()
    if output_path is None:  # 没传 --output → 用默认日期文件名
        report_file = f"report_batch_{now.strftime('%Y%m%d%H%M%S')}.txt"
        print(f"\n未指定 --output，使用默认文件名：{report_file}") # 打印默认文件名
    
    else:  # 传了 --output → 用用户指定的文件名
        report_file = output_path
        print(f"\n使用用户指定的文件名：{report_file}") # 打印用户指定的文件名

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"============运维日志批量分析汇总报告============\n")
        f.write(f"分析时间：{now.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"文件数量：{len(batch_results)}个\n\n")

        total_counter = {}   # 循环开始前：所有文件累计的级别统计
        total_error = {}     # 循环开始前：所有文件累计的错误分类

        # ↓ 外层for：解包元组，回忆 enumerate 
        for file_path, counter, error_counter, total_lines in batch_results:
            f.write(f"-------- 文件：{file_path}（共{total_lines}行）--------\n")
            
            # ↓ 内层两个for写级别统计、错误分类
            f.write(f"=============级别统计：============\n")
            
            for level, count in counter.items():
                f.write(f"{level}: {count}次\n")
                total_counter[level] = total_counter.get(level, 0) + count  # 累计所有文件的级别统计
            
            for category, count in error_counter.items():
                total_error[category] = total_error.get(category, 0) + count  # 累计所有文件的错误分类
            f.write(f"\n")
           
            f.write(f"=============错误分类统计：============\n")
            for category, count in error_counter.items():
                f.write(f"{category}: {count}个\n")
           
        f.write(f"=============所有文件总计：============\n")
        f.write(f"总行数：{sum(total_counter.values()) }行\n")
        f.write(f"错误总计：{sum(total_error.values())}个\n")
        f.write(f"============================\n")
    print(f"✅ 汇总报告已生成：{report_file}")    

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
        report_file = f"report_{now.strftime('%Y%m%d%H%M%S')}.txt"
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
               '  python log_analyzer.py --file sample.log --output my_report.txt\n'
               '  python log_analyzer.py --dir ./logs/',
        formatter_class=argparse.RawDescriptionHelpFormatter)  # 1.创建解析器
    parser.add_argument('--file', help='单个日志文件路径（可选）')  # 2.登记--file
    parser.add_argument('--dir', help='日志文件所在目录路径（可选）')  # 3.登记--dir
    parser.add_argument('--start', help='开始日期(YYYY-MM-DD, 格式：2023-01-01)') # 4登记--start
    parser.add_argument('--end', help='结束日期(YYYY-MM-DD, 格式：2023-01-01)') # 5登记--end
    parser.add_argument('--output', help='输出报告文件路径（可选，不传则用默认文件名）') # 6登记--output
    args = parser.parse_args()

    if (args.start and not args.end) or (not args.start and args.end): # 有开始日期但没有结束日期的，或者没有开始日期，但是有结束日期的
       parser.error('必须同时指定 --start 和 --end，格式：YYYY-MM-DD, 格式：2023-01-01，或者两个都不传')  
        
    if not args.file and not args.dir:  # 都没传
        parser.error('必须指定 --file 或 --dir 其中一个')

    if args.dir:  # ===== 批量分支 =====
        log_files = find_log_files(args.dir)
        
        if log_files:  # 列表非空才继续（目录不存在时上面已打印提示）
            batch_results = []  # 收集每个文件的打包结果
            for log_file in log_files:
                lines = read_log_lines(log_file)      # 单个文件 → 传文件路径
                
                if lines:  # 单个文件读不到就跳过，不中断批量（Done标准伏笔）
                    if args.start and args.end:              # 传了时间参数才过滤
                        lines = filter_lines_by_time(lines, args.start, args.end)
                    counter = count_levels(lines)
                    error_counter = classify_errors(lines)
                    batch_results.append((log_file, counter, error_counter, len(lines)))
            generate_batch_report(batch_results, args.output)

    else:  # ===== 单文件分支：Day 8 =====
        lines = read_log_lines(args.file)
        if lines:
            if args.start and args.end:              # 传了时间参数才过滤
                lines = filter_lines_by_time(lines, args.start, args.end)
            counter = count_levels(lines)
            error_counter = classify_errors(lines)
            generate_report(counter, error_counter, args.file, len(lines), args.output)

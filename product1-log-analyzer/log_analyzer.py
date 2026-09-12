# 运维日志分析脚本 Day11 错误模式检测

import re  #正则表达式模块
import argparse #命令行参数解析模块
import os #操作系统模块
import glob #文件匹配模块
import html #HTML模块
from datetime import datetime   #时间模块


CATEGORIES = {
    '数据库错误': ['MySQL','database'],
    '存储错误': ['storage', 'write file'],
    '网络错误': ['connection', 'DNS', 'SSH', 'network'],
    '权限错误': ['denied', 'permission', 'Authentication'],
    '服务异常': ['service', 'nginx', 'Redis'],
}

FREQUENT_THRESHOLD = 3  # 高频错误阈值，同一错误出现>=3次认为是高频

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

def find_frequent_errors(lines, threshold=3):
    """找出高频错误（同一错误信息出现次数>=阈值）
       lines: 所有日志行(必填)
       threshold: 高频判定阈值(可选，默认3)
       返回: 高频错误列表，每个元素是 (错误指纹, 次数, 首次时间, 末次时间)
    """
    # ① 创建空字典，存每个错误指纹的统计信息
    #    结构：{错误指纹: [次数, 首次时间, 末次时间]}
    error_stats = {}
    
    # ② 遍历所有日志行
    for line in lines:
        # ②.1 提取日志级别，只处理 ERROR 行
        level = extract_level(line)
        if level != 'ERROR':
            continue  # 不是 ERROR 就跳过
        
        # ②.2 提取时间字符串和错误指纹
        parts = line.split()
        time_str = parts[0] + ' ' + parts[1]  # 时间字符串
        error_fingerprint = ' '.join(parts[2:])  # 错误指纹
        
        # ②.3 更新字典
        if error_fingerprint in error_stats:
            # 再次遇到：次数+1，末次时间更新
            error_stats[error_fingerprint][0] += 1
            error_stats[error_fingerprint][2] = time_str
        else:
            # 首次遇到：创建条目 [1, 时间, 时间]
            error_stats[error_fingerprint] = [1, time_str, time_str]
    
    # ③ 筛选高频错误：遍历字典，挑出 次数 >= threshold 的条目
    frequent_list = []
    for fingerprint, stats in error_stats.items():
        if stats[0] >= threshold:
            # 转成元组 (错误指纹, 次数, 首次时间, 末次时间)
            frequent_list.append((fingerprint, stats[0], stats[1], stats[2]))
    
    # ④ 返回筛选结果
    return frequent_list

def generate_batch_report(batch_results, output_path):
    """生成批量分析汇总报告：每个文件一段
       batch_results: 列表，每个元素是 (文件路径, counter, error_counter, 总行数, 高频错误列表)
    """
    now = datetime.now()
    if output_path is None:  # 没传 --output → 用默认日期文件名
        report_file = f"report_batch_{now.strftime('%Y%m%d%H%M%S')}.txt"
        print(f"\n未指定 --output，使用默认文件名：{report_file}") # 打印默认文件名
    
    else:  # 传了 --output → 用用户指定的文件名
        report_file = output_path
        print(f"\n使用用户指定的文件名：{report_file}") # 打印用户指定的文件名

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"============运维日志批量分析汇总报告（TXT版）============\n")
        f.write(f"分析时间：{now.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"文件数量：{len(batch_results)}个\n\n")

        total_counter = {}   # 循环开始前：所有文件累计的级别统计
        total_error = {}     # 循环开始前：所有文件累计的错误分类

        # ↓ 外层for：解包元组，回忆 enumerate 
        for file_path, counter, error_counter, total_lines, frequent_errors in batch_results:
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

            if frequent_errors: # 如果有频繁错误
                f.write(f"=============高频错误清单：============\n")
                f.write(f"出现次数超过{FREQUENT_THRESHOLD}次的错误：\n")
                for fingerprint, count, first_time, last_time in frequent_errors:
                    f.write(f"  {fingerprint}: {count}次，首次：{first_time}，末次：{last_time}\n")
            else: # 如果没有频繁错误
                f.write(f"=============高频错误清单：============\n")
                f.write(f"没有出现次数超过{FREQUENT_THRESHOLD}次的错误\n")
            f.write(f"\n")

        f.write(f"=============所有文件总计：============\n")
        f.write(f"总行数：{sum(total_counter.values()) }行\n")
        f.write(f"错误总计：{sum(total_error.values())}个\n")
        f.write(f"============================\n")
    print(f"✅ 汇总报告已生成：{report_file}")    

def generate_report(counter, error_counter, file_path, total_lines, frequent_errors, output_path):
    """生成TXT日志分析报告,包含级别统计和错误分类统计
       counter: 级别统计字典(必填)
       error_counter: 错误分类字典(必填)
       file_path: 日志文件路径(必填)
       total_lines: 总行数(必填)
       frequent_errors: 高频错误列表(必填)
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
        f.write(f"============运维日志分析报告（TXT版）============\n")
        f.write(f"分析时间：{now.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"日志文件：{file_path}\n")
        f.write(f"总行数：{total_lines}\n")
        f.write(f"\n")

        # ===== 高频错误清单 =====
        if frequent_errors:  # 如果有高频错误
            f.write(f"=============高频错误清单：============\n")
            f.write(f"出现次数超过{FREQUENT_THRESHOLD}次的错误：\n")
            for fingerprint, count, first_time, last_time in frequent_errors:
                f.write(f"  {fingerprint}: {count}次，首次：{first_time}，末次：{last_time}\n")
            f.write(f"\n")
        else:  # 没有高频错误
            f.write(f"=============高频错误清单：============\n")
            f.write(f"没有出现次数超过{FREQUENT_THRESHOLD}次的错误\n\n")

        # ===== 级别统计 =====
        f.write(f"=============级别统计：============\n")
        for level, count in counter.items():
            f.write(f"{level}: {count}次\n")
        f.write(f"\n")

        # ===== 错误分类统计 =====
        f.write(f"=============错误分类统计：============\n")
        for category, count in error_counter.items():
            f.write(f"{category}: {count}个\n")
        f.write(f"============================\n")
    print(f"✅ 报告已生成：{report_file}") # 写完后告诉用户文件在哪

def build_report_content(counter, error_counter, file_path, total_lines, frequent_errors):
    """数据层：构建单文件报告数据（纯dict，不含任何格式）"""
    return {
        'type': 'single', # 报告类型：单文件或批量
        'file_path': file_path, # 日志文件路径
        'total_lines': total_lines, # 总行数
        'frequent_errors': frequent_errors, # 高频错误列表
        'counter': counter, # 级别统计字典
        'error_counter': error_counter, # 错误分类字典
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), # 生成时间
    }

def build_batch_report_content(batch_results): # 批量报告数据
    """数据层：构建批量报告数据（纯dict，不含任何格式）"""
    total_counter = {} # 所有文件的级别统计字典
    total_error = {} # 所有文件的错误分类字典
    files = [] # 所有文件的报告数据列表

    for file_path, counter, error_counter, total_lines, frequent_errors in batch_results: # 遍历每个文件的分析结果
        files.append({ # 每个文件的报告数据
            'file_path': file_path, # 日志文件路径
            'total_lines': total_lines, # 总行数
            'frequent_errors': frequent_errors, # 高频错误列表
            'counter': counter, # 级别统计字典
            'error_counter': error_counter, # 错误分类字典
        })
        for level, count in counter.items():
            total_counter[level] = total_counter.get(level, 0) + count
        for category, count in error_counter.items():
            total_error[category] = total_error.get(category, 0) + count

    return { # 批量报告数据
        'type': 'batch', # 报告类型：单文件或批量
        'files': files, # 所有文件的报告数据列表
        'total_counter': total_counter, # 所有文件的级别统计字典
        'total_error': total_error, # 所有文件的错误分类字典
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), # 生成时间
    }

def _render_stats_table(title, items):
    """把统计字典渲染成完整HTML表格（下划线开头=模块内部私有函数）"""
    table = f"<table><tr><th>{title}</th><th>数量</th></tr>\n"
    for name, count in items.items():
        table += f"<tr><td>{html.escape(str(name))}</td><td>{count}</td></tr>\n"
    table += "</table>"
    return table

def _render_frequent_errors_table(frequent_errors):
    """把高频错误列表渲染成4列HTML表格
       frequent_errors: 列表，元素是 (错误指纹, 次数, 首次时间, 末次时间)"""
    if not frequent_errors:  # 无高频错误 → 返回提示段落，避免空表头
        return "<p>没有出现次数超过阈值的高频错误</p>"
    table = f"<table><tr><th>错误指纹</th><th>次数</th><th>首次</th><th>末次</th></tr>\n"
    for error, count, first_time, last_time in frequent_errors:
        table += f"<tr><td>{html.escape(error)}</td><td>{count}</td><td>{html.escape(first_time)}</td><td>{html.escape(last_time)}</td></tr>\n"     
    table += "</table>"
    return table

def write_html_report(content, output_path):
    """格式层：把报告数据dict渲染成HTML并写入文件"""
    now = datetime.now()
    if content['type'] == 'batch':
        default_name = f"report_batch_{now.strftime('%Y%m%d%H%M%S')}.html"
    else:
        default_name = f"report_{now.strftime('%Y%m%d%H%M%S')}.html"

    if output_path is None:
        report_file = default_name
        print(f"\n未指定 --output，使用默认文件名：{report_file}")
    else:
        report_file = output_path
        print(f"\n使用用户指定的文件名：{report_file}")

    # ---- 组装HTML（每行一个元素，最后一次性写入）----
    lines = []
    lines.append("<!DOCTYPE html>")
    lines.append("<html lang='zh-CN'>")
    lines.append("<head>")
    lines.append("    <meta charset='UTF-8'>")  # 防中文乱码关键
    lines.append("    <title>运维日志分析报告</title>")
    lines.append("    <style>")
    lines.append("        body { font-family: Arial, sans-serif; margin: 20px; }") # 字体和间距
    lines.append("        h1 { color: #2c3e50; }") # 标题颜色
    lines.append("        table { border-collapse: collapse; margin: 10px 0; }") # 表格样式
    lines.append("        td, th { border: 1px solid #ccc; padding: 5px 12px; }") # 单元格样式
    lines.append("        th { background: #f2f2f2; }") # 表头背景颜色
    lines.append("        .file { margin-top: 20px; font-weight: bold; }") # 文件路径样式
    lines.append("    </style>")
    lines.append("</head>")
    lines.append("<body>")
    lines.append("    <h1>运维日志分析报告</h1>")
    lines.append(f"    <p>分析时间：{content['generated_at']}</p>")
    
    if content['type'] == 'single':  # ===== 单文件报告 =====
        lines.append(f"    <p>日志文件：{html.escape(content['file_path'])}</p>")
        lines.append(f"    <p>总行数：{content['total_lines']}</p>")
        lines.append("    <h2>级别统计</h2>")
        lines.append(_render_stats_table('级别', content['counter'])) 
        lines.append("    <h2>高频错误统计</h2>")
        lines.append(_render_frequent_errors_table(content['frequent_errors'])) # 添加高频错误表格显示
        lines.append("    <h2>错误分类统计</h2>")
        lines.append(_render_stats_table('错误类别', content['error_counter']))   # 错误分类统计       

    else:  # ===== 批量报告 =====
        lines.append(f"    <p>文件数量：{len(content['files'])}个</p>")
        lines.append("    <h2>每个文件的详细统计</h2>")
        for file in content['files']:
            lines.append(f"    <p class='file'>文件：{html.escape(file['file_path'])}（共{file['total_lines']}行）</p>") # 文件路径和总行数
            lines.append(_render_stats_table('级别', file['counter'])) # 级别统计
            lines.append(_render_frequent_errors_table(file['frequent_errors'])) # 添加高频错误表格显示
            lines.append(_render_stats_table('错误类别', file['error_counter']))   # 错误分类统计       
        lines.append("    <h2>所有文件总计</h2>")
        lines.append(_render_stats_table('级别', content['total_counter'])) # 所有文件的级别统计
        lines.append(_render_stats_table('错误类别', content['total_error'])) # 所有文件的错误分类统计

    lines.append("</body>")
    lines.append("</html>")

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

    print(f"✅ HTML报告已生成：{report_file}")



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
    parser.add_argument('--format', choices=['txt', 'html'], default='txt', help='输出格式：txt或html（默认txt，向后兼容）') # 6登记--format
    parser.add_argument('--output', help='输出报告文件路径（可选，不传则用默认文件名）') # 7登记--output    
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
                        lines = filter_lines_by_time(lines, args.start, args.end) # 过滤时间范围内的日志行
                    if not lines:
                       print(f"提示：文件 '{log_file}' 在 {args.start} ~ {args.end} 范围内没有日志，跳过")  
                       continue
                    else:
                        error_counter = classify_errors(lines) # 分类错误
                        counter = count_levels(lines)    # 统计级别
                        frequent_errors = find_frequent_errors(lines) # 查找高频错误            
                    batch_results.append((log_file, counter, error_counter, len(lines), frequent_errors)) # 收集每个文件的打包结果
            if args.format == 'html':  # HTML格式 → 数据层+格式层
                content = build_batch_report_content(batch_results)  # ①数据层：dict
                write_html_report(content, args.output)              # ②格式层：dict→HTML→文件
            else:  # 默认txt → 走老函数（向后兼容）
                generate_batch_report(batch_results, args.output)    # 生成批量报告

    else:  # ===== 单文件分支 =====
        lines = read_log_lines(args.file)  # 读取单个文件的日志行
        if lines:  # 单个文件读不到就跳过，不中断批量（Done标准伏笔）
            if args.start and args.end:              # 传了时间参数才过滤
                lines = filter_lines_by_time(lines, args.start, args.end) # 过滤时间范围内的日志行
            if not lines:
                print(f"⚠️ 警告：文件 '{args.file}' 在 {args.start} 至 {args.end} 时间范围内没有日志行")
            else:
                counter = count_levels(lines)
                error_counter = classify_errors(lines)
                frequent_errors = find_frequent_errors(lines)
                if args.format == 'html':
                    content = build_report_content(counter, error_counter, args.file, len(lines), frequent_errors)
                    write_html_report(content, args.output)
                else:
                    generate_report(counter, error_counter, args.file, len(lines), frequent_errors, args.output)
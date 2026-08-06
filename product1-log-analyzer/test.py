# 运维日志分析脚本 Day 1：读取日志文件并打印内容
def read_log_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                print(line, end='')
    except FileNotFoundError:
        print(f"错误:文件, '{file_path}' 该路径找不到此文件！ ")

if __name__ == '__main__':
    read_log_file('sample.log')
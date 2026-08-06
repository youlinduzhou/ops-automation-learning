# 运维日志分析脚本 Day1 读取日志文件并打印


def read_log_file(file_path):
    """读取日志文件，逐行打印内容"""
    try:
        # with 语句打开文件，离开这个缩进块会自动关闭文件
        with open(file_path, 'r', encoding='utf-8') as f:
            # 逐行读取并打印；end='' 避免 print 自带换行导致多出空行
            for line in f:
                print(line, end='')
    except FileNotFoundError:
        # 文件不存在时打印友好提示，而不是让程序报错崩溃
        print(f"错误：文件 '{file_path}' 不存在，请检查文件路径！")

# 程序入口：只有直接运行本文件时才会执行下面这行
if __name__ == '__main__':
    read_log_file('sample.log')




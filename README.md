# ops-automation-learning

运维自动化学习项目：用 Python + Dify 做三个可展示的成品。

- **成品1**：运维日志分析工具（`product1-log-analyzer/`）——Python 脚本，见下方说明
- **成品2**：运维知识库 AI 助手——基于 Dify 低代码平台搭建（非代码，不在此仓库）
- **成品3**：运维自动化巡检工具——规划中

学习笔记见 [`notes.md`](notes.md)。

---

# 成品1：运维日志分析工具

自动分析运维日志文件，统计 ERROR/WARNING/INFO 级别，按问题类型归类，检测高频错误，生成结构化报告。

## 功能

- 读取单个日志文件，或批量读取目录下所有 `.log` 文件
- 用正则表达式提取日志级别（ERROR / WARNING / INFO / DEBUG，忽略大小写）
- 按问题类型分类（数据库错误 / 存储错误 / 网络错误 / 权限错误 / 服务异常 / 其他错误）
- 支持时间范围过滤（按日期）
- 检测高频错误（同一条错误信息出现 3 次及以上）
- 生成 TXT 或 HTML 格式报告（HTML 含级别统计、高频错误、错误分类三节）

## 使用方法

命令在仓库根目录执行（报告默认生成在当前目录）。

```bash
# 分析单个文件（默认输出 TXT）
python product1-log-analyzer/log_analyzer.py --file product1-log-analyzer/sample.log

# 批量分析目录下所有 .log 文件
python product1-log-analyzer/log_analyzer.py --dir product1-log-analyzer/logs/

# 指定时间范围（--start 与 --end 必须成对使用，格式 YYYY-MM-DD）
python product1-log-analyzer/log_analyzer.py --file product1-log-analyzer/sample.log --start 2026-08-01 --end 2026-08-01

# 生成 HTML 报告
python product1-log-analyzer/log_analyzer.py --file product1-log-analyzer/sample.log --format html

# 指定输出文件名（默认用时间戳命名，如 report_20260913105802.txt）
python product1-log-analyzer/log_analyzer.py --file product1-log-analyzer/sample.log --output my_report.txt
```

### 命令行参数

| 参数 | 说明 |
| --- | --- |
| `--file` | 单个日志文件路径（与 `--dir` 二选一，必填其一） |
| `--dir` | 日志文件所在目录，批量分析其中所有 `.log` 文件 |
| `--start` | 开始日期（`YYYY-MM-DD`），与 `--end` 成对使用 |
| `--end` | 结束日期（`YYYY-MM-DD`），与 `--start` 成对使用 |
| `--format` | 输出格式：`txt` 或 `html`（默认 `txt`） |
| `--output` | 输出报告文件路径，不传则用时间戳默认名 |

## 设计说明

报告生成采用**数据层与格式层分离**：`build_report_content` / `build_batch_report_content` 只产出纯数据字典（不碰文件），`generate_report` / `write_html_report` 负责把数据渲染成 TXT / HTML 并写文件。这样新增一种输出格式时，数据统计逻辑无需改动。

## 技术栈

Python 3.10+ / re / argparse / datetime / os / glob / html（均标准库，无第三方依赖）

## 作者

张彦新（GitHub: [youlinduzhou](https://github.com/youlinduzhou)）

# 学习笔记

> 记录日期：2026-08-05 ~ 08-09  
> 用途：代码理解笔记放这里，不污染可运行的 .py 文件

***

## 一、Day 0 + 成品2 笔记（08-04）

### 计划核心（记住这三条）

- **方向**：B+C 组合 —— B=低代码AI应用（Dify，先变现见效快）；C=Python运维自动化（补代码能力，吃9年运维经验红利）
- **三个成品**（成品思维：先定成品再倒推学什么）：

  - 成品1：运维日志分析脚本（Python，2周）
  - 成品2：运维知识库AI助手（Dify，1周）✅ 已发布
  - 成品3：运维自动化巡检（Python+Dify，2-3周）

- **每日三原则**：时间固定（晚20:00-21:30底线）、任务具体、反馈及时（每天产出一个可运行的东西）

### 环境配置（6组30项全部通过 ✅）

<!--inkdown-t:widths=90,510-->
| 组别       | 结果                                                                     |
| ---------- | ------------------------------------------------------------------------ |
| Python     | 3.14.4 + pip 26.0.1 + 清华源 + venv                                      |
| Trae IDE   | 3.3.73 + AI对话 + Python插件 + 内置终端                                  |
| Git/GitHub | git 2.53.0 + 仓库 ops-automation-learning（Public+README+MIT）+ sync.ps1 |
| Dify       | 宏碁笔记本 WSL2 + Docker 29.6.2 + 14容器                                 |
| 模型       | ZhipuAI glm-4.7-flash（永久免费）+ embedding-3（免费）                   |
| 日志样本   | sample.log 20行（ERROR/WARNING/INFO）                                    |

> **内存观察**：Docker + Dify（浏览器运行）+ Trae IDE 三件套同时运行，16GB内存峰值约10GB（不超过10GB）。不用Dify时可 `docker compose stop` 释放内存。

### 踩坑记录（最有价值的部分）

1. **SSH 22端口被封** → 认证改用 HTTPS + PAT + dev-sidecar代理(127.0.0.1:31181)
2. **git push超时** → 配置 `git config --global http.proxy http://127.0.0.1:31181`（https.proxy同）
3. **sync.ps1退出码bug** → `git diff --cached --quiet` 的退出码1=有变更应提交（原逻辑写反了）
4. **DeepSeek** → 改 ZhipuAI 4.7 flash（更稳定且永久免费）
5. **Dify模型配置找不到** → 侧边栏"集成→模型供应商→ZHIPU AI"（UI更新后位置会变）
6. **Chatflow节点顺序错误** → 错误：开始→LLM→知识检索→直接回复（LLM先跑看不到知识库）；正确：开始→**知识检索→LLM**→直接回复
7. **通用分段把Markdown切碎** → 召回0.44分被0.5阈值过滤；切换"父子分段"模式（子块700字符、父块段落）后召回0.58-0.68
8. **知识检索输出变量选不了** → `{{#context#}}`要**手打**到SYSTEM提示词末尾（Dify渲染为📄上下文芯片），不是标准变量不能从选择器选

### 成品2 配置备忘（运维知识库助手）

- **应用**：Chatflow 类型（多轮对话有记忆；Workflow单轮无记忆）
- **知识库**：ops-knowledge-base，文档=第一个月实验手册（18个父块）
- **检索配置**：高质量+混合检索（语义0.7/关键词0.3），Top K=3，Score阈值0.5，Rerank关闭
- **Web App**：开场白✅ 问题建议✅ 引用归属✅ 文件上传❌ 内容审查❌
- **SYSTEM提示词结构**：角色+回答规则（结论先行/知识库优先/危险操作警告/末尾追问）+格式（代码块/有序列表）+`{{#context#}}`
- **端到端测试**：问"WSL2怎么装Ubuntu?" → 结论先行+4步步骤+代码块+风险提示+末尾追问，完美通过

***

## 二、Day 1 笔记：log_analyzer.py（08-05~06）

### 脚本一句话

读日志文件 → 逐行打印；文件不存在时打印友好提示，不崩溃。

### 逐块理解（我的翻译 + 核心职责）

1. **`def read_log_file(file_path):`** → def 是声明/定义，read 读，log 日志，file 文件 → "定义一个读日志文件的函数，需要传文件路径给它" | 核心职责：把可复用代码打包起名，按名调用
2. **`try:`** → 先尝试执行，出错有预案 | 核心职责：异常处理（错误捕获），出错时不崩溃
3. **`with open(file_path, 'r', encoding='utf-8') as f:`** → 打开文件——开哪个（file_path）、什么模式（r=只读）、什么编码（utf-8 防乱码），起名 f，用完自动关闭 | 核心职责：管理文件开关（打开→用完自动关，不用手动 close）
4. **`for line in f:`** → for 是"对每一个"，line 是"一行" → "对文件里的每一行" | 核心职责：逐行遍历，自动从头取到尾，取完自动停
5. **`print(line, end='')`** → 打印这一行；end='' 表示末尾不加额外换行（日志行自带换行）| 核心职责：输出内容，不产生多余空行
6. **`except FileNotFoundError:`** → 除非遇到"文件找不到"这个特定错误 | 核心职责：精准兜底，只拦这一种错，其他错误不掩盖
7. **`print(f"...")`** → f 是格式化，把变量用 {} 塞进字符串 | 核心职责：输出带变量的友好提示
8. **`if __name__ == '__main__':`** → **name** 是文件名变量；直接运行时它等于 '**main**' → "如果我是被直接运行的这个脚本" | 核心职责：区分"直接运行"还是"被 import 引用"
9. **`read_log_file('sample.log')`** → 调用上面定义的函数，告诉它读 sample.log | 核心职责：触发执行（def 是写说明书，这行才是开工）

### 记忆骨架（8步逻辑链条）

````
打包  → def read_log_file(file_path):
防错  → try:
开门  → with open(...) as f:
读    → for line in f:
打印  → print(line, end='')
兜底  → except FileNotFoundError:
开关  → if __name__ == '__main__':
开工  → read_log_file('sample.log')
````

### 默写时踩的3个坑

1. **except 缩进**必须和 try 对齐（都是4个空格）
2. **FileNotFoundError** 大小写敏感（F、N、F 三个大写）
3. **中文输入法**导致全角符号（字符串外的括号/引号必须英文半角）

### 复盘问题

- 为什么用 with？→ 自动关闭文件
- 为什么 end=''？→ 日志行自带换行符，避免打印出空行
- 为什么用 except FileNotFoundError 而不是 except Exception？→ 只拦特定错误，不掩盖其他问题
- open() 的三个参数分别是什么？→ 文件路径、模式 r/w/a、编码
- 'sample.log' 是全盘搜索吗？→ 不是，只在当前工作目录找（相对路径）

### Git 提交历史

````
91f1a6b Day 1: 实现日志文件读取和打印功能
63cb806 test sync
e277fd2 Day 0: 项目初始化（README/.gitignore/目录结构）
2d4a53c Initial commit
````

***

## 二-B、Day 2 笔记：提取日志级别（08-06）

### 脚本一句话

在Day 1逐行打印的基础上，用正则表达式提取每行的日志级别（ERROR/WARNING/INFO），输出"行号: 级别"。

### Day 2 新增5个知识点（逐词注释）

#### ① `import re` — 引入正则模块

- `import` = 引入/导入
- `re` = 正则表达式模块（Python自带，不用pip安装）

#### ② `enumerate(f, start=1)` — 给每行编号

- `enumerate` = 给每项编号的函数
- `f` = 要遍历的文件对象
- `start=1` = 编号从1开始（不是默认的0）
- 和Day 1的 `for line in f` 区别：enumerate额外给一个行号

#### ③ `re.search(r'ERROR|WARNING|INFO', line)` — 正则搜索

- `re.search` = 在字符串中搜索第一个匹配项

  - 找到 → 返回Match对象（if眼里是True）
  - 没找到 → 返回None（if眼里是False）

- `r'...'` = raw字符串（原始字符串），\不会被转义
- `|` = 正则的"或"，`ERROR|WARNING|INFO` 匹配三者之一

#### ④ `match.group()` — 取出匹配到的文字

- `match` = re.search的返回值（Match对象）
- `.group()` = 取出匹配到的文字
- 比如匹配到ERROR，就返回字符串`'ERROR'`

#### ⑤ `if match:` — 用真假判断代替显式比较

- 核心原理：Match对象在if里是True，None在if里是False
- `if match:` 等价于 `if match is not None:`
- 不需要写 `if match == True`，Python风格就是直接 `if match:`

### 记忆骨架（Day 2 在 Day 1 基础上新增的部分）

````
读+编号 → for line_number, line in enumerate(f, start=1):    ← 新
瞄准    → match = re.search(r'ERROR|WARNING|INFO', line)     ← 新
判断    → if match:                                           ← 新
命中    →     level = match.group()                           ← 新
落空    → else: level = 'UNKNOWN'                            ← 新
打印    → print(f"{line_number}: {level}")                    ← 改
````

### 关键认知纠正

- `re.search()` 没找到返回的是 `None`，不是 `UNKNOWN`。UNKNOWN是我们代码else分支贴的标签。
- `|` 在正则里是"或"，不是Python的位运算符。

### 创：扩展DEBUG级别

- 只需在正则模式加 `|DEBUG`：`r'ERROR|WARNING|INFO|DEBUG'`
- 正则"或"的威力：加一个 `|新词` 就扩展一个识别能力

### Git 提交

````
8f7145f Day 2：实现日志级别的提取（正则表达式+DEBUG扩展）
````

***

## 三、Day 3 笔记：字典统计日志级别（08-08）

### 脚本一句话

在Day 2提取级别的基础上，用字典统计每个级别出现几次，打印统计结果。

### Day 3 新增3个知识点（逐词注释）

#### ① `counter = {}` — 创建空计分板

- `counter` = 变量名（自己起的，意思是"计数器"）
- `{}` = 空字典（键值对容器，像计分板：{级别: 次数}）
- `=` = 赋值，把空字典装进counter这个变量

#### ② `counter[level] = counter.get(level, 0) + 1` — 核心计数

- `counter[level]` = 字典的键访问/赋值

  - 读取：`counter['ERROR']` → 取出ERROR的次数
  - 赋值：`counter['ERROR'] = 9` → 把ERROR的次数设为9

- `counter.get(level, 0)` = 安全取值

  - `.get` = 字典的方法，取值
  - `level` = 要找的键名
  - `0` = 默认值（键不存在时返回0，而不是报错KeyError）

- `+ 1` = 在原值基础上加1
- 整句意思：这个级别出现过几次？取出旧次数+1，写回去

#### ③ `return counter` — 把计分板交出去

- `return` = 从函数返回一个值，函数到此结束
- `counter` = 字典，如 `{'ERROR': 10, 'WARNING': 4, 'INFO': 6}`
- 调用方可以用 `result = count_log_levels('sample.log')` 接住
- 如果不return，计分板就锁在函数里面，外面的人（Day 5生成报告）看不到

### 其他新增代码逐词

- `counter.items()` = 把字典拆成键值对列表

  - 比如 `{'ERROR': 10, 'INFO': 6}.items()` → `[('ERROR', 10), ('INFO', 6)]`
  - 每次循环取出一对 `(level, count)`

- `\n` = 换行符（让统计结果和上面隔开一行）
- `return {}` = 文件不存在时返回空字典（不是None，保证调用方拿到的一定是字典）

### 记忆骨架（Day 3 在 Day 2 基础上新增的部分）

````
准备    → counter = {}                                    ← 新
...（Day 2一样）...
计数    → counter[level] = counter.get(level, 0) + 1      ← 新
...
输出    → for level, count in counter.items():              ← 新
          →     print(f"{level}: {count}次")
返回    → return counter                                   ← 新
````

### 关键认知纠正

- `re.search()` 没找到返回的是 `None`，不是 `UNKNOWN`。UNKNOWN 是我们代码 else 分支贴的标签。
- `if match:` 能判断是因为：Match对象在if眼里是True，None在if眼里是False。
- `counter.get(level, 0)` 的 `0` 不能去掉，去掉后键不存在会报 KeyError。

### 统计结果验证

````
INFO: 6次（第1,2,6,11,15,19行）
WARNING: 4次（第3,8,13,17行）
ERROR: 10次（第4,5,7,9,10,12,14,16,18,20行）
合计：6+4+10 = 20行 ✅
````

### Git 提交

````
（待提交）Day 3: 实现日志级别统计（字典计数）
8f7145f Day 2：实现日志级别的提取（正则表达式+DEBUG扩展）
91f1a6b Day 1: 实现日志文件读取和打印功能
````

***

## 四、安全红线

- 上传GitHub/Dify前必须脱敏：无真实IP、主机名、内网信息
- .gitignore 必含：`.env` / `config.json` / `**/__pycache__` / `reports/`
- push前 `git status` + `git ls-files` 检查敏感文件
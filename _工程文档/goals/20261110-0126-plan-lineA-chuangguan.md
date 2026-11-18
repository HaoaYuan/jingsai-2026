# 线 A 编程闯关速成包 · 施工计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 11.30 编程闯关赛交付「闯关地图 + 8 关 + 限时模拟关」离线网页练习包和 3 节课教案，零基础学生课后自学可用。

**Architecture:** 单一生成脚本 `工具/生成关卡.py` 同时内嵌「页面引擎模板」和「全部关卡数据」，运行后产出 9 个关卡页 + 1 个地图页（共 10 个单文件 HTML）；`--verify` 模式实际运行每道编程任务的参考解法并与预期输出逐字比对。数据与引擎单一来源，改内容只改脚本重生成。

**Tech Stack:** Python 3 标准库（生成器）、原生 HTML/CSS/JS（ES2017 以内）、localStorage。

**Spec:** `goals/20261110-0055-three-track-courses.md`（§2 目标、§3 约束、§4 线 A、§5 验收）

## Global Constraints

- 本仓库**不是 git 仓库**：所有任务无 commit 步骤，以验证步骤收尾。
- 学生/参考代码只用 Python 3.9 兼容语法（实际只用 ≤3.6 特性：print、f-string/逗号拼接、input、int()、if/elif/else、for+range、len、索引、`//`、`%`）；不用函数、类、推导式、`match`；本机验证跑 3.14，兼容性靠语法清单保证。
- 网页：单文件 HTML（CSS/JS 全内嵌），**零外部请求**（生成文件中不得出现 `http://`、`https://`、`<script src=`、`<link `）；Windows 10 + Edge 离线打开。
- JS 语法上限 ES2017：禁用 `?.`、`??`、`Array.prototype.flat`、`Object.fromEntries`、可选链捕获等新特性。
- localStorage 键名前缀 `ck`，与既有 `pyNN_practice_v1` / `pyNNsup_practice_v1` 系列互不冲突；不登录、不上传任何数据。
- 网页不执行 Python：编程任务用「学生 IDLE 写码 → 粘贴运行结果 → 页面归一化比对」；格式检查只提示不判分。
- 页面不提前展示完整答案：三级提示第 3 级只给局部代码片段，完整参考解法只存在于生成脚本（教师工具）。
- 中文排版：全角标点，中英文/数字交界半角空格，破折号用 `--`；代码、变量名、文件名英文。
- 目录与命名：`编程闯关/index.html`、`编程闯关/关卡/level01.html`–`level08.html`、`编程闯关/关卡/final.html`、`编程闯关/第0N课_主题/教案.md`；链接相对路径：地图→关卡 `关卡/levelNN.html`，关卡→地图 `../index.html`。
- 每关只承载一个主知识点；基础任务不依赖选做。

## Review Focus

1. **粘贴输出带噪声**：尾部空行、行尾空格、CRLF、全角空格——比对必须归一化（逐行 strip ` \t　`、去掉末尾空行）后整串比对，否则正确答案被误判错。→ Task 2 步骤 4 的单测用例。
2. **学生误贴报错**：粘贴内容含 `Traceback` 时判定为「这是报错信息不是运行结果」，给针对性提示，绝不判通过。→ Task 2 步骤 4 用例。
3. **机房 Edge 兼容**：语法超限或意外外链导致白屏。→ Task 3 步骤 5 的 grep 检查（`?.`、`??`、`http`、`script src`）。
4. **localStorage 不可用**（机房公共机隐私模式）：页面不崩，顶部出现「进度无法保存，本页功能仍可用」横幅。→ Task 3 引擎初始化 try/catch + Task 6 抽查。
5. **误触重置丢进度**：地图页「重置进度」必须二次确认，确认文案写明「全部关卡记录将被清空」。→ Task 4 步骤 3。

## File Structure

```text
编程闯关/
├── 00_课程总览.md            # Task 1：3 课节奏 + 8 关序列 + 赛前安排
├── 00_制作规范.md            # Task 1：继承 Python基础 规范，写明差异（关卡制/ck 键/无课件/生成器）
├── index.html                # Task 4：闯关地图（生成器产出）
├── 关卡/level01..08.html     # Task 3：8 个关卡页（生成器产出）
├── 关卡/final.html           # Task 3：限时模拟关（生成器产出）
├── 第01课_认识IDLE与print/教案.md      # Task 5
├── 第02课_运算与判断/教案.md           # Task 5
├── 第03课_循环与综合/教案.md           # Task 5
└── 工具/生成关卡.py          # Task 2/3/4：引擎模板 + 关卡数据 + 参考解法 + verify（教师包专属）
```

### Task 1: 骨架与总纲文档

**Files:**
- Create: `编程闯关/00_课程总览.md`、`编程闯关/00_制作规范.md`

**Interfaces:**
- Produces: 全局 Constraints 的项目化落地版；后续所有任务的文案、键名、目录以这两份文档为准。

- [ ] **Step 1: 写 `00_制作规范.md`**
  结构参照 `Python基础/00_制作规范.md`，内容按本计划 Global Constraints 改写差异点：关卡制（顺序解锁 + `?unlock=1` 教师后门）、键名前缀 `ck`、无课件（教案 + 生成网页即全部材料）、`工具/生成关卡.py` 为内容唯一来源（改内容必须改脚本并重生成，不手改 HTML）、学生包 = `index.html` + `关卡/`，教师包另含 `工具/` + `教案.md`。
- [ ] **Step 2: 写 `00_课程总览.md`**
  必含表格：3 节课（第 1 课 IDLE/print/变量 → 第 2 课 运算/input/if → 第 3 课 for/综合，各 40 分钟）；8 关知识点序列（1 print与注释、2 变量与字符串、3 四则运算与 `//` `%`、4 input 与类型转换、5 if/elif/else、6 for 与 range、7 字符串索引与 len、8 综合）+ 限时模拟关；课后闯关节奏（第 1 课后做 L01–L03，第 2 课后 L04–L06，第 3 课后 L07–L08，赛前一周完成 final）；课程目标（独立写出 30 行以内基础程序、答对 Python 基础单选+判断题）；明确「赛制未通知，客观题按单选+判断、编程按输出核对通用准备，通知到达后校核」。
- [ ] **Step 3: 验证**
  自读两份文档：目录树、键名、关卡序列与本计划完全一致；无「待定」字样。

### Task 2: 关卡数据、参考解法与 --verify

**Files:**
- Create: `编程闯关/工具/生成关卡.py`

**Interfaces:**
- Produces（后续任务全部依赖）:
  - CLI：`python 工具/生成关卡.py` 输出 10 个 HTML 到正确路径并打印清单；`python 工具/生成关卡.py --verify` 先跑内容校验再生成，任何失败以非 0 退出。
  - 数据结构（脚本内 `LEVELS` 列表 + `FIN` 字典）：`{id:"L01", file:"level01.html", title, topic, obj:[{t:"single"|"judge", q, opts?, a:int|bool, why}], tasks:[{id:"T1", title, desc, input, starter, expect, hints:[三级], optional:bool}]}`；FIN 另有 `timeLimitMin:40`。
  - 参考解法：每道编程任务一段 `REF[tasks_id]` 源码字符串，`--verify` 用 `subprocess` 写临时 `.py`（放 `.tmp/`）以 stdin 喂入样例、比对 stdout 与 `expect`。

- [ ] **Step 1: 写关卡数据骨架**
  9 个数据块（L01–L08 + FIN）。客观题数量：每关 5 道（单选 4 + 判断 1；L08 全单选 5 道），FIN 10 道（单选 7 + 判断 3，覆盖 L1–L8）。客观题主题按关：L01 IDLE 操作与 print/注释/中文符号报错；L02 变量赋值/引号/print 逗号与 + 的区别/命名规则；L03 `/` 与 `//` 区别、`%`、行列换算、优先级；L04 input 返回字符串/int() 转换/int("abc") 报错；L05 冒号缩进/elif 顺序/`==` 与 `=`/and-or；L06 range(1,101) 不含 101/累加变量置 0/range 三参；L07 索引从 0 起/len()/负索引/IndexError；L08 读代码写输出 ×2/累乘逻辑/综合排查；FIN 混合覆盖。每题答案唯一、`why` 解释错误选项。
- [ ] **Step 2: 写编程任务与参考解法（预期输出逐字如下，`·` 表行界）**
  | 关 | 任务 | input(stdin) | expect |
  |---|---|---|---|
  | L01 T1 | 用 3 个 print 输出指定三行 | 无 | `你好，我是闯关新手`·`这是我的第一个程序`·`闯关开始` |
  | L02 T1 | 用变量 name="Python"、hobby="闯关"，逗号拼接输出两行 | 无 | `我在学 Python`·`我的爱好是 闯关` |
  | L03 T1 | 17 个像素每行摆 5 个，用 `//` 和 `%` 输出两行 | 无 | `能摆满 3 行`·`还剩 2 个` |
  | L04 T1 | 读入两行整数（7、3），输出和与差两行 | `7\n3` | `两个数的和是 10`·`两个数的差是 4` |
  | L05 T1 | score=78，90+优秀 / 80+良好 / 60+及格 / 否则不及格，输出一行 | 无 | `78 分的等级是：良好` |
  | L06 T1 | for 累加 1..100，输出一行 | 无 | `1 到 100 的总和是 5050` |
  | L06 T2(选做) | for + end=" " 输出乘法口诀第 3 行 | 无 | `3x1=3 3x2=6 3x3=9` |
  | L07 T1 | s="1011010"，输出三行：长度/第 3 个字符/最后一个字符 | 无 | `长度是 7`·`第 3 个字符是 1`·`最后一个字符是 0` |
  | L08 T1 | 读入一行整数 n（样例 5），for 累乘算阶乘，输出一行 | `5` | `5 的阶乘是 120` |
  | FIN TA | 读入两行整数（17、5），输出两行 | `17\n5` | `17 // 5 = 3`·`17 % 5 = 2` |
  | FIN TB | 输出 1~20 中所有 3 的倍数，每行一个，共 6 行 | 无 | `3`·`6`·`9`·`12`·`15`·`18` |
  每道任务配 `starter`（含注释骨架）、三级 hints（思路→步骤→局部代码，第 3 级只给关键 1–2 行）。
- [ ] **Step 3: 实现 --verify**
  逐题：写 `.tmp/chuangguan_verify/<id>.py` → `subprocess.run([sys.executable, path], input=stdin, capture_output=True, text=True, timeout=30)` → stdout 过归一化（见 Task 3 引擎同一套规则）后与 expect 相等，且 stderr 为空。断言失败时打印关卡/任务/期望/实际。
- [ ] **Step 4: 先写比对规则的自测（verify 模式内置 `--selftest`）**
  用例：`"a \n b\n\n"` ≡ `"a\nb"`（归一化）；`"你好，我是闯关新手\n这是我的第一个程序\n闯关开始"` ≡ 同（全等）；含 `Traceback` 的粘贴返回「报错」判定；全角空格 `　` 被 strip。`python 工具/生成关卡.py --selftest` 退出码 0。
- [ ] **Step 5: 验证**
  Run: `python 工具/生成关卡.py --verify`。Expected: 11 道任务全部 PASS（本机 Python 3.14 跑逻辑；3.9 兼容由 Step 1–2 语法清单保证）。

### Task 3: 关卡页引擎模板（生成 9 个关卡页）

**Files:**
- Modify: `编程闯关/工具/生成关卡.py`（新增引擎模板字符串 + 渲染函数）
- Create（生成）: `编程闯关/关卡/level01.html`–`level08.html`、`关卡/final.html`

**Interfaces:**
- Consumes: Task 2 的 `LEVELS`/`FIN`/CLI。
- Produces:
  - localStorage `ck_progress_v1` = `{"v":1,"unlocked":<int 1..9>,"stamps":{"L01":bool...},"obj":{"L01":{"q0":<optionIdx>}},"hints":{"L01":{"T1":<int>}},"final":{"started":false,"left":2400}}`；草稿键 `ck_draft_L01_T1_v1`（字符串）。FIN 解锁条件：L01–L08 全部盖章。
  - 页面区块顺序：关卡头（第 N 关 · 知识点）→ 客观题区（逐题作答，全部提交后统一判分+解析，可重做）→ 编程任务区（题面/input 样例/starter 只读展示 + 复制按钮 → 三级提示按钮（计数存 `hints`）→ 代码粘贴框 + 「格式检查（不判分）」+ 「核对输出」→ 通过后绿章）→ 通关区（客观题全对 + 必做任务全过 → 盖章动画 + 「下一关」链接）。
  - 行为规则：输出核对 = 归一化比对（Task 2 同一套规则）；粘贴含 Traceback → 专属提示；格式检查项 = 中文引号、`if/elif/else/for/while` 行尾冒号、Tab 空格混用、`&&`/`||`、圆括号配对；草稿框 `input` 事件写 `ck_draft_*_v1`；导出 `.py`（Blob 下载，文件名 `L01_T1.py`）；localStorage 读写全部 try/catch，不可用时顶部横幅「进度无法保存，本页功能仍可用」；FIN 页加载即倒计时 40:00，归零后锁全部输入并显示「时间到，对照解析自查」。
  - 视觉：与 `Python基础/index.html` 同风格体系（配色/字体/圆角），关卡化变体（进度章、关卡色条）；字号 ≥ 16px 正文、代码 14px 等宽。

- [ ] **Step 1: 实现引擎模板 + 渲染函数**（模板 = HTML 骨架 + `<script>` 内 `PAGE_DATA` 注入 + 引擎 JS；引擎 JS 一次写好、9 页共用）
- [ ] **Step 2: 生成并跑通 `python 工具/生成关卡.py --verify`**：打印 10 个文件路径 + 11 任务 PASS。
- [ ] **Step 3: 引擎行为抽查（读生成文件核对）**：任取 level05.html 与 final.html，确认 `ck_` 键名、三级提示、格式检查、FIN 倒计时、通关条件代码存在且 `PAGE_DATA` 与数据一致。
- [ ] **Step 4: 兼容与离线 grep**
  Run: `grep -nE "https?://|<script src=|<link |\?\.|\?\?" 编程闯关/关卡/*.html 编程闯关/index.html`（Task 4 完成后一并复跑）。Expected: 无匹配。
- [ ] **Step 5: 验证 localStorage 防护**：临时在浏览器禁用站点存储不可行时，以代码审读替代——确认所有 `localStorage` 调用均在 try/catch 内，无裸调用。

### Task 4: 闯关地图 index.html

**Files:**
- Modify: `编程闯关/工具/生成关卡.py`（地图模板）
- Create（生成）: `编程闯关/index.html`

**Interfaces:**
- Consumes: `ck_progress_v1`（Task 3 schema）、9 个关卡页相对路径 `关卡/*.html`。
- Produces: 地图页状态渲染规则——每关一格：锁定（灰）/ 已解锁未过（亮，可点）/ 盖章（星章）；FIN 特殊显示为「终极模拟 · 40 分钟」；`?unlock=1` 读到后写 `unlocked:99` 并提示「教师模式：已解锁全部关卡」；「重置进度」按钮 → confirm 二次确认（文案含「全部关卡记录将被清空」）→ 清 `ck_` 前缀全部键。

- [ ] **Step 1: 实现地图模板**（同生成器产出；10 文件清单输出含 index.html）
- [ ] **Step 2: 重新生成并跑 `python 工具/生成关卡.py --verify`**
- [ ] **Step 3: 行为核对（读生成文件）**：解锁/盖章/锁定三态、`?unlock=1`、重置二次确认、到 `关卡/level01.html` 与回链 `../index.html` 的相对路径正确。
- [ ] **Step 4: 复跑 Task 3 Step 4 的离线 grep（含 index.html）**。Expected: 无匹配。

### Task 5: 三份教案

**Files:**
- Create: `编程闯关/第01课_认识IDLE与print/教案.md`、`第02课_运算与判断/教案.md`、`第03课_循环与综合/教案.md`

**Interfaces:**
- Consumes: `Python基础/第01讲_你好Python/教案.md` 的结构（目标/40 分钟流程/板书/常见错误/答案解析/参考代码/作业）；关卡数据中对应关卡的题目即课堂例题来源。

- [ ] **Step 1: 写三份教案**
  每份必含：40 分钟分段（复习 5 / 新知 15 / 动手 15 / 小结与作业布置 5，可按课微调但各段目标固定）、板书要点、常见错误（第 1 课：中文标点/路径含中文/忘保存；第 2 课：int 忘转换、`=` 与 `==`、`/` 结果带小数；第 3 课：range 边界、累加变量位置）、参考代码（与对应关卡任务同源，逐字可跑）、作业 = 对应课后关卡清单（第 1 课→L01–L03，第 2 课→L04–L06，第 3 课→L07–L08，第 3 课另布置赛前完成 final）。
- [ ] **Step 2: 验证**：教案内参考代码逐段粘到临时文件实跑，输出与关卡 `expect` 一致（可复用 Task 2 的验证思路抽查）。

### Task 6: 终检与仓库文档

**Files:**
- Create: `ROADMAP.md`（仓库根，新建）
- Modify: `AGENTS.md`（仅过时项）

- [ ] **Step 1: 全量重跑 `python 工具/生成关卡.py --verify` 与离线 grep**（含 index.html）。Expected: 全绿。
- [ ] **Step 2: 学生包隔离检查**：`grep -rn "参考解法\|REF\[" 编程闯关/关卡 编程闯关/index.html` 无匹配；生成页内无任何任务的完整答案代码（提示第 3 级只含局部行）。
- [ ] **Step 3: Edge 实开抽查**：`start` 打开 `编程闯关/index.html` 与 `关卡/level01.html`、`final.html`，人工核对三态渲染、判分、提示、粘贴核对、倒计时各一次；发现问题回对应任务修。
- [ ] **Step 4: 写仓库 `ROADMAP.md`**（北京时间戳）：线 A 全部完成并记录验证方式与结果；线 B、C 状态「设计已批、施工未开始」。
- [ ] **Step 5: 更新 `AGENTS.md` 过时项**：`Python基础/` 与 `图形识别/以往教程/` 不再是空占位；新增 `编程闯关/`（线 A 材料与 `工具/生成关卡.py` 单一来源约定）、`大数分解/` 现状（散装 docx + 待建课程）；不删既有正确内容。

## Self-Review 结论

- 规格覆盖：设计 §4 线 A 全部条目（目录树、关卡序列、每关构成、通关规则、教师后门、模拟关、3 课教案、总览/规范）均有对应任务；§5 验收 1–6 落在 Task 2/3/4/6 的验证步骤；§5.7 的 ROADMAP/AGENTS 在 Task 6。
- 步骤可执行性：每步只产出一个明确产物；题目文案属 implementer 自由度（主题已 pin），预期输出逐字 pin。
- 接口一致：`ck_progress_v1` schema、CLI 行为、归一化规则在 Task 2/3/4 间引用一致；`--selftest` 只在 Task 2 定义、Task 3+ 复跑。
- Review Focus 五项均落到 owning task（1→T2S4，2→T2S4+T3，3→T3S4，4→T3S5，5→T4S3）。
- 比例：计划约 180 行 < 生成物规模，无代码转写。

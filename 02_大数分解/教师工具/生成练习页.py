#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成练习页.py -- 大数分解课程 5 个练习.html 的唯一内容源（教师包专属）。

用法：
    python 生成练习页.py             # 全量重生成 5 个练习页
    python 生成练习页.py --verify    # 实跑全部参考解法，比对预期输出
    python 生成练习页.py --selftest  # 引擎自检（归一化、转义、数据一致性）

约定：改题只改本文件数据区后重新生成，绝不手改任何 HTML（见 00_制作规范.md §5）。
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TRACK_ROOT = Path(__file__).resolve().parent.parent   # 02_大数分解/
COURSE_ROOT = TRACK_ROOT / "练习与模拟"

# ============================================================
# 数据区：5 讲全部题目、任务、提示、参考解法
# ============================================================

LESSONS = [
    {
        "nn": "01",
        "dirname": "Python基础速通",
        "title": "Python 基础速通",
        "intro": "这一讲从零开始：只要会开机打字，就能学会 Python 最常用的六个句型。比赛要用的分解程序，就是这六件事拼起来的。",
        "obj": [
            {
                "kind": "single",
                "q": "执行 print(\"2+3\")，屏幕上显示什么？（注意 2+3 外面有引号）",
                "opts": ["5", "2+3", "23", "报错"],
                "a": 1,
                "why": "引号里的内容会被原样显示，Python 不会帮你计算。想让它算出 5，要去掉引号写 print(2 + 3)。引号包住的叫字符串，只管显示；不带引号的才算数。",
            },
            {
                "kind": "single",
                "q": "表达式 7 // 2 的值是？",
                "opts": ["3.5", "3", "2", "4"],
                "a": 1,
                "why": "// 是整除：取商、丢掉余数，7 // 2 = 3。余数用 % 算：7 % 2 = 1。分解程序里就靠这一对搭档：n % i == 0 判断「i 是不是 n 的因数」，n = n // i 表示「把因子 i 除掉」。",
            },
            {
                "kind": "single",
                "q": "读入一行并把它变成整数 n，正确的写法是？",
                "opts": ["n = input()", "n = int(input())", "n = input(int())", "int n = input()"],
                "a": 1,
                "why": "input() 读到的永远是字符串（文字），字符串不能做算术。必须套一层 int() 把它变成整数，写 n = int(input())。",
            },
            {
                "kind": "single",
                "q": "写 if n % 2 == 0 时行末忘了冒号，运行会怎样？",
                "opts": ["TypeError", "SyntaxError", "ZeroDivisionError", "不报错，正常运行"],
                "a": 1,
                "why": "冒号是 Python 语法的一部分，if、for、while、def 的行末都要有英文冒号，漏了会报 SyntaxError（语法错误）并指出那一行。缩进不对报 IndentationError，除以零报 ZeroDivisionError。",
            },
            {
                "kind": "blank",
                "q": "让 i 从 1 数到 n（含 n），循环头写作 for i in ____（只写 range 那一段，不要空格）",
                "a": "range(1,n+1)",
                "accept": ["range(1,n+1)"],
                "why": "range(起, 止) 从「起」数到「止的前一个」，所以要数到 n 必须写 range(1, n + 1)。写 range(1, n) 会把 n 自己漏掉--枚举因数时 n 本身也是因数，漏不得。",
            },
            {
                "kind": "blank",
                "q": "17 除以 5 的余数，用 Python 表达式写作____（不要空格）",
                "a": "17%5",
                "accept": ["17%5"],
                "why": "% 是取余：17 % 5 = 2。比较的结果是 True 或 False（首字母大写），print(17 % 5 == 2) 会显示 True。",
            },
        ],
        "tasks": [
            {
                "id": "T1",
                "title": "和与差",
                "input": "10 3",
                "desc": "读入一行，里面有空格隔开的两个整数 a 和 b。第一行输出它们的和，第二行输出它们的差（a - b）。这一题练「输入 + 输出」两个句型。",
                "starter": "s = input()\na, b = s.split()\n# 第 1 步：把 a 和 b 都变成整数（用 int）\n# 第 2 步：第一行打印 a + b，第二行打印 a - b\n",
                "expect": "13\n7",
                "hints": [
                    "split() 按空格把一行拆成两份，但拆出来的还是字符串（文字），文字不能做加法。",
                    "a = int(a) 和 b = int(b)，各转一次。",
                    "print(a + b) 和 print(a - b) 各写一行。",
                ],
                "optional": False,
            },
            {
                "id": "T2",
                "title": "奇偶判断",
                "input": "8",
                "desc": "读入一个整数 n。如果它是偶数，输出 yes；否则输出 no。这一题练「判断」句型。",
                "starter": "n = int(input())\n# 第 1 步：用 % 判断 n 除以 2 余数是不是 0（余 0 就是偶数）\n# 第 2 步：偶数打印 yes，否则打印 no（记得行末冒号和缩进）\n",
                "expect": "yes",
                "hints": [
                    "偶数就是能被 2 整除：n % 2 == 0。",
                    "if n % 2 == 0: 下一行缩进 4 格，写 print(\"yes\")。",
                    "else: 下一行缩进写 print(\"no\")。",
                ],
                "optional": False,
            },
            {
                "id": "T3",
                "title": "1 到 n 求和（选做）",
                "input": "100",
                "desc": "读入整数 n，输出 1 + 2 + …… + n 的结果。这一题练「循环累加」句型--它就是分解程序的发动机。",
                "starter": "n = int(input())\ntotal = 0\n# 第 1 步：让 i 从 1 数到 n（用 range，注意数到 n 要 n + 1）\n# 第 2 步：每数一个 i，就把它加进 total\n# 循环结束后打印 total\n",
                "expect": "5050",
                "hints": [
                    "for i in range(1, n + 1): 让 i 依次取 1, 2, 3, ……, n。",
                    "循环体（缩进 4 格）里写 total = total + i。",
                    "循环写完后（顶格），print(total)。",
                ],
                "optional": True,
            },
        ],
    },
    {
        "nn": "02",
        "dirname": "因数分解实战",
        "title": "因数分解实战",
        "intro": "上一讲学会了六大句型，这一讲把它们拼成真正的分解程序。先不急着写代码：什么是因数、什么是质数，先用手算弄明白，再让计算机替我们除。这一讲的胜负手是输出格式--评委按格式给分，多一个空格少一个 × 都扣分。",
        "obj": [
            {
                "kind": "single",
                "q": "试除法输出 n 的全部因数（含 1 和 n 本身），循环范围应该写成？",
                "opts": ["range(1, n)", "range(1, n + 1)", "range(2, n)", "range(n)"],
                "a": 1,
                "why": "n 本身也是 n 的因数，上界要取到 n + 1。range(n) 更危险：从 0 开始，第一次 n % 0 直接报 ZeroDivisionError。",
            },
            {
                "kind": "single",
                "q": "质因数分解 180 = 2 × 2 × 3 × 3 × 5，循环里的正确做法是？",
                "opts": [
                    "n % i == 0 时反复除 i，除不尽了才让 i 加 1",
                    "n % i == 0 时除一次就马上让 i 加 1",
                    "i 从 n 往下倒着除回来",
                    "i 只需要试到 9 就够了",
                ],
                "a": 0,
                "why": "除一次就 i 加 1 会漏掉重复因子：4 = 2 × 2，除掉一个 2 后还能再除一个 2。短除法的核心就是「同一个因子除到不能再除」。倒着除顺序错且慢；i 要试到 √n。",
            },
            {
                "kind": "single",
                "q": "n = 360 = 2³ × 3² × 5，它的全部因数个数（含 1 和 360）是？",
                "opts": ["12", "24", "18", "360"],
                "a": 1,
                "why": "因数个数定理：(指数 + 1) 连乘 -- (3+1) × (2+1) × (1+1) = 4 × 3 × 2 = 24。也可写程序数一遍验证：枚举 1 到 360，是因数就计数，正好数出 24 个。数学公式和程序互相印证，评委问「怎么确认结果对」就这样答。",
            },
            {
                "kind": "single",
                "q": "要统计 n 的所有因数中偶因数的个数，最直接的思路是？",
                "opts": [
                    "枚举 i：n % i == 0 成立且 i % 2 == 0 时计数加 1",
                    "枚举 i：只要 n % 2 == 0 就计数加 1",
                    "把 n 除以 2，看还能除几次",
                    "只枚举奇数 i，用总数减去它",
                ],
                "a": 0,
                "why": "「n % i == 0」筛因数、「i % 2 == 0」筛偶性，两个条件同时满足才计数。B 判断的是 n 的奇偶不是因数的；C 数的是 2 的幂次；D 绕远路还容易错。",
            },
            {
                "kind": "blank",
                "q": "质因数分解中，把因子 i 除掉后更新 n 的语句是：n = ____（不要空格）",
                "a": "n//i",
                "accept": ["n//i"],
                "why": "整除更新用 //。写成 n = n / i 会得到小数，后面的 % 运算全部报错。",
            },
            {
                "kind": "blank",
                "q": "180 的所有因数中，最大的质因数是____（填数字）",
                "a": "5",
                "accept": ["5"],
                "why": "180 = 2 × 2 × 3 × 3 × 5，质因子有 2、3、5，最大是 5。注意最大质因数不等于最大因数（最大因数是 180 本身）。",
            },
        ],
        "tasks": [
            {
                "id": "T1",
                "title": "质因数分解",
                "input": "180",
                "desc": "读入整数 n（2 ≤ n ≤ 10^9，可能是质数），输出一行质因数分解式，格式逐字符照抄：n = 因子1 × 因子2 × ……（因子从小到大，乘号两侧各一个空格）。",
                "starter": "n = int(input())\nm = n\nparts = []\ni = 2\nX = \" × \"\n# 第 1 步：写外层循环--只要 i * i 不超过 m 就继续找（while 条件自己写）\n\n\n# 第 2 步：写内层循环--m % i == 0 成立就反复除同一个 i：\n#         把 i 存进 parts（用 str(i) 存文字），再把 m 整除更新（// 不是 /）\n\n\n# 第 3 步：内层结束后换下一个候选：i 加 1（注意少一层缩进）\n# 第 4 步：外层结束后，m 还大于 1 就把 m 也存进 parts（质数边界）\n# 第 5 步：拼输出：print(str(n) + \" = \" + X.join(parts))\n",
                "expect": "180 = 2 × 2 × 3 × 3 × 5",
                "hints": [
                    "先手算一遍 180：除 2 两次、除 3 两次、除 5 一次，正好除到 1。程序就是把这套动作自动化：外层循环负责「换下一个候选因子 i」，内层循环负责「把同一个 i 除到不能再除」。",
                    "两个句型套起来用：外层 while i * i <= m:，内层 while m % i == 0:。内层循环体（缩进 8 格）写两行：parts.append(str(i)) 和 m = m // i；内层写完后退回 4 格写 i = i + 1。",
                    "质数边界和输出：外层循环结束后（顶格）写 if m > 1: parts.append(str(m))，最后一行 print(str(n) + \" = \" + X.join(parts))。X 就是 starter 里的「 × 」，join 的意思是「用 X 把 parts 里的每一段连起来」。",
                ],
                "optional": False,
            },
            {
                "id": "T2",
                "title": "成分提取与统计",
                "input": "180",
                "desc": "读入整数 n（2 ≤ n ≤ 10^6），输出三行：第一行是偶因数的个数，第二行是奇因数之和，第三行是最大质因数。",
                "starter": "n = int(input())\neven_count = 0\nodd_sum = 0\n# 第 1 部分：枚举 1 到 n，把因数挑出来分两类统计\n# 第 1 步：写循环 while i <= n:（别忘了先给 i 起始值 1）\n# 第 2 步：循环里先判断是不是因数：if n % i == 0:\n# 第 3 步：是因数再分偶奇：偶数（i % 2 == 0）计数加 1，否则加进奇因数和\n\n\n# 第 4 步：循环末尾让 i 加 1\n# 第 2 部分：短除法找最大质因数（T1 同款，只是不存每个因子）\nm = n\nmax_prime = 0\ni = 2\n\n\n# 第 5 步：写短除法双循环，内层里记 max_prime = i 并整除更新 m\n# 第 6 步：循环结束后 m > 1 就令 max_prime = m\n# 第 7 步：打印三行：even_count、odd_sum、max_prime\n",
                "expect": "12\n78\n5",
                "hints": [
                    "分两部分做：第一部分用循环枚举 1 到 n 挑因数，偶的计数、奇的求和；第二部分把 T1 的短除法搬过来，只是不用存每个因子，只记住最后除掉的那个 i。",
                    "第一部分：while i <= n: 里套 if n % i == 0:，里面再套 if i % 2 == 0: even_count = even_count + 1，else: odd_sum = odd_sum + i；循环末尾 i = i + 1。第二部分：while i * i <= m: 套 while m % i == 0:，内层写 max_prime = i 和 m = m // i。",
                    "短除法结束后（顶格）写 if m > 1: max_prime = m。最后三行各打印一个：print(even_count)、print(odd_sum)、print(max_prime)。输入 180 应该输出 12、78、5。",
                ],
                "optional": False,
            },
            {
                "id": "T3",
                "title": "因数个数与总和（选做）",
                "input": "180",
                "desc": "读入整数 n（2 ≤ n ≤ 10^6），输出两行：第一行是全部因数的个数，第二行是全部因数之和。",
                "starter": "n = int(input())\n# 枚举 1 到 n，是因数就计数并累加\n",
                "expect": "18\n546",
                "hints": [
                    "两个累加器：count 和 total，n % i == 0 时同时更新。",
                    "180 的因数有 18 个，总和 546，可以先对答案。",
                    "想更快：只枚举到 √n，每找到一对因子 d 和 n // d 同时累加，注意 n 是完全平方数时 √n 只算一次。",
                ],
                "optional": True,
            },
        ],
    },
    {
        "nn": "03",
        "dirname": "双算法效率对比",
        "title": "双算法效率对比",
        "intro": "评分核心「算法效率探究与优化 20 分」的前半场：把三种试除法一版一版讲透--朴素、优化（√N、跳偶）、6k±1，每一版只改上一版的几行。三版都学会，再跑实验一给三档大数计时，用数据证明「快」。批处理与埃氏筛在下一讲。",
        "obj": [
            {
                "kind": "single",
                "q": "实验要客观记录程序耗时，Python 里推荐的计时函数是？",
                "opts": [
                    "time.perf_counter()（高精度、不受系统时间调整影响）",
                    "time.sleep()",
                    "print() 自己的输出时间",
                    "input() 等待输入的时间",
                ],
                "a": 0,
                "why": "perf_counter 是专为测耗时设计的单调高精度时钟。time.time() 也能凑合，但系统时间被调整时它会跳，实验数据就不干净了。",
            },
            {
                "kind": "single",
                "q": "「控制变量」在效率实验里具体指什么？",
                "opts": [
                    "两种算法用同一组数字、同一台电脑、同样的重复次数，只有算法不同",
                    "把测试数字控制得很小，免得跑太久",
                    "两种算法的变量名保持一致",
                    "每个数字只测一次，节省时间",
                ],
                "a": 0,
                "why": "评分表原文要求「控制变量对比两种算法的效率差异」。任务相同、数据相同、环境相同，只留算法一个变量，快慢才能归因给算法本身。",
            },
            {
                "kind": "single",
                "q": "分解 10^12 级别的质数，朴素试除要从 2 试到 n 本身，约 10^12 次除法。Python 每秒约几千万次运算，需要的耗时量级是？",
                "opts": ["几秒", "几分钟", "几小时到几天", "一百年"],
                "a": 2,
                "why": "10^12 ÷ 3×10^7 ≈ 33000 秒 ≈ 9 小时起步。所以大档位朴素版直接超时，如实记录「>30 秒未出结果」也是客观记录--这正是评分表要的「客观记录」。",
            },
            {
                "kind": "single",
                "q": "同一任务同一电脑，优化版 0.08 秒、朴素版超过 30 秒没出结果。最规范的结论句是？",
                "opts": [
                    "优化版快多了，肯定选它",
                    "在 10^12 档位，优化试除 0.08 秒出结果，朴素试除超过 30 秒未出结果；原因是操作次数从约 10^12 降到约 10^6",
                    "朴素算法是错误的算法",
                    "Python 语言太慢了",
                ],
                "a": 1,
                "why": "结论要有三要素：条件（档位、环境）、数据（双方耗时）、原因（操作次数差异）--对应评分表「总结优化策略及其数学原理，结论可信、数据真实」。A 没数据；C 错误--朴素版结果一样对，只是慢；D 归因错了。",
            },
            {
                "kind": "blank",
                "q": "6k±1 试除中，处理完 i 和 i+2 两个位置后，i 要跳到下一个 6 的倍数：i = ____（写完整表达式，不要空格）",
                "a": "i=i+6",
                "accept": ["i=i+6", "i+=6"],
                "why": "两步铺垫：第一步先跳偶（i += 2）--除完 2 之后 n 是奇数，奇数不可能有偶数因子，候选 3,5,7,9… 每次迈 2 步。第二步再看数轴：9,15,21 是 3 的倍数、必已被 3 除过，所以候选只剩 6k−1 与 6k+1 两种位置，每轮检查 i 和 i+2 后 i = i + 6。",
            },
            {
                "kind": "blank",
                "q": "同一组计时重复跑 3 次，应取其中____值作为该算法的耗时（填：最大 / 最小 / 平均）",
                "a": "最小",
                "accept": ["最小"],
                "why": "取最小值是为了排除系统偶发卡顿（后台程序、调度抖动）的干扰，最快那次最能代表算法本身的潜力。",
            },
        ],
        "tasks": [
            {
                "id": "T1",
                "title": "优化试除判质数",
                "input": "1000000007",
                "desc": "读入整数 n（2 ≤ n ≤ 10^12）。用优化试除（先除 2，再只试 3、5、7…到 √n）判断它是质数还是合数：质数输出 yes，合数输出 no。这就是实验一的「优化版」本体，写对它再去跑三档计时。",
                "starter": "n = int(input())\nanswer = \"yes\"\n# n 是 2：直接 yes；n 是大于 2 的偶数：直接 no\n# 否则 i = 3, 5, 7, ... 试到 i * i <= n\n# 用 found 记录有没有找到因子，替代 break\n",
                "expect": "yes",
                "hints": [
                    "先做两个特判：n 是 2 直接 yes；n 是大于 2 的偶数直接 no。剩下的 n 都是奇数，从 3 开始试。",
                    "用「判断 + 循环」句型：while i * i <= n and not found:（只试到 √n，因为因子成对，小的那个总在 √n 以内）；里面 if n % i == 0: 就把 answer 改成 no、found 改成 True。",
                    "循环末尾 i = i + 2（跳偶：奇数没有偶数因子，候选只走 3,5,7…）；循环结束后顶格 print(answer)。1000000007 要试到约 31623 才停。",
                ],
                "optional": False,
            },
            {
                "id": "T2",
                "title": "6k±1 试除判质数",
                "input": "1000000007",
                "desc": "同样的任务、更快的一版：除 2、3 特判后，从 i = 5 开始只试 6k−1 和 6k+1 两个位置（5 和 7、11 和 13……）。质数输出 yes，合数输出 no。和 T1 用同一个输入核对，体会「同任务双算法」。",
                "starter": "n = int(input())\nanswer = \"yes\"\n# 特判：n 是 2 或 3 直接 yes；n 是 2 或 3 的倍数直接 no\n# i = 5 开始，每轮检查 n % i == 0 或 n % (i + 2) == 0\n# 然后 i = i + 6\n",
                "expect": "yes",
                "hints": [
                    "特判两条：n 是 2 或 3 直接 yes；n 是 2 或 3 的倍数直接 no。剩下的候选从 5 开始。",
                    "为什么候选是 5,7、11,13、17,19…？看 6k±1 数轴：偶数和 3 的倍数（9,15,21…）都早被除过了，只剩 6k−1 和 6k+1 两种位置。一轮检查两个：if n % i == 0 or n % (i + 2) == 0:。",
                    "一轮查完两个位置后 i = i + 6，跳到下一对；最后 print(answer)。和 T1 用同一个输入核对：1000000007 → yes。",
                ],
                "optional": False,
            },
        ],
    },
    {
        "nn": "04",
        "dirname": "埃氏筛与批处理加速",
        "title": "埃氏筛与批处理加速",
        "intro": "上一讲把三种试除讲透了，这一讲解决「一批数」：先用埃氏筛造一张素数表，再让批处理分解快 2~3.5 倍。老规矩：先手算后代码，两方案输出完全一致才算数。",
        "obj": [
            {
                "kind": "single",
                "q": "埃氏筛划掉倍数时，为什么从 p × p 开始划，而不是从 p × 2 开始？",
                "opts": [
                    "从 p × p 开始划更快，因为更小的倍数（p × 2、p × 3……）已经被更小的素数划过了",
                    "从小倍数开始划会漏掉质数",
                    "p × p 是第一个合数，后面都不是",
                    "没有原因，习惯写法",
                ],
                "a": 0,
                "why": "筛到 p 时，比 p × p 更小的 p 的倍数（如 p × 2 里的 2 已划掉它们）早就被更小的素数划掉了。从 p × p 开始既不漏也不重复，这是埃氏筛「快」的细节之一。",
            },
            {
                "kind": "single",
                "q": "筛法跑完后，flags[v] 还是 True（没被划掉），说明 v 是？",
                "opts": ["质数", "合数", "1", "偶数"],
                "a": 0,
                "why": "埃氏筛把每个质数的倍数全部划掉，剩下没被划掉的就是质数。flags[v] 为 True 表示 v 没有更小的质因子--它就是质数。",
            },
            {
                "kind": "single",
                "q": "实验二比较「逐个试除」和「先筛再只除素数」时，最重要的正确性护栏是？",
                "opts": [
                    "两方案的输出逐行完全一致，提速才可信",
                    "提速倍数越大越不用管对错",
                    "方案 B 是书上写的，肯定正确",
                    "多跑几次取平均",
                ],
                "a": 0,
                "why": "评分表要求「结论可信、数据真实」。「输出逐行一致」证明加速没有牺牲正确性；如果输出不一致，说明算法写错了，提速数据作废。",
            },
            {
                "kind": "single",
                "q": "方案 B（先筛再分解）比方案 A（逐个试除）快的根本原因是？",
                "opts": [
                    "只除素数表里的素数，合数候选全部跳过，每个数除的次数大幅减少",
                    "方案 B 的代码行数更少",
                    "方案 B 不用循环",
                    "方案 B 的变量名更短",
                ],
                "a": 0,
                "why": "逐个试除要把 4、6、8、9 这些合数候选都除一遍；只除素数后，候选少一半以上（30 以内只剩 10 个素数）。一次建表、处处复用，批处理时优势最大。",
            },
            {
                "kind": "blank",
                "q": "埃氏筛内层「划掉下一个倍数」的更新语句是：multiple = multiple + ____（一个字母）",
                "a": "p",
                "accept": ["p"],
                "why": "每划掉一个倍数，就跳到下一个倍数：multiple = multiple + p（p 是当前素数）。注意不是 + 1--那是把每个数都划掉了。",
            },
            {
                "kind": "blank",
                "q": "30 以内（含 30）共有____个质数（填数字）",
                "a": "10",
                "accept": ["10"],
                "why": "2, 3, 5, 7, 11, 13, 17, 19, 23, 29--共 10 个。这就是课堂手筛的结果，也是 flags 表数出来的结果。",
            },
        ],
        "tasks": [
            {
                "id": "T1",
                "title": "批处理分解（先写对）",
                "input": "3\n12\n97\n100",
                "desc": "模拟实验二的批处理：第一行读个数 m，后面 m 行每行一个整数，逐个输出质因数分解式（格式同第 02 讲 T1：n = 因子 × 因子……）。这是「先写对，再加速」的基本功。",
                "starter": "m = int(input())\nk = 0\nwhile k < m:\n    n = int(input())\n    # 对这个 n 做质因数分解并按格式输出一行\n    k = k + 1\n",
                "expect": "12 = 2 × 2 × 3\n97 = 97\n100 = 2 × 2 × 5 × 5",
                "hints": [
                    "把第 02 讲 T1 的分解代码放进 while k < m 循环体里，每次处理一个新读入的 n。",
                    "别忘了质数边界：内层分解结束后剩下的 m 大于 1 也要 append。",
                    "每处理完一个数立刻输出一行，不要攒到最后。",
                ],
                "optional": False,
            },
            {
                "id": "T2",
                "title": "埃氏筛：数素数个数",
                "input": "30",
                "desc": "读入整数 n（2 ≤ n ≤ 10^6），输出 n 以内（含 n）质数的个数。这就是埃氏筛的本体：先造素数表，再数一数。",
                "starter": "n = int(input())\nflags = [True] * (n + 1)   # flags[v] 为 True 表示「v 还没被划掉」\nflags[0] = False\nflags[1] = False\n# 第 1 步：外层循环，p 从 2 试起，只要 p * p <= n 就继续（while 条件自己写）\n\n\n# 第 2 步：p 没被划掉（flags[p] 为 True）才需要划它的倍数\n\n\n# 第 3 步：内层从 multiple = p * p 开始，把不超过 n 的倍数全部划掉（每次加 p）\n\n\n# 第 4 步：别忘了外层末尾 p = p + 1\n# 第 5 步：数一数 2 到 n 里还有多少个 True，打印个数\n",
                "expect": "10",
                "hints": [
                    "先想手筛 30 的过程：从 2 开始，把每个没被划掉的数的倍数划掉。程序里 flags[v] 为 True 表示没被划掉。",
                    "外层 while p * p <= n:，里面 if flags[p]: 才划；内层 multiple = p * p，while multiple <= n: 把 flags[multiple] 改成 False，每次 multiple = multiple + p。",
                    "数个数：count = 0，v 从 2 到 n，if flags[v]: 就 count = count + 1；最后 print(count)。输入 30 应该输出 10。",
                ],
                "optional": False,
            },
        ],
    },
    {
        "nn": "05",
        "dirname": "报告与全真模拟",
        "title": "报告与全真模拟",
        "intro": "对准评分表「问题描述 10 + 项目分析报告 20 + 现场成果分享 5」。数据/ 里有 PPT 六页框架、流程图规范、陈述脚本骨架、全真模拟卷和自评清单--比赛当天 120 分钟的每一步，今天先走一遍。",
        "obj": [
            {
                "kind": "single",
                "q": "评分表「数字分解与处理 15 分」里，程序写对之后最容易被忽视的得分点是？",
                "opts": [
                    "输出完整、格式规范",
                    "代码越短越好",
                    "用最复杂的算法显得厉害",
                    "注释越多越好",
                ],
                "a": 0,
                "why": "评分表原文明确写「输出完整、格式规范」。分解对了、格式错了，分数照扣--第 02 讲的格式三查要带进赛场。",
            },
            {
                "kind": "single",
                "q": "流程图里「n % i == 0?」这样的判断分支，规范的画法是？",
                "opts": [
                    "菱形判断框，两个出口分别标「是」「否」",
                    "矩形处理框，出口不标注",
                    "平行四边形输入输出框",
                    "圆角矩形起止框",
                ],
                "a": 0,
                "why": "判断用菱形、双出口标「是 / 否」；输入输出用平行四边形；处理用矩形；起止用圆角矩形。判断框不标「是 / 否」是流程图最常见的扣分点。",
            },
            {
                "kind": "single",
                "q": "5 分钟陈述的时间分配，最合理的是？",
                "opts": [
                    "开场 30 秒 + 算法讲解 90 秒 + 数据展示 90 秒 + 优化原理 60 秒 + 收尾 30 秒",
                    "开场自我介绍 3 分钟，后面赶着念完",
                    "全程逐行念代码，数据一笔带过",
                    "数据展示部分省略，只讲想法",
                ],
                "a": 0,
                "why": "时间控制本身就是评分项。数据展示是评委最想听的段（「效率探究」20 分的证据），90 秒必须给足；收尾不超时体现时间控制能力。",
            },
            {
                "kind": "single",
                "q": "评委追问「你们还能再优化吗？」，最好的回应是？",
                "opts": [
                    "拍胸脯说我们的方案已经最优",
                    "如实说明已做优化的原理与量级，再诚实指出更高阶的算法（如概率型算法）超出中学范围，是我们想继续学习的方向",
                    "说不知道，请评委指教",
                    "转移话题讲别的",
                ],
                "a": 1,
                "why": "评分要求「能准确回应评委问题」。知道边界在哪、如实说出来，比夸大更可信--报告评分同样要求「结论可信、数据真实」。",
            },
            {
                "kind": "blank",
                "q": "流程图中表示「输入 / 输出」的框，形状名称是____（填五个字）",
                "a": "平行四边形",
                "accept": ["平行四边形"],
                "why": "输入输出用平行四边形、判断用菱形、处理用矩形、起止用圆角矩形--四种形状记牢，画一张规范的流程图就是「问题描述 10 分」的主力。",
            },
            {
                "kind": "blank",
                "q": "任务一的分解程序，输出格式必须与题面模板____一致（填两字）",
                "a": "完全",
                "accept": ["完全", "逐字", "严格"],
                "why": "评分表原文「输出完整、格式规范」。逐字符照抄模板：等号空格、乘号两侧空格、末尾干净。",
            },
        ],
        "tasks": [
            {
                "id": "T1",
                "title": "综合自检 + 全真模拟",
                "input": "360",
                "desc": "读入整数 n（2 ≤ n ≤ 10^6），输出两行：第一行是质因数分解式（格式同第 02 讲），第二行是全部因数个数。这是全课程综合自检--写对它，再去完成一次 120 分钟全真模拟（数据/全真模拟卷.md）。",
                "starter": "n = int(input())\n# 第一行：短除法分解（第 02 讲 T1 原样复用）\n# 第二行：枚举 1 到 n 数因数个数；\n# 快速法提示：因数个数定理，指数 + 1 连乘\n",
                "expect": "360 = 2 × 2 × 2 × 3 × 3 × 5\n24",
                "hints": [
                    "分解部分和第 02 讲 T1 一模一样：内层反复除、外层换下一个、最后 m > 1 补上。",
                    "因数个数用枚举：j 从 1 到 n，n % j == 0 就计数；360 的答案是 24。",
                    "想用因数个数定理验证：360 = 2³ × 3² × 5，(3+1) × (2+1) × (1+1) = 24，和枚举结果应该一样。",
                ],
                "optional": False,
            },
        ],
    },
]

# 参考解法：键为 (讲次 nn, 任务 id)，--verify 实跑比对 expect
REF = {
    ("01", "T1"): "s = input()\na, b = s.split()\na = int(a)\nb = int(b)\nprint(a + b)\nprint(a - b)",
    ("01", "T2"): 'n = int(input())\nif n % 2 == 0:\n    print("yes")\nelse:\n    print("no")',
    ("01", "T3"): "n = int(input())\ntotal = 0\nfor i in range(1, n + 1):\n    total = total + i\nprint(total)",
    ("02", "T1"): (
        'n = int(input())\n'
        'm = n\n'
        'parts = []\n'
        'i = 2\n'
        'while i * i <= m:\n'
        '    while m % i == 0:\n'
        '        parts.append(i)\n'
        '        m = m // i\n'
        '    i = i + 1\n'
        'if m > 1:\n'
        '    parts.append(m)\n'
        'out = ""\n'
        'for k in range(len(parts)):\n'
        '    if k > 0:\n'
        '        out = out + " × "\n'
        '    out = out + str(parts[k])\n'
        'print(str(n) + " = " + out)'
    ),
    ("02", "T2"): (
        'n = int(input())\n'
        'even_count = 0\n'
        'odd_sum = 0\n'
        'i = 1\n'
        'while i <= n:\n'
        '    if n % i == 0:\n'
        '        if i % 2 == 0:\n'
        '            even_count = even_count + 1\n'
        '        else:\n'
        '            odd_sum = odd_sum + i\n'
        '    i = i + 1\n'
        'm = n\n'
        'max_prime = 0\n'
        'i = 2\n'
        'while i * i <= m:\n'
        '    while m % i == 0:\n'
        '        max_prime = i\n'
        '        m = m // i\n'
        '    i = i + 1\n'
        'if m > 1:\n'
        '    max_prime = m\n'
        'print(even_count)\n'
        'print(odd_sum)\n'
        'print(max_prime)'
    ),
    ("02", "T3"): (
        'n = int(input())\n'
        'count = 0\n'
        'total = 0\n'
        'for i in range(1, n + 1):\n'
        '    if n % i == 0:\n'
        '        count = count + 1\n'
        '        total = total + i\n'
        'print(count)\n'
        'print(total)'
    ),
    ("03", "T1"): (
        'n = int(input())\n'
        'answer = "yes"\n'
        'if n == 2:\n'
        '    print("yes")\n'
        'else:\n'
        '    if n % 2 == 0:\n'
        '        print("no")\n'
        '    else:\n'
        '        i = 3\n'
        '        found = False\n'
        '        while i * i <= n and not found:\n'
        '            if n % i == 0:\n'
        '                found = True\n'
        '                answer = "no"\n'
        '            i = i + 2\n'
        '        print(answer)'
    ),
    ("03", "T2"): (
        'n = int(input())\n'
        'if n == 2 or n == 3:\n'
        '    print("yes")\n'
        'else:\n'
        '    if n % 2 == 0 or n % 3 == 0:\n'
        '        print("no")\n'
        '    else:\n'
        '        i = 5\n'
        '        found = False\n'
        '        answer = "yes"\n'
        '        while i * i <= n and not found:\n'
        '            if n % i == 0 or n % (i + 2) == 0:\n'
        '                found = True\n'
        '                answer = "no"\n'
        '            i = i + 6\n'
        '        print(answer)'
    ),
    ("04", "T1"): (
        'm = int(input())\n'
        'k = 0\n'
        'while k < m:\n'
        '    n = int(input())\n'
        '    mm = n\n'
        '    parts = []\n'
        '    i = 2\n'
        '    while i * i <= mm:\n'
        '        while mm % i == 0:\n'
        '            parts.append(i)\n'
        '            mm = mm // i\n'
        '        i = i + 1\n'
        '    if mm > 1:\n'
        '        parts.append(mm)\n'
        '    out = ""\n'
        '    for j in range(len(parts)):\n'
        '        if j > 0:\n'
        '            out = out + " × "\n'
        '        out = out + str(parts[j])\n'
        '    print(str(n) + " = " + out)\n'
        '    k = k + 1'
    ),
    ("04", "T2"): (
        'n = int(input())\n'
        'flags = [True] * (n + 1)\n'
        'flags[0] = False\n'
        'flags[1] = False\n'
        'p = 2\n'
        'while p * p <= n:\n'
        '    if flags[p]:\n'
        '        multiple = p * p\n'
        '        while multiple <= n:\n'
        '            flags[multiple] = False\n'
        '            multiple = multiple + p\n'
        '    p = p + 1\n'
        'count = 0\n'
        'v = 2\n'
        'while v <= n:\n'
        '    if flags[v]:\n'
        '        count = count + 1\n'
        '    v = v + 1\n'
        'print(count)'
    ),
    ("05", "T1"): (
        'n = int(input())\n'
        'm = n\n'
        'parts = []\n'
        'i = 2\n'
        'while i * i <= m:\n'
        '    while m % i == 0:\n'
        '        parts.append(i)\n'
        '        m = m // i\n'
        '    i = i + 1\n'
        'if m > 1:\n'
        '    parts.append(m)\n'
        'out = ""\n'
        'for k in range(len(parts)):\n'
        '    if k > 0:\n'
        '        out = out + " × "\n'
        '    out = out + str(parts[k])\n'
        'print(str(n) + " = " + out)\n'
        'j = 1\n'
        'count = 0\n'
        'while j <= n:\n'
        '    if n % j == 0:\n'
        '        count = count + 1\n'
        '    j = j + 1\n'
        'print(count)'
    ),
    ("M01", "T1"): (
        'n = int(input())\n'
        'm = n\n'
        'parts = []\n'
        'i = 2\n'
        'while i * i <= m:\n'
        '    while m % i == 0:\n'
        '        parts.append(str(i))\n'
        '        m = m // i\n'
        '    i = i + 1\n'
        'if m > 1:\n'
        '    parts.append(str(m))\n'
        'print(str(n) + " = " + " × ".join(parts))\n'
        'tot_cnt = 0\n'
        'even_cnt = 0\n'
        'j = 1\n'
        'while j <= n:\n'
        '    if n % j == 0:\n'
        '        tot_cnt = tot_cnt + 1\n'
        '        if j % 2 == 0:\n'
        '            even_cnt = even_cnt + 1\n'
        '    j = j + 1\n'
        'print(tot_cnt)\n'
        'print(even_cnt)\n'
        'print(parts[-1])'
    ),
    ("M01", "T2"): (
        'n = int(input())\n'
        'ans1 = "yes"\n'
        'cnt1 = 0\n'
        'if n == 2:\n'
        '    ans1 = "yes"\n'
        'elif n % 2 == 0:\n'
        '    ans1 = "no"\n'
        'else:\n'
        '    i = 3\n'
        '    found = False\n'
        '    while i * i <= n and not found:\n'
        '        cnt1 = cnt1 + 1\n'
        '        if n % i == 0:\n'
        '            found = True\n'
        '            ans1 = "no"\n'
        '        i = i + 2\n'
        'cnt2 = 0\n'
        'if n == 2 or n == 3:\n'
        '    pass\n'
        'elif n % 2 == 0 or n % 3 == 0:\n'
        '    pass\n'
        'else:\n'
        '    i = 5\n'
        '    found = False\n'
        '    while i * i <= n and not found:\n'
        '        cnt2 = cnt2 + 1\n'
        '        if n % i == 0 or n % (i + 2) == 0:\n'
        '            found = True\n'
        '        i = i + 6\n'
        'print(ans1)\n'
        'print("跳偶版循环次数 =", cnt1)\n'
        'print("6k±1版循环次数 =", cnt2)'
    ),
    ("M01", "T3"): (
        'n = int(input())\n'
        'flags = [True] * (n + 1)\n'
        'flags[0] = False\n'
        'flags[1] = False\n'
        'p = 2\n'
        'while p * p <= n:\n'
        '    if flags[p]:\n'
        '        multiple = p * p\n'
        '        while multiple <= n:\n'
        '            flags[multiple] = False\n'
        '            multiple = multiple + p\n'
        '    p = p + 1\n'
        'primes = []\n'
        'v = 2\n'
        'while v <= n:\n'
        '    if flags[v]:\n'
        '        primes.append(v)\n'
        '    v = v + 1\n'
        'twins = 0\n'
        'k = 0\n'
        'while k < len(primes) - 1:\n'
        '    if primes[k + 1] - primes[k] == 2:\n'
        '        twins = twins + 1\n'
        '    k = k + 1\n'
        'print("质数个数 =", len(primes))\n'
        'print("孪生质数对数 =", twins)'
    ),
    ("E01", "T1"): (
        'a0 = int(input())\n'
        'b0 = int(input())\n'
        'a = a0\n'
        'b = b0\n'
        'while b != 0:\n'
        '    r = a % b\n'
        '    a = b\n'
        '    b = r\n'
        'gcd_val = a\n'
        'groups = a0 // gcd_val + b0 // gcd_val\n'
        'lcm_val = a0 * b0 // gcd_val\n'
        'print("每组最多人数 =", gcd_val)\n'
        'print("最少总组数 =", groups)\n'
        'print("最小公倍数 =", lcm_val)'
    ),
    ("E01", "T2"): (
        'n = int(input())\n'
        'cnt = 0\n'
        'x = 2\n'
        'while x <= n:\n'
        '    s = 1\n'
        '    i = 2\n'
        '    while i * i <= x:\n'
        '        if x % i == 0:\n'
        '            s = s + i\n'
        '            if i * i != x:\n'
        '                s = s + x // i\n'
        '        i = i + 1\n'
        '    if s == x:\n'
        '        print(x)\n'
        '        cnt = cnt + 1\n'
        '    x = x + 1\n'
        'print("共", cnt, "个完全数")'
    ),
    ("E01", "T3"): (
        'n = int(input())\n'
        'flags = [True] * (n + 1)\n'
        'flags[0] = False\n'
        'flags[1] = False\n'
        'p = 2\n'
        'while p * p <= n:\n'
        '    if flags[p]:\n'
        '        m = p * p\n'
        '        while m <= n:\n'
        '            flags[m] = False\n'
        '            m = m + p\n'
        '    p = p + 1\n'
        'primes = []\n'
        'v = 2\n'
        'while v <= n:\n'
        '    if flags[v]:\n'
        '        primes.append(v)\n'
        '    v = v + 1\n'
        'cnt = 0\n'
        'best = 0\n'
        'i = 0\n'
        'while i < len(primes):\n'
        '    j = i + 1\n'
        '    while j < len(primes):\n'
        '        prod = primes[i] * primes[j]\n'
        '        if prod <= n:\n'
        '            cnt = cnt + 1\n'
        '            if prod > best:\n'
        '                best = prod\n'
        '        j = j + 1\n'
        '    i = i + 1\n'
        'print("不同质数乘积个数 =", cnt)\n'
        'print("最大一个 =", best)'
    ),
}

MOCKS = [
    {
        "nn": "M01",
        "filename": "模拟卷01.html",
        "title": "大数分解 60 分钟全真模拟卷一",
        "timeLimitMin": 60,
        "intro": "限时 60 分钟，覆盖因数分解、效率对比、埃氏筛应用与报告规范。建议分配：客观题 15 分钟 + 编程三题 40 分钟 + 流程与自查 5 分钟。",
        "obj": [
            {
                "kind": "single",
                "q": "数字 1 属于哪一类？",
                "opts": ["质数", "既不是质数也不是合数", "合数", "最小偶质数"],
                "a": 1,
                "why": "质数要求「除了 1 和它本身以外没有别的因数」，且必须大于 1；1 只有一个因数，既不是质数也不是合数。埃氏筛也要把 flags[0] 和 flags[1] 设为 False。",
            },
            {
                "kind": "single",
                "q": "用短除试除法分解质数 n = 29 时，外层 while i * i <= m: 循环结束时，m 的值是？",
                "opts": ["1", "0", "5", "29"],
                "a": 3,
                "why": "29 没有 2 到 5 之间的任何因数，所以内层循环一次都没执行，m 一直保持 29。正因如此，循环外必须写 if m > 1: 把剩下的质数 29 收进结果里。",
            },
            {
                "kind": "single",
                "q": "已知 84 = 2 × 2 × 3 × 7，84 的全部因数（含 1 和 84）共有几个？",
                "opts": ["12", "6", "8", "24"],
                "a": 0,
                "why": "按因数个数定理：84 = 2² × 3¹ × 7¹，指数加 1 连乘得 (2+1) × (1+1) × (1+1) = 3 × 2 × 2 = 12 个。",
            },
            {
                "kind": "single",
                "q": "在短除法外层循环中，误把 while i * i <= m: 写成了 while i * i < m:（少了一个等号），输入哪个数一定会出错？",
                "opts": ["12", "30", "49", "17"],
                "a": 2,
                "why": "49 = 7 × 7。i = 7 时正好 i * i == 49，写成 < 会提前停在 i = 6，把合数 49 原封不动当成质因数放进结果。12、30 在 i = 2、3 时已除小，17 本身是质数。",
            },
            {
                "kind": "single",
                "q": "检验一个约 10^10 大小的质数，「从 2 试到 √n」大约需要试除多少次？",
                "opts": ["50 次左右", "10^5 次左右", "10^8 次左右", "10^10 次左右"],
                "a": 1,
                "why": "√(10^10) = 10^5 = 十万次。如果从 2 试到 n 则需要 10^10 次，两者相差十万倍。",
            },
            {
                "kind": "single",
                "q": "用 6k±1 试除法检查 n = 35 是否质数，特判完 2 和 3 后，第一轮循环检查的两个除数 i 和 i + 2 分别是？",
                "opts": ["1 和 3", "3 和 5", "7 和 9", "5 和 7"],
                "a": 3,
                "why": "6k±1 试除从 i = 5 起步，每轮检查 i 和 i + 2（也就是 5 和 7），下一轮 i 加 6 检查 11 和 13。检查 35 时第一轮遇到 5 就发现 35 % 5 == 0 停下。",
            },
            {
                "kind": "single",
                "q": "用埃氏筛求 100 以内的全部质数，外层循环变量 p 最大只需检查到多少？",
                "opts": ["10", "50", "99", "100"],
                "a": 0,
                "why": "外层条件是 p * p <= 100，即 p <= 10。任何不超过 100 的合数，必然有一个不超过 10 的质因子，所以 p 超过 10 后不会再划掉新数。",
            },
            {
                "kind": "single",
                "q": "在比赛 PPT 六页报告框架中，「控制变量说明 + 实验记录表 + 算法耗时对比图」最适合放在哪一部分？",
                "opts": ["封面与标题页", "问题理解页", "实验设计与数据对比页", "创新与反思页"],
                "a": 2,
                "why": "控制变量属于实验设计，记录表与柱状/折线图属于数据与对比，是支撑「算法效率探究 20 分」的核心证据。",
            },
            {
                "kind": "blank",
                "q": "埃氏筛划掉质数 p 的倍数时，为了跳过已被更小质数划掉的数，内层起始位置 multiple 应设为 ____（用字母 p 表示，不要空格）",
                "a": "p*p",
                "accept": ["p*p", "p**2"],
                "why": "2×p、3×p 等更小的倍数在筛 2、3 时已经划过，直接从 p * p 开始划既省时间又不遗漏。",
            },
            {
                "kind": "blank",
                "q": "用短除法分解 n = 36，若误把内层 while m % i == 0: 写成了 if m % i == 0:（只除一次不反复除），最终分解结果里会混入一个合数因子 ____（填数字）",
                "a": "6",
                "accept": ["6"],
                "why": "手算追踪：i=2 除一次得 m=18，i=3 除一次得 m=6，接着 i=4 时 4×4>6 循环结束，剩下的 m=6 被当成质数放进结果（变成 2 × 3 × 6）。",
            },
            {
                "kind": "blank",
                "q": "若一台电脑每秒可完成 5×10^7 次简单取余运算，估算执行 1.5×10^9 次取余大约需要 ____ 秒（填数字）",
                "a": "30",
                "accept": ["30"],
                "why": "总次数 ÷ 每秒次数 = (1.5 × 10^9) ÷ (5 × 10^7) = 30 秒。",
            },
            {
                "kind": "blank",
                "q": "手绘比赛流程图时，表示「条件判断（如 n % i == 0?）」的图框形状名称是 ____（填两字）",
                "a": "菱形",
                "accept": ["菱形"],
                "why": "四种标准图框：起止用圆角矩形、输入输出用平行四边形、处理计算用矩形、条件判断用菱形（出口需标「是」「否」）。",
            },
        ],
        "tasks": [
            {
                "id": "T1",
                "title": "数字分解与成分统计",
                "input": "485100",
                "desc": "读入整数 n（2 ≤ n ≤ 10^6），依次输出四行：\n第 1 行：质因数分解式（格式如 485100 = 2 × 2 × ...）\n第 2 行：全部因数的个数\n第 3 行：偶因数的个数\n第 4 行：最大质因数\n注意：不要死记硬背样例数字，程序要对任意合数/质数通用。",
                "starter": "n = int(input())\n# 第 1 部分：短除法求质因数列表 parts（存字符串），按格式打印分解式\n# 第 2 部分：枚举 1 到 n 统计全部因数个数 tot_cnt 与偶因数个数 even_cnt\n# 第 3 部分：最大质因数就是 parts 的最后一个元素 parts[-1]\n",
                "expect": "485100 = 2 × 2 × 3 × 3 × 5 × 5 × 7 × 7 × 11\n162\n108\n11",
                "hints": [
                    "短除法所得因子是从小到大排列的，所以 parts[-1] 天然就是最大质因数（前提是循环后别忘了 if m > 1: 补最后一项）。",
                    "统计全部因数与偶因数可以在同一个 while j <= n 循环里做：if n % j == 0: 时 tot_cnt 加 1，再套一层 if j % 2 == 0: 让 even_cnt 加 1。",
                    "输出第 1 行用 print(str(n) + \" = \" + \" × \".join(parts))，后三行分别 print(tot_cnt)、print(even_cnt)、print(parts[-1])。",
                ],
                "optional": False,
            },
            {
                "id": "T2",
                "title": "双算法循环次数对比（跳偶 vs 6k±1）",
                "input": "104729",
                "desc": "读入整数 n（n ≥ 2）。分别用「跳偶试除」和「6k±1 试除」判断 n 是否质数，并各自统计 while 循环执行了多少轮（记为 cnt1 和 cnt2）。输出三行：\n第 1 行：yes 或 no\n第 2 行：跳偶版循环次数 = cnt1\n第 3 行：6k±1版循环次数 = cnt2\n（比赛现场在此基础上套一层 time.perf_counter() 即可直接用于效率实验表。）",
                "starter": "n = int(input())\n# 算法一：跳偶试除（2 特判，偶数直接 no，否则 i 从 3 起每次 +2 到 i*i <= n），用 cnt1 记循环轮数\n# 算法二：6k±1 试除（2/3 特判，2 或 3 的倍数直接停，否则 i 从 5 起每次查 i 和 i+2、每次 +6），用 cnt2 记循环轮数\n",
                "expect": "yes\n跳偶版循环次数 = 161\n6k±1版循环次数 = 54",
                "hints": [
                    "两种写法都先各自初始化 cnt1 = 0、cnt2 = 0，只要进了 while 循环体开头就把对应计数器加 1。",
                    "跳偶版：while i * i <= n and not found: 里 cnt1 = cnt1 + 1；6k±1 版：while i * i <= n and not found: 里 cnt2 = cnt2 + 1。",
                    "注意输出格式逗号拼接会自动加空格：print(\"跳偶版循环次数 =\", cnt1) 和 print(\"6k±1版循环次数 =\", cnt2)。",
                ],
                "optional": False,
            },
            {
                "id": "T3",
                "title": "埃氏筛应用：区间孪生质数统计",
                "input": "100",
                "desc": "相差为 2 的两个质数称为「孪生质数」（例如 3 和 5、5 和 7、11 和 13）。读入整数 n（2 ≤ n ≤ 10^5），用埃氏筛找出 2 到 n 的全部质数存入列表 primes，然后统计孪生质数的对数，输出两行：\n质数个数 = ...\n孪生质数对数 = ...",
                "starter": "n = int(input())\n# 第 1 步：用埃氏筛造 flags 表，把 2 到 n 中 flags[v] 为 True 的数 append 进 primes\n# 第 2 步：遍历相邻两个质数 primes[k] 和 primes[k + 1]，若差等于 2 就计数\n",
                "expect": "质数个数 = 25\n孪生质数对数 = 8",
                "hints": [
                    "先照第 04 讲 T2 写出埃氏筛得到 flags，然后用 v 从 2 到 n 收集所有 flags[v] 为 True 的数放进 primes。",
                    "收集完 primes 后，写 k = 0，while k < len(primes) - 1:（注意减 1 防越界），判断 if primes[k + 1] - primes[k] == 2:。",
                    "最后打印 print(\"质数个数 =\", len(primes)) 和 print(\"孪生质数对数 =\", twins)。输入 100 应得 25 和 8。",
                ],
                "optional": False,
            },
        ],
    },
    {
        "nn": "E01",
        "filename": "拓展卷01.html",
        "title": "大数分解拓展拔高卷（GCD / 完全数 / 半质数）",
        "timeLimitMin": 60,
        "intro": "限时 60 分钟，面向已掌握五讲主线的学生拓展拔高：结合辗转相除、互质、完全数、半质数与唯一分解原理，全部题目与五讲及模拟卷一零重复。",
        "obj": [
            {
                "kind": "single",
                "q": "两个正整数的最大公约数是 1（例如 8 和 15），在数学上称这两个数？",
                "opts": ["孪生质数", "互质（互素）", "完全数", "等差数列"],
                "a": 1,
                "why": "最大公约数为 1 的两个整数称为互质（互素），它们自身不一定是质数（8 和 15 都是合数，但公因数只有 1）。",
            },
            {
                "kind": "single",
                "q": "已知 a = 24、b = 36，两数的最大公约数是 12，那么它们的最小公倍数是？",
                "opts": ["48", "144", "72", "864"],
                "a": 2,
                "why": "核心恒等式：最小公倍数 = a × b ÷ 最大公约数 = 24 × 36 ÷ 12 = 72。",
            },
            {
                "kind": "single",
                "q": "如果把整数拆成「两个质数的乘积」（例如 15 = 3 × 5、21 = 3 × 7），这类数叫「半质数」。下面哪个数是半质数？",
                "opts": ["30", "12", "49", "24"],
                "a": 2,
                "why": "49 = 7 × 7，恰好是两个质数之积；30 = 2×3×5（3 个质因子）、12 = 2×2×3、24 = 2×2×2×3。",
            },
            {
                "kind": "single",
                "q": "已知两个数的质因数分解式分别是 A = 2³ × 3² × 5 和 B = 2² × 3³ × 7，它们的最大公约数是？",
                "opts": ["2² × 3² = 36", "2³ × 3³ = 216", "2 × 3 × 5 × 7 = 210", "2³ × 3² × 5 × 7"],
                "a": 0,
                "why": "求最大公约数时，取两数「共同拥有」的质因子，且指数取较小值：2 取 2²、3 取 3²，5 和 7 不共有，得 36。",
            },
            {
                "kind": "single",
                "q": "如果一个正整数等于它所有「真因数（不含自身）」之和，例如 6 = 1 + 2 + 3，就称为「完全数」。继 6 之后的第二个完全数是？",
                "opts": ["12", "24", "36", "28"],
                "a": 3,
                "why": "28 的真因数是 1、2、4、7、14，之和 1 + 2 + 4 + 7 + 14 = 28。",
            },
            {
                "kind": "single",
                "q": "只枚举 i 从 2 到 √n 成对统计 n 的全部因数之和时，当遇到 i * i == n（即 n 是完全平方数）时必须特别注意什么？",
                "opts": [
                    "i 和 n // i 是同一个数，只能加一次，不能重复加两次",
                    "完全平方数没有因数",
                    "必须改回从 1 枚举到 n",
                    "n // i 一定比 √n 小"
                ],
                "a": 0,
                "why": "例如 36 当 i = 6 时，36 // 6 还是 6；若不判断 i * i != n 就把 i 和 n // i 都加上去，6 会被多算一次。",
            },
            {
                "kind": "single",
                "q": "埃氏筛开一个长度为 n + 1 的布尔列表 flags = [True] * (n + 1)。如果 n = 10^9（十亿），这套写法最先遇到的问题是？",
                "opts": [
                    "Python 列表内存占用过大（几个 GB），普通电脑会卡死或报 MemoryError",
                    "p * p <= n 条件会失效",
                    "flags[0] 无法设为 False",
                    "列表无法存超过 100 的下标"
                ],
                "a": 0,
                "why": "10^9 个 Python 列表引用就要消耗约 8 GB 内存，超出普通考场机房内存；这也是报告里「算法局限与内存边界」的重要分析点。",
            },
            {
                "kind": "single",
                "q": "在拓展阅读《费马小定理》中，如果有同学在答辩时把费马小定理吹成「百分百能识别所有质数的万能公式」，评委追问时最危险的反例是？",
                "opts": [
                    "存在极少数「卡迈克尔数」（如 561）是合数却能骗过测试",
                    "费马小定理不能算 2 的倍数",
                    "Python 无法做幂运算",
                    "质数 7 不满足费马小定理"
                ],
                "a": 0,
                "why": "费马小定理是必要不充分条件：561 = 3 × 11 × 17 是合数，却能骗过许多底数测试。不懂原理不要在报告里硬吹。",
            },
            {
                "kind": "blank",
                "q": "用辗转相除法求 gcd(a, b) 时，每次把 (a, b) 更新为 (b, ____) 直到 b 变成 0（不要空格）",
                "a": "a%b",
                "accept": ["a%b"],
                "why": "欧几里得算法的核心一步：a 与 b 的最大公约数等于 b 与 a % b 的最大公约数。",
            },
            {
                "kind": "blank",
                "q": "两个正整数 12 和 18 的最小公倍数是 ____（填数字）",
                "a": "36",
                "accept": ["36"],
                "why": "gcd(12, 18) = 6，所以 lcm = 12 × 18 ÷ 6 = 36。",
            },
            {
                "kind": "blank",
                "q": "6 = 1 + 2 + 3 是最小的完全数，它一共有 ____ 个正因数（含 1 和 6 本身，填数字）",
                "a": "4",
                "accept": ["4"],
                "why": "6 的全部正因数是 1、2、3、6，共 4 个（真因数 3 个）。",
            },
            {
                "kind": "blank",
                "q": "现代 RSA 加密算法的安全性，主要利用了「两个大质数相乘很容易，但把乘积反过来做____非常困难」这一特性（填四个字）",
                "a": "大数分解",
                "accept": ["大数分解", "质因数分解"],
                "why": "大数分解在经典计算机上没有已知的多项式时间算法，这正是本赛项研究的现实背景。",
            },
        ],
        "tasks": [
            {
                "id": "T1",
                "title": "活动团队分组（GCD 与最小公倍数）",
                "input": "84\n126",
                "desc": "分两行读入 A 校人数 a（输入 84 回车）和 B 校人数 b（输入 126 回车）。要求把两校各自平均分成若干人数相同的小组，每组人数尽可能多；再用最大公约数算出最小公倍数。输出三行：\n每组最多人数 = 42\n最少总组数 = 5\n最小公倍数 = 252",
                "starter": "a0 = int(input())\nb0 = int(input())\n# 用辗转相除法 while b != 0: 求 gcd_val，再算 groups 与 lcm_val\n",
                "expect": "每组最多人数 = 42\n最少总组数 = 5\n最小公倍数 = 252",
                "hints": [
                    "先拷贝一份 a = a0, b = b0 去跑辗转相除法：while b != 0: r = a % b; a = b; b = r，结束时 a 就是最大公约数。",
                    "最少总组数是两校各自分成的组数之和：a0 // gcd_val + b0 // gcd_val。",
                    "最小公倍数公式：a0 * b0 // gcd_val（先乘再整除，整数不会溢出）。",
                ],
                "optional": False,
            },
            {
                "id": "T2",
                "title": "区间完全数搜寻（O(√x) 真因数求和）",
                "input": "500",
                "desc": "读入整数 n（2 <= n <= 10000，输入 500 回车），找出 2 到 n 之间所有「完全数」（真因数之和等于它本身），依次逐行输出，并在最后一行输出总数：\n6\n28\n496\n共 3 个完全数\n提示：判断每个 x 时只需枚举 i 从 2 到 i * i <= x，找到一对因数 i 和 x // i 同时累加（注意 i * i == x 只加一次）。",
                "starter": "n = int(input())\ncnt = 0\n# 外层 x 从 2 到 n，内层 s = 1（1 一定是真因数），i 从 2 试到 i * i <= x\n",
                "expect": "6\n28\n496\n共 3 个完全数",
                "hints": [
                    "对每个 x，真因数不包含 x 本身，所以 s 从 1 起算，i 从 2 试到 i * i <= x。",
                    "如果 x % i == 0：把 i 加进 s；若 i * i != x，再把 x // i 也加进 s。",
                    "内层结束后如果 s == x，就 print(x) 且 cnt 加 1；最后输出 print(\"共\", cnt, \"个完全数\")。",
                ],
                "optional": False,
            },
            {
                "id": "T3",
                "title": "区间无平方半质数统计",
                "input": "200",
                "desc": "读入整数 n（4 <= n <= 5000，输入 200 回车）。先用埃氏筛找出 2 到 n 的全部质数存入列表 primes，再统计「恰好能写成两个不同质数相乘（p < q 且 p * q <= n）」的无平方半质数共有多少个，以及其中最大的一个是多少，输出两行：\n不同质数乘积个数 = 56\n最大一个 = 194",
                "starter": "n = int(input())\n# 第 1 步：埃氏筛建质数表 primes\n# 第 2 步：双层遍历 primes[i] 和 primes[j]（j > i），统计 prod = primes[i] * primes[j] <= n 的个数与最大值\n",
                "expect": "不同质数乘积个数 = 56\n最大一个 = 194",
                "hints": [
                    "先用埃氏筛收集出所有不超过 n 的质数放进列表 primes。",
                    "用两层循环 i 从 0 到 len(primes)-1，j 从 i+1 到 len(primes)-1，检查 primes[i] * primes[j] <= n。",
                    "只要乘积 <= n，计数器 cnt 加 1，同时用 if prod > best: best = prod 更新最大值。",
                ],
                "optional": False,
            },
        ],
    },
]


# ============================================================
# 引擎函数（先 stub，selftest 通过后再实现）
# ============================================================

def normalize_output(text):
    """输出归一化：统一换行、逐行去两端空白（含全角空格）、去末尾空行。"""
    lines = text.replace("\r\n", "\n").split("\n")
    lines = [ln.strip(" \t　") for ln in lines]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def detect_traceback(text):
    """粘贴内容是否是 Python 报错信息。"""
    return "Traceback (most recent call last)" in text


def normalize_blank(s):
    """填空归一化：去两端空白、去整体成对引号、去全部空白；保留大小写。"""
    s = s.strip(" \t　")
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        s = s[1:-1].strip(" \t　")
    return "".join(s.split())


def html_escape(s):
    """HTML 转义：& < > " '。"""
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def check_obj_data(lessons, expected_obj=(6, 4, 2)):
    """数据自检：客观题构成、单选下标与选项互异、填空 accept、REF 与提示齐全。"""
    errs = []
    for lesson in lessons:
        nn = lesson["nn"]
        singles = [q for q in lesson["obj"] if q["kind"] == "single"]
        blanks = [q for q in lesson["obj"] if q["kind"] == "blank"]
        if expected_obj is not None:
            tot_exp, s_exp, b_exp = expected_obj
            if len(lesson["obj"]) != tot_exp or len(singles) != s_exp or len(blanks) != b_exp:
                errs.append(f"{nn}: 客观题应为 {tot_exp} 道（{s_exp} 单选 + {b_exp} 填空），实际 {len(lesson['obj'])} 道")
        for qi, q in enumerate(singles):
            if not (0 <= q["a"] < len(q["opts"])):
                errs.append(f"{nn}: 单选第 {qi + 1} 题答案下标越界")
            if len(set(q["opts"])) != len(q["opts"]):
                errs.append(f"{nn}: 单选第 {qi + 1} 题选项文本重复")
        for qi, q in enumerate(blanks):
            if q["a"] not in q["accept"]:
                errs.append(f"{nn}: 填空第 {qi + 1} 题 accept 未含标准答案")
        for t in lesson["tasks"]:
            if (nn, t["id"]) not in REF:
                errs.append(f"{nn}: 任务 {t['id']} 缺参考解法 REF")
            if len(t["hints"]) != 3:
                errs.append(f"{nn}: 任务 {t['id']} 提示应为 3 级")
            if normalize_output(t["expect"]) == "" and not t["optional"]:
                errs.append(f"{nn}: 任务 {t['id']} 必做但 expect 为空")
    if errs:
        for e in errs:
            print("  数据问题:", e)
        return False
    return True


# ============================================================
# 页面模板（占位符：__NN__ __TITLE__ __DATA__；JS 保持 ES5 风格）
# ============================================================

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>第 __NN__ 讲练习 · 大数分解备赛</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: "Microsoft YaHei", "PingFang SC", sans-serif; background: #eef2f7; color: #24324a;
       font-size: 16px; line-height: 1.65; }
main { max-width: 860px; margin: 0 auto; padding: 16px 14px 48px; }
header.site { background: #24466e; color: #fff; padding: 18px 16px 14px; }
header.site h1 { font-size: 22px; }
header.site .sub { font-size: 13px; opacity: .85; margin-top: 2px; }
.banner { background: #b5453c; color: #fff; text-align: center; padding: 6px; font-size: 14px; display: none; }
.card { background: #fff; border-radius: 10px; padding: 16px 18px; margin-top: 16px;
        box-shadow: 0 1px 3px rgba(30, 50, 90, .12); }
.card > h2 { font-size: 18px; margin-bottom: 8px; padding-bottom: 6px; border-bottom: 2px solid #dce4ef; }
.intro { font-size: 15px; color: #51607a; }
.qcard { border: 1px solid #e2e8f2; border-radius: 8px; padding: 10px 12px; margin-top: 10px; }
.qcard.right { border-color: #2e8b57; background: #f2fbf6; }
.qcard.wrong { border-color: #c0392b; background: #fdf5f4; }
.qnum { font-size: 13px; color: #7a879e; }
.qtext { margin: 2px 0 6px; }
label.opt { display: block; padding: 3px 6px; border-radius: 6px; cursor: pointer; }
label.opt:hover { background: #f0f4fa; }
.blank { font-size: 16px; padding: 6px 8px; border: 1px solid #c3cdde; border-radius: 6px; width: 100%;
         font-family: Consolas, monospace; }
.why { display: none; margin-top: 8px; padding: 8px 10px; background: #f4f7fc; border-radius: 6px;
       font-size: 14px; color: #3b4a63; }
.row { display: flex; align-items: center; margin-top: 12px; }
.row > * + * { margin-left: 10px; }
button { font-family: inherit; font-size: 15px; padding: 7px 14px; border: 1px solid #9db2cd;
         border-radius: 7px; background: #f7f9fc; color: #24324a; cursor: pointer; }
button:hover { background: #e9eff8; }
button.primary { background: #24466e; border-color: #24466e; color: #fff; }
button.primary:hover { background: #2d5685; }
button.hint { font-size: 13px; padding: 4px 10px; }
button:disabled { opacity: .5; cursor: default; }
#objScore { font-size: 16px; font-weight: bold; color: #24466e; }
.task { border: 1px solid #e2e8f2; border-radius: 8px; padding: 12px 14px; margin-top: 12px; }
.task-head { display: flex; align-items: center; }
.task-head > * + * { margin-left: 8px; }
.task-head .tname { font-size: 16px; font-weight: bold; }
.badge { font-size: 12px; padding: 1px 8px; border-radius: 9px; background: #e3eaf4; color: #51607a; }
.badge.done { background: #2e8b57; color: #fff; }
.badge.opt { background: #f0e6d2; color: #8a6d1a; }
.tdesc { margin: 6px 0; }
.meta { display: flex; flex-wrap: wrap; margin: 4px 0; }
.meta > * + * { margin-left: 18px; }
.meta .k { color: #7a879e; font-size: 14px; }
pre.io { font-family: Consolas, monospace; font-size: 14px; background: #f4f7fc; padding: 6px 10px;
         border-radius: 6px; white-space: pre-wrap; }
textarea { width: 100%; min-height: 120px; font-family: Consolas, monospace; font-size: 14px;
           padding: 8px; border: 1px solid #c3cdde; border-radius: 6px; margin-top: 6px; resize: vertical; }
textarea.paste { min-height: 72px; }
.hintbox { display: none; margin-top: 8px; padding: 8px 10px; background: #fff9ec; border-radius: 6px;
           font-size: 14px; }
.hintbox p { margin-top: 4px; }
.msg { margin-top: 8px; font-size: 14px; white-space: pre-wrap; }
.msg.ok { color: #2e8b57; font-weight: bold; }
.msg.bad { color: #c0392b; }
.msg.warn { color: #8a6d1a; }
.done-stamp { display: none; margin-top: 14px; text-align: center; font-size: 20px; font-weight: bold;
              color: #2e8b57; border: 2px dashed #2e8b57; border-radius: 10px; padding: 10px; }
.timer-bar { display: none; margin-top: 8px; font-size: 15px; }
.timer-digits { font-family: Consolas, monospace; font-size: 20px; font-weight: bold; background: rgba(255,255,255,.18);
                padding: 2px 10px; border-radius: 6px; margin: 0 8px; }
.timer-btn { font-size: 13px; padding: 3px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,.45);
             background: rgba(255,255,255,.15); color: #fff; cursor: pointer; margin-left: 6px; }
.timer-btn:hover { background: rgba(255,255,255,.28); }
footer.page { margin-top: 20px; text-align: center; color: #7a879e; font-size: 13px; }
</style>
</head>
<body>
<div id="banner" class="banner">进度无法保存，本页功能仍可用</div>
<header class="site">
  <div style="font-size:13px;opacity:.88;margin-bottom:4px;"><a href="__BACK_HREF__" style="color:#fff;text-decoration:none;">← 返回大数分解主页</a></div>
  <h1>__HEADER_TITLE__</h1>
  <div class="sub">大数分解备赛 · __SUBTITLE__（记录只保存在本机浏览器）</div>
  <div class="timer-bar" id="timerBar">
    <span>剩余时间</span><span class="timer-digits" id="timerDigits">60:00</span>
    <button class="timer-btn" id="timerToggleBtn">暂停</button>
    <button class="timer-btn" id="timerResetBtn">重新计时</button>
  </div>
</header>
<main>
  <div class="card">
    <h2>本页导引</h2>
    <div class="intro" id="intro"></div>
    <div class="done-stamp" id="doneStamp">&#9733; 本页全部完成</div>
  </div>
  <div class="card">
    <h2 id="objHeading">客观题</h2>
    <div id="objHost"></div>
    <div class="row">
      <button id="submitObjBtn" class="primary">提交判分</button>
      <span id="objScore"></span>
    </div>
  </div>
  <div class="card">
    <h2>程序任务（在 IDLE 里写代码，运行后粘贴输出核对）</h2>
    <div id="taskHost"></div>
  </div>
  <div class="card">
    <h2>记录</h2>
    <div class="row">
      <button id="exportBtn">导出学习记录 .txt</button>
      <button id="resetBtn">清空本页记录</button>
    </div>
  </div>
  <footer class="page">本页由 工具/生成练习页.py 生成，请勿手改 · 数据不上传，只存本机</footer>
</main>
<script id="pageData" type="application/json">__DATA__</script>
<script>
var D = JSON.parse(document.getElementById("pageData").textContent);
var LS_KEY = "ds" + D.nn + "_practice_v1";
var storageOK = true;

function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { storageOK = false; return null; } }
function lsSet(k, v) { try { localStorage.setItem(k, v); } catch (e) { storageOK = false; } showBanner(); }
function lsDel(k) { try { localStorage.removeItem(k); } catch (e) { storageOK = false; } showBanner(); }
function showBanner() { if (!storageOK) document.getElementById("banner").style.display = "block"; }

function el(tag, cls) { var e = document.createElement(tag); if (cls) e.className = cls; return e; }
function normOut(t) {
  var lines = t.replace(/\\r\\n/g, "\\n").split("\\n");
  var out = [];
  for (var i = 0; i < lines.length; i++) {
    out.push(lines[i].replace(/^[\\s\\u3000]+/, "").replace(/[\\s\\u3000]+$/, ""));
  }
  while (out.length && out[out.length - 1] === "") out.pop();
  return out.join("\\n");
}
function detectTB(t) { return t.indexOf("Traceback (most recent call last)") !== -1; }
function normBlank(s) {
  s = s.replace(/^[\\s\\u3000]+/, "").replace(/[\\s\\u3000]+$/, "");
  if (s.length >= 2 && s.charAt(0) === s.charAt(s.length - 1) &&
      (s.charAt(0) === '"' || s.charAt(0) === "'")) {
    s = s.substring(1, s.length - 1);
  }
  return s.replace(/[\\s\\u3000]+/g, "");
}

var state = { obj: {}, objScore: -1, tasks: {}, timerLeft: D.timeLimitMin ? D.timeLimitMin * 60 : 0 };
D.tasks.forEach(function (t) {
  if (!state.tasks[t.id]) state.tasks[t.id] = { done: false, hints: 0 };
});

function loadState() {
  var raw = lsGet(LS_KEY);
  if (!raw) return;
  try {
    var s = JSON.parse(raw);
    if (s && typeof s === "object") {
      if (s.obj) state.obj = s.obj;
      if (typeof s.objScore === "number") state.objScore = s.objScore;
      if (typeof s.timerLeft === "number") state.timerLeft = s.timerLeft;
      if (s.tasks) {
        D.tasks.forEach(function (t) {
          if (s.tasks[t.id]) state.tasks[t.id] = s.tasks[t.id];
        });
      }
    }
  } catch (e) { /* 记录损坏则从新开始 */ }
}
function saveState() { lsSet(LS_KEY, JSON.stringify(state)); updateBadge(); }

function updateBadge() {
  var allObj = state.objScore === D.obj.length;
  var allTask = true;
  D.tasks.forEach(function (t) {
    if (!t.optional && !state.tasks[t.id].done) allTask = false;
  });
  document.getElementById("doneStamp").style.display = (allObj && allTask) ? "block" : "none";
}

function renderObj() {
  var host = document.getElementById("objHost");
  D.obj.forEach(function (q, qi) {
    var card = el("div", "qcard"); card.id = "q" + qi;
    var num = el("div", "qnum");
    num.textContent = "第 " + (qi + 1) + " 题 · " + (q.kind === "single" ? "单选" : "填空");
    var qt = el("div", "qtext"); qt.textContent = q.q;
    card.appendChild(num); card.appendChild(qt);
    if (q.kind === "single") {
      for (var oi = 0; oi < q.opts.length; oi++) {
        var lb = el("label", "opt");
        var r = document.createElement("input");
        r.type = "radio"; r.name = "q" + qi; r.value = String(oi);
        lb.appendChild(r);
        var sp = document.createElement("span");
        sp.textContent = " " + "ABCD".charAt(oi) + ". " + q.opts[oi];
        lb.appendChild(sp);
        card.appendChild(lb);
      }
    } else {
      var inp = document.createElement("input");
      inp.type = "text"; inp.className = "blank"; inp.id = "b" + qi;
      inp.placeholder = "在此填写答案";
      card.appendChild(inp);
    }
    var why = el("div", "why"); why.id = "why" + qi;
    card.appendChild(why);
    host.appendChild(card);
  });
  // 恢复已答记录
  D.obj.forEach(function (q, qi) {
    var v = state.obj["q" + qi];
    if (v === undefined || v === -1) return;
    if (q.kind === "single") {
      var radios = document.getElementsByName("q" + qi);
      for (var i = 0; i < radios.length; i++) {
        if (radios[i].value === String(v)) radios[i].checked = true;
      }
    } else {
      document.getElementById("b" + qi).value = v;
    }
  });
}

function submitObj() {
  var unanswered = [];
  D.obj.forEach(function (q, qi) {
    if (q.kind === "single") {
      var picked = document.querySelector('input[name="q' + qi + '"]:checked');
      if (!picked) { unanswered.push(qi + 1); state.obj["q" + qi] = -1; }
      else state.obj["q" + qi] = Number(picked.value);
    } else {
      var v = document.getElementById("b" + qi).value;
      if (!v.replace(/[\\s\\u3000]+/g, "")) { unanswered.push(qi + 1); state.obj["q" + qi] = ""; }
      else state.obj["q" + qi] = v;
    }
  });
  var scoreEl = document.getElementById("objScore");
  if (unanswered.length) {
    scoreEl.textContent = "还有 " + unanswered.length + " 题没作答：第 " + unanswered.join("、") + " 题";
    return;
  }
  var score = 0;
  D.obj.forEach(function (q, qi) {
    var card = document.getElementById("q" + qi);
    var why = document.getElementById("why" + qi);
    var ok;
    if (q.kind === "single") ok = state.obj["q" + qi] === q.a;
    else ok = [q.a].concat(q.accept || []).some(function (v) { return normBlank(state.obj["q" + qi]) === normBlank(v); });
    card.className = "qcard " + (ok ? "right" : "wrong");
    var head = ok ? "答对了。" : "正确答案：" + (q.kind === "single" ? "ABCD".charAt(q.a) + ". " + q.opts[q.a] : q.a) + " ";
    why.textContent = (ok ? "\\u221A " : "\\u00D7 ") + head + q.why;
    why.style.display = "block";
    if (ok) score++;
  });
  state.objScore = score;
  scoreEl.textContent = "得分：" + score + " / " + D.obj.length + (score === D.obj.length ? "　全对！" : "　可修改后重新提交");
  saveState();
}

function renderTasks() {
  var host = document.getElementById("taskHost");
  D.tasks.forEach(function (t, ti) {
    var box = el("div", "task"); box.id = "task" + t.id;
    var head = el("div", "task-head");
    var nm = el("span", "tname"); nm.textContent = t.id + " · " + t.title;
    head.appendChild(nm);
    if (t.optional) { var ob = el("span", "badge opt"); ob.textContent = "选做"; head.appendChild(ob); }
    var db = el("span", "badge"); db.id = "done" + t.id; db.textContent = "未通过";
    head.appendChild(db);
    box.appendChild(head);

    var d = el("div", "tdesc"); d.textContent = t.desc; box.appendChild(d);
    var m = el("div", "meta");
    var k1 = el("span", "k"); k1.textContent = "输入样例："; m.appendChild(k1);
    var v1 = el("pre", "io"); v1.textContent = t.input; m.appendChild(v1);
    var k2 = el("span", "k"); k2.textContent = "预期输出："; m.appendChild(k2);
    var v2 = el("pre", "io"); v2.textContent = t.expect; m.appendChild(v2);
    box.appendChild(m);

    var ta = document.createElement("textarea");
    ta.id = "code" + t.id; ta.spellcheck = false;
    ta.value = lsGet("ds" + D.nn + "_draft_" + t.id + "_v1") || t.starter;
    box.appendChild(ta);
    ta.addEventListener("input", function () {
      lsSet("ds" + D.nn + "_draft_" + t.id + "_v1", ta.value);
    });

    var hr1 = el("div", "row");
    for (var h = 1; h <= 3; h++) {
      (function (level) {
        var b = el("button", "hint");
        b.textContent = "提示 " + level;
        b.addEventListener("click", function () { showHint(t, level); });
        hr1.appendChild(b);
      })(h);
    }
    var fb = el("button"); fb.textContent = "格式检查（不判分）";
    fb.addEventListener("click", function () { checkFormat(t); });
    hr1.appendChild(fb);
    var ex = el("button"); ex.textContent = "导出 .py";
    ex.addEventListener("click", function () { exportPy(t); });
    hr1.appendChild(ex);
    box.appendChild(hr1);

    var hint = el("div", "hintbox"); hint.id = "hint" + t.id;
    box.appendChild(hint);
    var msg = el("div", "msg"); msg.id = "msg" + t.id;
    box.appendChild(msg);

    var ta2 = document.createElement("textarea");
    ta2.className = "paste"; ta2.id = "paste" + t.id; ta2.spellcheck = false;
    ta2.placeholder = "把程序运行结果的全部输出粘贴到这里（贴 Traceback 也行，会给你专门提示）";
    box.appendChild(ta2);
    var hr2 = el("div", "row");
    var cb = el("button", "primary"); cb.textContent = "核对输出";
    cb.addEventListener("click", function () { checkOut(t); });
    hr2.appendChild(cb);
    box.appendChild(hr2);

    host.appendChild(box);
    refreshTask(t);
  });
}

function showHint(t, level) {
  if (state.tasks[t.id].hints < level) { state.tasks[t.id].hints = level; saveState(); }
  refreshHint(t);
}
function refreshHint(t) {
  var n = state.tasks[t.id].hints;
  var box = document.getElementById("hint" + t.id);
  if (!n) { box.style.display = "none"; return; }
  box.style.display = "block";
  var parts = [];
  for (var i = 0; i < n && i < t.hints.length; i++) parts.push("提示" + (i + 1) + "：" + t.hints[i]);
  box.textContent = parts.join("\\n");
}

function checkFormat(t) {
  var code = document.getElementById("code" + t.id).value;
  var issues = [];
  var lines = code.split("\\n");
  var openP = 0, closeP = 0;
  for (var i = 0; i < lines.length; i++) {
    var ln = lines[i];
    var t2 = ln.replace(/^[\\s\\u3000]+/, "");
    if (!t2) continue;
    var no = i + 1;
    if (ln.indexOf("\\t") >= 0 && /^ +/.test(ln)) issues.push("第 " + no + " 行：Tab 与空格混用，统一用 4 个空格缩进");
    if (t2.indexOf("&&") >= 0 || t2.indexOf("||") >= 0) issues.push("第 " + no + " 行：Python 用 and / or，不是 && / ||");
    if (t2.indexOf("\\u201c") >= 0 || t2.indexOf("\\u201d") >= 0 || t2.indexOf("\\u2018") >= 0 || t2.indexOf("\\u2019") >= 0)
      issues.push("第 " + no + " 行：字符串的引号要用英文的（半角），不能用中文引号");
    if (!/["']/.test(t2) && /^(if|elif|else|for|while)\\b/.test(t2)) {
      var body = t2.split("#")[0].replace(/[\\s\\u3000]+$/, "");
      if (body.indexOf(":") === -1) issues.push("第 " + no + " 行：缺英文冒号 :");
    }
    openP += (ln.match(/\\(/g) || []).length;
    closeP += (ln.match(/\\)/g) || []).length;
  }
  if (code.indexOf("\\uff08") >= 0 || code.indexOf("\\uff09") >= 0) issues.push("代码里出现了中文括号（），应使用英文括号 ( )");
  if (openP !== closeP) issues.push("圆括号不配对：( 有 " + openP + " 个，) 有 " + closeP + " 个");
  var msg = document.getElementById("msg" + t.id);
  if (!issues.length) { msg.className = "msg ok"; msg.textContent = "格式检查：没发现常见问题（只查格式，不判断对错）"; }
  else { msg.className = "msg warn"; msg.textContent = "格式检查发现 " + issues.length + " 处：\\n" + issues.join("\\n"); }
}

function checkOut(t) {
  var pasted = document.getElementById("paste" + t.id).value;
  var msg = document.getElementById("msg" + t.id);
  var db = document.getElementById("done" + t.id);
  if (!pasted.replace(/[\\s\\u3000]+/g, "")) {
    msg.className = "msg warn"; msg.textContent = "先在 IDLE 里运行程序，把全部输出粘贴到上面的框里。";
    return;
  }
  if (detectTB(pasted)) {
    msg.className = "msg bad";
    msg.textContent = "粘贴的内容里有 Traceback，说明程序报错了。把报错的最后一行复制去查：常见原因是缺少 int() 转换、冒号、缩进。";
    db.textContent = "未通过"; db.className = "badge";
    state.tasks[t.id].done = false; saveState();
    return;
  }
  if (normOut(pasted) === normOut(t.expect)) {
    state.tasks[t.id].done = true; saveState();
    refreshTask(t);
    msg.className = "msg ok";
    msg.textContent = "核对通过，输出一致！" + (t.optional ? "（选做任务，不占必做进度）" : "");
  } else {
    state.tasks[t.id].done = false; saveState();
    refreshTask(t);
    msg.className = "msg bad";
    msg.textContent = "输出不一致。左边是你的，右边是预期的，逐行对照：\\n你的：\\n" + normOut(pasted) + "\\n预期：\\n" + normOut(t.expect);
  }
}

function refreshTask(t) {
  var db = document.getElementById("done" + t.id);
  if (state.tasks[t.id].done) { db.textContent = "已通过 \\u2713"; db.className = "badge done"; }
  else { db.textContent = "未通过"; db.className = "badge"; }
  refreshHint(t);
}

function exportPy(t) {
  var code = document.getElementById("code" + t.id).value;
  var blob = new Blob([code], { type: "text/plain" });
  var a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "ds" + D.nn + "_" + t.id + ".py";
  a.click();
  URL.revokeObjectURL(a.href);
}

function exportTxt() {
  var blob = new Blob([JSON.stringify(state, null, 2)], { type: "text/plain" });
  var a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "ds" + D.nn + "_练习记录.txt";
  a.click();
  URL.revokeObjectURL(a.href);
}

function resetAll() {
  if (!confirm("将清空本页全部答题与草稿记录，确定清空吗？")) return;
  var dead = [];
  try {
    for (var i = 0; i < localStorage.length; i++) {
      var k = localStorage.key(i);
      if (k && k.indexOf("ds" + D.nn + "_") === 0) dead.push(k);
    }
  } catch (e) { storageOK = false; }
  for (var j = 0; j < dead.length; j++) lsDel(dead[j]);
  location.reload();
}

document.getElementById("intro").textContent = D.intro;
var singleCnt = 0, blankCnt = 0;
D.obj.forEach(function (q) { if (q.kind === "single") singleCnt++; else blankCnt++; });
document.getElementById("objHeading").textContent = "客观题（" + singleCnt + " 单选 + " + blankCnt + " 填空）";
document.getElementById("submitObjBtn").addEventListener("click", submitObj);
document.getElementById("exportBtn").addEventListener("click", exportTxt);
document.getElementById("resetBtn").addEventListener("click", resetAll);
loadState();
renderObj();
renderTasks();
var scoreEl = document.getElementById("objScore");
if (state.objScore >= 0) scoreEl.textContent = "上次得分：" + state.objScore + " / " + D.obj.length + "（可重新提交）";
showBanner();
updateBadge();

if (D.timeLimitMin) {
  var tBar = document.getElementById("timerBar");
  var tDigits = document.getElementById("timerDigits");
  var tToggle = document.getElementById("timerToggleBtn");
  var tReset = document.getElementById("timerResetBtn");
  tBar.style.display = "block";
  var tRunning = true;
  var tId = null;
  function pad2(x) { return (x < 10 ? "0" : "") + x; }
  function paintTimer() {
    var sec = state.timerLeft > 0 ? state.timerLeft : 0;
    tDigits.textContent = pad2(Math.floor(sec / 60)) + ":" + pad2(sec % 60);
  }
  function startMockTimer() {
    if (tId) clearInterval(tId);
    paintTimer();
    tId = setInterval(function () {
      if (!tRunning) return;
      if (state.timerLeft > 0) {
        state.timerLeft--;
        paintTimer();
        saveState();
      } else {
        clearInterval(tId);
        tToggle.disabled = true;
        tToggle.textContent = "已结束";
      }
    }, 1000);
  }
  tToggle.addEventListener("click", function () {
    tRunning = !tRunning;
    tToggle.textContent = tRunning ? "暂停" : "继续";
  });
  tReset.addEventListener("click", function () {
    if (!confirm("重新开始 " + D.timeLimitMin + " 分钟倒计时？")) return;
    state.timerLeft = D.timeLimitMin * 60;
    tRunning = true;
    tToggle.disabled = false;
    tToggle.textContent = "暂停";
    saveState();
    startMockTimer();
  });
  startMockTimer();
}
</script>
</body>
</html>
"""


def render_page(lesson):
    """渲染一讲练习页或模拟卷，返回完整 HTML 字符串。"""
    is_mock = bool(lesson.get("timeLimitMin"))
    header_title = lesson["title"] if is_mock else f"第 {lesson['nn']} 讲练习 · {lesson['title']}"
    subtitle = f"限时 {lesson['timeLimitMin']} 分钟模拟" if is_mock else "课堂练习"
    back_href = "../index.html" if is_mock else "../../index.html"
    data = {
        "nn": lesson["nn"],
        "title": lesson["title"],
        "intro": lesson["intro"],
        "obj": lesson["obj"],
        "tasks": lesson["tasks"],
    }
    if is_mock:
        data["timeLimitMin"] = lesson["timeLimitMin"]
    data_json = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = (
        PAGE_TEMPLATE
        .replace("__NN__", html_escape(lesson["nn"]))
        .replace("__TITLE__", html_escape(lesson["title"]))
        .replace("__HEADER_TITLE__", html_escape(header_title))
        .replace("__SUBTITLE__", html_escape(subtitle))
        .replace("__BACK_HREF__", back_href)
        .replace("__DATA__", data_json)
    )
    return html


def run_verify_impl():
    """实跑每个任务的参考解法，比对归一化输出与 expect；stderr 必须为空。"""
    total = passed = 0
    tmp = Path(tempfile.mkdtemp(prefix="ds_verify_"))
    try:
        for lesson in LESSONS + MOCKS:
            for t in lesson["tasks"]:
                key = (lesson["nn"], t["id"])
                f = tmp / f"L{lesson['nn']}_{t['id']}.py"
                with open(f, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(REF[key])
                r = subprocess.run(
                    [sys.executable, "-I", "-X", "utf8", str(f)],
                    input=t["input"] + "\n", capture_output=True, text=True,
                    encoding="utf-8", errors="replace", timeout=120,
                )
                total += 1
                got = normalize_output(r.stdout)
                want = normalize_output(t["expect"])
                if r.returncode == 0 and not r.stderr.strip() and got == want:
                    passed += 1
                    print(f"  PASS {lesson['nn']}/{t['id']}")
                else:
                    print(f"  FAIL {lesson['nn']}/{t['id']}  rc={r.returncode}")
                    if r.stderr.strip():
                        print("    stderr:", r.stderr.strip()[:300])
                    print(f"    want={want!r}")
                    print(f"    got ={got!r}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\nverify: {passed}/{total}")
    return 0 if passed == total else 1


def run_verify():
    return run_verify_impl()


# ============================================================
# selftest
# ============================================================

def run_selftest():
    failures = []

    def check(name, cond, detail=""):
        if cond:
            print(f"  PASS {name}")
        else:
            failures.append(name)
            print(f"  FAIL {name} {detail}")

    # 1) 输出归一化：CRLF、两端空白（含全角）、末尾空行
    check("norm-crlf-tail", normalize_output(" 13 \r\n\r\n") == "13")
    check("norm-keep-inner", normalize_output("a b\n") == "a b")
    check("norm-multiline", normalize_output("13\n7\n\n") == "13\n7")

    # 2) Traceback 判定
    check("tb-yes", detect_traceback('Traceback (most recent call last):\n  File "x", line 1\nValueError: bad') is True)
    check("tb-no", detect_traceback("13\n7") is False)

    # 3) 填空归一化：两端空白、成对引号、内部空格；保留大小写
    check("blank-trim-quote", normalize_blank('  "int(input())"  ') == "int(input())")
    check("blank-spaces", normalize_blank("17 % 5") == "17%5")
    check("blank-case-kept", normalize_blank("Range") == "Range")

    # 4) 数据自检：单选下标、选项互异；填空 accept；REF 齐全；题干去重
    all_stems = [q["q"].strip() for grp in (LESSONS + MOCKS) for q in grp["obj"]]
    check("obj-data", check_obj_data(LESSONS) is True and check_obj_data(MOCKS, expected_obj=(12, 8, 4)) is True and len(all_stems) == len(set(all_stems)))

    # 5) 渲染转义：注入串不得以裸 HTML 出现；radio value 按下标且互异
    evil = {
        "nn": "99",
        "title": "注入测试</title><script>alert(1)</script>",
        "intro": "<!-- 注释注入 -->",
        "obj": [
            {"kind": "single", "q": "<b>加粗</b> <!-- 隐身 -->", "opts": ["<i>A</i>", "B", "C", "D"], "a": 0, "why": "</script>关闭"},
            {"kind": "single", "q": "q2", "opts": ["a", "b", "c", "d"], "a": 1, "why": "w"},
            {"kind": "single", "q": "q3", "opts": ["a", "b", "c", "d"], "a": 2, "why": "w"},
            {"kind": "single", "q": "q4", "opts": ["a", "b", "c", "d"], "a": 3, "why": "w"},
            {"kind": "blank", "q": '填"<b>"', "a": "x", "accept": ["x"], "why": "<!-- w -->"},
            {"kind": "blank", "q": "填2", "a": "y", "accept": ["y"], "why": "w"},
        ],
        "tasks": [
            {
                "id": "T1", "title": "t", "input": "1", "desc": "d",
                "starter": "print(1)\n", "expect": "1", "hints": ["h1", "h2", "h3"], "optional": False,
            },
        ],
    }
    evil_page = render_page(evil)
    # 静态 HTML 区 = 去掉 JSON 数据块后的部分（JSON 块是 script raw text，字面 <!-- 不构成注入）
    html_part = re.sub(
        r'<script id="pageData" type="application/json">.*?</script>', "", evil_page, flags=re.S
    )
    check("esc-lt-b", "<b>加粗</b>" not in html_part, "裸 <b> 出现")
    check("esc-comment", "<!-- 注释注入 -->" not in html_part, "裸注释出现")
    check("esc-script-close", "alert(1)</script>" not in evil_page, "title 注入未转义")
    # JSON 数据块必须可无损解析回读（radio value 由 JS 按下标生成，实机验证在终检做）
    m = re.search(r'<script id="pageData" type="application/json">(.*?)</script>', evil_page, re.S)
    check("json-embed", m is not None)
    if m:
        back = json.loads(m.group(1).replace("<\\/", "</"))
        check("json-roundtrip", len(back["obj"]) == 6 and back["obj"][0]["kind"] == "single"
              and len(back["obj"][0]["opts"]) == 4 and back["obj"][0]["a"] == 0
              and len(back["obj"][4]["accept"]) >= 1
              and len(back["tasks"][0]["hints"]) == 3)
    # JSON 数据块中 </script> 必须被转义为 <\/script>
    check("json-script-safe", "</script>\nalert" not in evil_page and "</script>" in evil_page)

    # 6) 填空判分必须使用 accept 列表：等价写法要判对，不能只认规范答案
    real_page = render_page(LESSONS[2])
    blocks = re.findall(r"<script[^>]*>(.*?)</script>", real_page, re.S)
    main_js = next((b for b in blocks if "normBlank" in b), "")
    check("render-mainjs", main_js != "")
    check("blank-grades-accept", "q.accept" in main_js,
          "填空判分未引用 accept：accept 里的等价写法会被误判错")
    # 数据自检：accept 必须涵盖规范答案，且各项归一化后互异、非空
    ok = True
    for les in LESSONS:
        for q in les["obj"]:
            if q["kind"] != "blank":
                continue
            acc = [normalize_blank(x) for x in q.get("accept", [q["a"]])]
            if normalize_blank(q["a"]) not in acc or len(set(acc)) != len(acc) or "" in acc:
                ok = False
    check("blank-accept-data", ok)

    print()
    if failures:
        print(f"selftest FAILED: {len(failures)} 项 -> {failures}")
        return 1
    print(f"selftest 全部通过")
    return 0


# ============================================================
# verify：实跑参考解法
# ============================================================

# ============================================================
# 生成 + 入口
# ============================================================

DS_INDEX_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>02 大数分解 · 备赛主页</title>
<style>
  :root { --blue:#24466e; --blue2:#36649c; --ink:#24324a; --muted:#61718a; --line:#dce4ef; --bg:#eef2f7; --green:#2e8b57; }
  * { box-sizing:border-box; }
  body { margin:0; font-family:"Microsoft YaHei","PingFang SC",sans-serif; background:var(--bg); color:var(--ink); line-height:1.6; font-size:16px; }
  .wrap { max-width:1060px; margin:0 auto; padding:0 22px 44px; }
  header.top { background:linear-gradient(135deg,#24466e 0%,#36649c 100%); color:#fff; padding:32px 0 26px; }
  header.top a.back { color:rgba(255,255,255,.88); text-decoration:none; font-size:13.5px; }
  h1 { margin:6px 0 6px; font-size:30px; }
  .sub { margin:0; font-size:15px; opacity:.9; }
  .banner-card { background:#fff; border:1px solid #bfd6ff; border-radius:12px; padding:14px 18px; margin:20px 0 10px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; }
  .sec { margin:24px 0 12px; font-size:19px; color:var(--blue); border-bottom:2px solid var(--line); padding-bottom:6px; }
  .grid { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }
  @media (max-width:860px) { .grid { grid-template-columns:repeat(2,1fr); } }
  @media (max-width:580px) { .grid { grid-template-columns:1fr; } }
  .card { background:#fff; border:1px solid var(--line); border-radius:12px; padding:16px 18px; display:flex; flex-direction:column; box-shadow:0 4px 14px rgba(30,50,90,.05); }
  .card h3 { margin:0 0 6px; font-size:17px; color:var(--blue); }
  .card p { margin:0 0 14px; font-size:13.5px; color:var(--muted); flex:1; }
  .actions { display:flex; flex-wrap:wrap; }
  .actions > * + * { margin-left:8px; }
  .btn { display:inline-block; padding:7px 14px; border-radius:8px; border:1px solid var(--blue); background:var(--blue); color:#fff; text-decoration:none; font-size:13.5px; }
  .btn.ghost { background:#fff; color:var(--blue); }
  footer { text-align:center; font-size:13px; color:var(--muted); padding:24px 0; }
</style>
</head>
<body>
<header class="top">
  <div class="wrap">
    <a class="back" href="../index.html">← 返回三大赛项总入口</a>
    <h1>02 大数分解 · 零基础 5 讲与模拟特训</h1>
    <p class="sub">对准 2026 官方评分表：数字分解与处理（15 分）+ 算法设计（20 分）+ 效率探究（20 分）+ 报告与分享（35 分）</p>
  </div>
</header>
<main class="wrap">
  <div class="banner-card">
    <span><b>单页全课程合集：</b>已将 5 讲课堂练习 + 60 分钟模拟卷一 + 拓展拔高卷整合在一个页面内，左侧一键切换。</span>
    <a class="btn" href="大数分解全课程.html">打开「大数分解全课程.html」 →</a>
  </div>
  <h2 class="sec">一、赛前 60 分钟限时模拟与拓展</h2>
  <div class="grid">
    <div class="card">
      <h3>60 分钟全真模拟卷一</h3>
      <p>12 道客观题（单选 + 填空）+ 3 道编程题（485100 分解统计 / 104729 双算法循环轮数对比 / 100 以内埃氏筛孪生质数）。</p>
      <div class="actions"><a class="btn" href="练习与模拟/模拟卷01.html">进入模拟卷一 →</a></div>
    </div>
    <div class="card">
      <h3>60 分钟拓展拔高卷</h3>
      <p>12 道拓展客观题 + 3 道拓展编程题（活动团队分组 GCD 与 LCM / 区间完全数搜寻 / 无平方半质数统计）。</p>
      <div class="actions"><a class="btn" href="练习与模拟/拓展卷01.html">进入拓展拔高卷 →</a></div>
    </div>
    <div class="card">
      <h3>120 分钟赛场模拟与报告模板</h3>
      <p>第 05 讲配套：120 分钟全真模拟卷、PPT 六页框架模板、标准流程图画法、5 分钟陈述脚本骨架与自评清单。</p>
      <div class="actions"><a class="btn ghost" href="练习与模拟/第05讲_报告与全真模拟/数据/全真模拟卷.md">120分钟模拟卷</a><a class="btn ghost" href="练习与模拟/第05讲_报告与全真模拟/数据/PPT六页框架模板.md">PPT模板</a></div>
    </div>
  </div>
  <h2 class="sec">二、零基础 5 讲系统课程</h2>
  <div class="grid">
    <div class="card">
      <h3>第 01 讲 · Python 基础速通</h3>
      <p>从零掌握输出、变量、输入、判断、循环累加、函数六大句型（6 客观 + 3 编程）。</p>
      <div class="actions"><a class="btn" href="练习与模拟/第01讲_Python基础速通/练习.html">进入练习</a><a class="btn ghost" href="练习与模拟/第01讲_Python基础速通/课件.pptx">PPTX课件</a></div>
    </div>
    <div class="card">
      <h3>第 02 讲 · 因数分解实战</h3>
      <p>全因数枚举、短除法质因数分解、偶因数/奇因数和/最大质因数统计与严格输出格式。</p>
      <div class="actions"><a class="btn" href="练习与模拟/第02讲_因数分解实战/练习.html">进入练习</a><a class="btn ghost" href="练习与模拟/第02讲_因数分解实战/课件.pptx">PPTX课件</a></div>
    </div>
    <div class="card">
      <h3>第 03 讲 · 双算法效率对比</h3>
      <p>朴素试除、√N 跳偶试除、6k±1 试除逐版升级 + 实验一三档计时与记录表。</p>
      <div class="actions"><a class="btn" href="练习与模拟/第03讲_双算法效率对比/练习.html">进入练习</a><a class="btn ghost" href="练习与模拟/第03讲_双算法效率对比/课件.pptx">PPTX课件</a></div>
    </div>
    <div class="card">
      <h3>第 04 讲 · 埃氏筛与批处理加速</h3>
      <p>手筛 30 → 埃氏筛五步 → 批处理先写对再加速 + 实验二对比与输出一致性护栏。</p>
      <div class="actions"><a class="btn" href="练习与模拟/第04讲_埃氏筛与批处理加速/练习.html">进入练习</a><a class="btn ghost" href="练习与模拟/第04讲_埃氏筛与批处理加速/课件.pptx">PPTX课件</a></div>
    </div>
    <div class="card">
      <h3>第 05 讲 · 报告与全真模拟</h3>
      <p>问题描述 10 分 + 分析报告 20 分 + 成果分享 5 分：流程图规范、陈述话术与综合自检。</p>
      <div class="actions"><a class="btn" href="练习与模拟/第05讲_报告与全真模拟/练习.html">进入练习</a><a class="btn ghost" href="练习与模拟/第05讲_报告与全真模拟/课件.pptx">PPTX课件</a></div>
    </div>
  </div>
</main>
<footer>02 大数分解备赛 · 离线练习 · 不联网、不上传</footer>
</body>
</html>
"""

DS_ALL_IN_ONE_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>02 大数分解 · 全课程与模拟一体化平台</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: "Microsoft YaHei", "PingFang SC", sans-serif; background: #eef2f7; color: #24324a; font-size: 16px; line-height: 1.65; }
.app { display: flex; min-height: 100vh; }
.sidebar { width: 280px; flex: 0 0 280px; background: #fff; border-right: 1px solid #dce4ef; position: sticky; top: 0; height: 100vh; overflow-y: auto; }
.side-top { background: #24466e; color: #fff; padding: 16px; }
.side-top a { color: rgba(255,255,255,.85); text-decoration: none; font-size: 12.5px; }
.side-top h2 { font-size: 18px; margin: 6px 0 2px; }
.side-top p { font-size: 12.5px; opacity: .88; }
.nav-sec { font-size: 12px; font-weight: bold; color: #7a879e; padding: 10px 14px 4px; }
.nav-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 14px; margin: 2px 8px; border-radius: 7px; cursor: pointer; font-size: 14px; }
.nav-item:hover { background: #f0f4fa; }
.nav-item.active { background: #e3eaf4; color: #24466e; font-weight: bold; }
.main-area { flex: 1; min-width: 0; }
header.site { background: #24466e; color: #fff; padding: 18px 20px 14px; }
header.site h1 { font-size: 22px; }
header.site .sub { font-size: 13px; opacity: .85; margin-top: 2px; }
main { max-width: 860px; margin: 0 auto; padding: 16px 16px 48px; }
.card { background: #fff; border-radius: 10px; padding: 16px 18px; margin-top: 16px; box-shadow: 0 1px 3px rgba(30, 50, 90, .12); }
.card > h2 { font-size: 18px; margin-bottom: 8px; padding-bottom: 6px; border-bottom: 2px solid #dce4ef; }
.qcard { border: 1px solid #e2e8f2; border-radius: 8px; padding: 10px 12px; margin-top: 10px; }
.qcard.right { border-color: #2e8b57; background: #f2fbf6; }
.qcard.wrong { border-color: #c0392b; background: #fdf5f4; }
.qnum { font-size: 13px; color: #7a879e; }
.qtext { margin: 2px 0 6px; }
label.opt { display: block; padding: 3px 6px; border-radius: 6px; cursor: pointer; }
.blank { font-size: 16px; padding: 6px 8px; border: 1px solid #c3cdde; border-radius: 6px; width: 100%; font-family: Consolas, monospace; }
.why { display: none; margin-top: 8px; padding: 8px 10px; background: #f4f7fc; border-radius: 6px; font-size: 14px; color: #3b4a63; }
.row { display: flex; align-items: center; margin-top: 12px; flex-wrap: wrap; }
.row > * + * { margin-left: 10px; }
button { font-family: inherit; font-size: 15px; padding: 7px 14px; border: 1px solid #9db2cd; border-radius: 7px; background: #f7f9fc; color: #24324a; cursor: pointer; }
button.primary { background: #24466e; border-color: #24466e; color: #fff; }
.task { border: 1px solid #e2e8f2; border-radius: 8px; padding: 12px 14px; margin-top: 12px; }
.badge { font-size: 12px; padding: 1px 8px; border-radius: 9px; background: #e3eaf4; color: #51607a; margin-left: 8px; }
.badge.done { background: #2e8b57; color: #fff; }
pre.io { font-family: Consolas, monospace; font-size: 14px; background: #f4f7fc; padding: 6px 10px; border-radius: 6px; white-space: pre-wrap; margin: 4px 0; }
textarea { width: 100%; min-height: 110px; font-family: Consolas, monospace; font-size: 14px; padding: 8px; border: 1px solid #c3cdde; border-radius: 6px; margin-top: 6px; resize: vertical; }
textarea.paste { min-height: 70px; }
.hintbox { display: none; margin-top: 8px; padding: 8px 10px; background: #fff9ec; border-radius: 6px; font-size: 14px; white-space: pre-wrap; }
.msg { margin-top: 8px; font-size: 14px; white-space: pre-wrap; }
.msg.ok { color: #2e8b57; font-weight: bold; }
.msg.bad { color: #c0392b; }
@media (max-width: 820px) { .app { flex-direction: column; } .sidebar { width: 100%; height: auto; position: static; } }
</style>
</head>
<body>
<div class="app">
  <aside class="sidebar">
    <div class="side-top">
      <a href="index.html">← 大数分解主页</a> · <a href="../index.html">总入口</a>
      <h2>02 大数分解全课程</h2>
      <p>5 讲课程 + 模拟卷01 + 拓展卷01</p>
    </div>
    <div id="sideNav"></div>
  </aside>
  <div class="main-area">
    <header class="site">
      <h1 id="pageTitle"></h1>
      <div class="sub" id="pageIntro"></div>
    </header>
    <main>
      <div class="card">
        <h2 id="objHeading">客观题</h2>
        <div id="objHost"></div>
        <div class="row">
          <button id="submitObjBtn" class="primary">提交判分</button>
          <span id="objScore" style="font-weight:bold;color:#24466e;"></span>
        </div>
      </div>
      <div class="card">
        <h2>程序任务（在 IDLE 运行后粘贴输出核对）</h2>
        <div id="taskHost"></div>
      </div>
    </main>
  </div>
</div>
<script id="ALL_DS_DATA" type="application/json">__ALL_DATA__</script>
<script>
(function () {
  var ALL = JSON.parse(document.getElementById("ALL_DS_DATA").textContent);
  var curIdx = 0;
  var D = ALL[0];

  function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function el(tag, cls) { var e = document.createElement(tag); if (cls) e.className = cls; return e; }
  function normOut(t) {
    var lines = t.replace(/\\r\\n/g, "\\n").split("\\n"), out = [];
    for (var i = 0; i < lines.length; i++) out.push(lines[i].replace(/^[\\s\\u3000]+/, "").replace(/[\\s\\u3000]+$/, ""));
    while (out.length && out[out.length - 1] === "") out.pop();
    return out.join("\\n");
  }
  function normBlank(s) {
    s = s.replace(/^[\\s\\u3000]+/, "").replace(/[\\s\\u3000]+$/, "");
    if (s.length >= 2 && s.charAt(0) === s.charAt(s.length - 1) && (s.charAt(0) === '"' || s.charAt(0) === "'")) s = s.substring(1, s.length - 1);
    return s.replace(/[\\s\\u3000]+/g, "");
  }

  function getUnitState(u) {
    var st = { obj: {}, objScore: -1, tasks: {} };
    u.tasks.forEach(function (t) { st.tasks[t.id] = { done: false, hints: 0 }; });
    var raw = lsGet("ds" + u.nn + "_practice_v1");
    if (raw) {
      try {
        var s = JSON.parse(raw);
        if (s && s.obj) st.obj = s.obj;
        if (s && typeof s.objScore === "number") st.objScore = s.objScore;
        if (s && s.tasks) u.tasks.forEach(function (t) { if (s.tasks[t.id]) st.tasks[t.id] = s.tasks[t.id]; });
      } catch (e) {}
    }
    return st;
  }
  function saveUnitState(u, st) { lsSet("ds" + u.nn + "_practice_v1", JSON.stringify(st)); renderNav(); }

  function renderNav() {
    var host = document.getElementById("sideNav");
    var html = '<div class="nav-sec">零基础 5 讲</div>';
    for (var i = 0; i < ALL.length; i++) {
      if (i === 5) html += '<div class="nav-sec">60 分钟模拟与拓展</div>';
      var u = ALL[i], st = getUnitState(u);
      var ok = (st.objScore === u.obj.length);
      u.tasks.forEach(function (t) { if (!t.optional && !st.tasks[t.id].done) ok = false; });
      html += '<div class="nav-item' + (i === curIdx ? ' active' : '') + '" data-i="' + i + '"><span>' + u.nn + ' · ' + u.title + '</span><span style="color:#2e8b57;font-weight:bold;">' + (ok ? '✓' : '') + '</span></div>';
    }
    host.innerHTML = html;
    var items = host.querySelectorAll(".nav-item");
    for (var k = 0; k < items.length; k++) {
      items[k].addEventListener("click", function () {
        curIdx = Number(this.getAttribute("data-i"));
        D = ALL[curIdx];
        renderNav();
        renderUnit();
        window.scrollTo({ top: 0, behavior: "smooth" });
      });
    }
  }

  function renderUnit() {
    var st = getUnitState(D);
    document.getElementById("pageTitle").textContent = (D.timeLimitMin ? D.title : ("第 " + D.nn + " 讲 · " + D.title));
    document.getElementById("pageIntro").textContent = D.intro;
    var sCnt = 0, bCnt = 0;
    D.obj.forEach(function (q) { if (q.kind === "single") sCnt++; else bCnt++; });
    document.getElementById("objHeading").textContent = "客观题（" + sCnt + " 单选 + " + bCnt + " 填空）";
    var objHost = document.getElementById("objHost");
    objHost.innerHTML = "";
    D.obj.forEach(function (q, qi) {
      var card = el("div", "qcard"); card.id = "q" + qi;
      var num = el("div", "qnum"); num.textContent = "第 " + (qi + 1) + " 题 · " + (q.kind === "single" ? "单选" : "填空");
      var qt = el("div", "qtext"); qt.textContent = q.q;
      card.appendChild(num); card.appendChild(qt);
      if (q.kind === "single") {
        for (var oi = 0; oi < q.opts.length; oi++) {
          var lb = el("label", "opt");
          var r = document.createElement("input"); r.type = "radio"; r.name = "q" + qi; r.value = String(oi);
          if (st.obj["q" + qi] === oi) r.checked = true;
          lb.appendChild(r);
          var sp = document.createElement("span"); sp.textContent = " " + "ABCD".charAt(oi) + ". " + q.opts[oi];
          lb.appendChild(sp); card.appendChild(lb);
        }
      } else {
        var inp = document.createElement("input"); inp.type = "text"; inp.className = "blank"; inp.id = "b" + qi;
        inp.value = st.obj["q" + qi] || ""; card.appendChild(inp);
      }
      var why = el("div", "why"); why.id = "why" + qi; card.appendChild(why);
      objHost.appendChild(card);
    });
    document.getElementById("objScore").textContent = st.objScore >= 0 ? ("上次得分：" + st.objScore + " / " + D.obj.length) : "";

    document.getElementById("submitObjBtn").onclick = function () {
      var score = 0;
      D.obj.forEach(function (q, qi) {
        var ok = false;
        if (q.kind === "single") {
          var p = document.querySelector('input[name="q' + qi + '"]:checked');
          st.obj["q" + qi] = p ? Number(p.value) : -1;
          ok = (st.obj["q" + qi] === q.a);
        } else {
          st.obj["q" + qi] = document.getElementById("b" + qi).value;
          ok = [q.a].concat(q.accept || []).some(function (v) { return normBlank(st.obj["q" + qi]) === normBlank(v); });
        }
        var card = document.getElementById("q" + qi), why = document.getElementById("why" + qi);
        card.className = "qcard " + (ok ? "right" : "wrong");
        why.textContent = (ok ? "✓ 答对了。" : "× 正确答案：" + (q.kind === "single" ? "ABCD".charAt(q.a) : q.a) + "。") + q.why;
        why.style.display = "block";
        if (ok) score++;
      });
      st.objScore = score;
      document.getElementById("objScore").textContent = "得分：" + score + " / " + D.obj.length;
      saveUnitState(D, st);
    };

    var taskHost = document.getElementById("taskHost");
    taskHost.innerHTML = "";
    D.tasks.forEach(function (t) {
      var box = el("div", "task");
      var h = el("div");
      var nm = document.createElement("b"); nm.textContent = t.id + " · " + t.title;
      var db = el("span", "badge" + (st.tasks[t.id].done ? " done" : "")); db.textContent = st.tasks[t.id].done ? "已通过 ✓" : "未通过";
      h.appendChild(nm); h.appendChild(db); box.appendChild(h);
      var desc = el("div"); desc.style.margin = "6px 0"; desc.textContent = t.desc; box.appendChild(desc);
      var io = el("pre", "io"); io.textContent = "输入样例：\\n" + t.input + "\\n预期输出：\\n" + t.expect; box.appendChild(io);
      var ta = document.createElement("textarea");
      ta.value = lsGet("ds" + D.nn + "_draft_" + t.id + "_v1") || t.starter;
      ta.addEventListener("input", function () { lsSet("ds" + D.nn + "_draft_" + t.id + "_v1", ta.value); });
      box.appendChild(ta);
      var hbox = el("div", "hintbox");
      var hbtn = document.createElement("button"); hbtn.textContent = "展开三级提示";
      hbtn.style.marginTop = "6px";
      hbtn.onclick = function () {
        hbox.style.display = "block";
        hbox.textContent = t.hints.map(function (x, i) { return "提示" + (i + 1) + "：" + x; }).join("\\n");
      };
      box.appendChild(hbtn); box.appendChild(hbox);
      var paste = document.createElement("textarea"); paste.className = "paste"; paste.placeholder = "粘贴 IDLE 运行输出核对…";
      box.appendChild(paste);
      var msg = el("div", "msg");
      var cbtn = document.createElement("button"); cbtn.className = "primary"; cbtn.style.marginTop = "6px"; cbtn.textContent = "核对输出";
      cbtn.onclick = function () {
        if (paste.value.indexOf("Traceback") !== -1) { msg.className = "msg bad"; msg.textContent = "检测到 Traceback 报错，请先修正语法。"; return; }
        if (normOut(paste.value) === normOut(t.expect)) {
          st.tasks[t.id].done = true; saveUnitState(D, st);
          db.className = "badge done"; db.textContent = "已通过 ✓";
          msg.className = "msg ok"; msg.textContent = "核对通过，输出一致！";
        } else {
          msg.className = "msg bad"; msg.textContent = "输出不一致，请对照预期输出。";
        }
      };
      box.appendChild(cbtn); box.appendChild(msg);
      taskHost.appendChild(box);
    });
  }

  renderNav();
  renderUnit();
})();
</script>
</body>
</html>
"""


def generate_all():
    """生成全部练习页、模拟卷、导航主页与全课程单页。"""
    pages = []
    for lesson in LESSONS:
        html = render_page(lesson)
        out = COURSE_ROOT / f"第{lesson['nn']}讲_{lesson['dirname']}" / "练习.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(html)
        pages.append(out)
    for mock in MOCKS:
        html = render_page(mock)
        out = COURSE_ROOT / mock["filename"]
        with open(out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(html)
        pages.append(out)
    idx_out = TRACK_ROOT / "index.html"
    with open(idx_out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(DS_INDEX_HTML)
    pages.append(idx_out)
    all_out = TRACK_ROOT / "大数分解全课程.html"
    all_data = json.dumps(LESSONS + MOCKS, ensure_ascii=False).replace("</", "<\\/")
    with open(all_out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(DS_ALL_IN_ONE_HTML.replace("__ALL_DATA__", all_data))
    pages.append(all_out)
    import runpy
    daily = runpy.run_path(str(TRACK_ROOT.parent / "_工程文档" / "生成每日训练.py"))
    daily["write_track"](1)
    daily["link_track_portal"](1)
    return pages


def main():
    if "--selftest" in sys.argv:
        return run_selftest()
    if "--verify" in sys.argv:
        return run_verify()
    check_obj_data(LESSONS)
    check_obj_data(MOCKS, expected_obj=(12, 8, 4))
    pages = generate_all()
    for p in pages:
        print(f"生成 {p.relative_to(TRACK_ROOT.parent)}  ({len(p.read_text(encoding='utf-8'))} 字符)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

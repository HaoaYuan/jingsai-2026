#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成关卡.py -- 编程闯关 全部网页的唯一内容源（教师工具）

用法（在仓库任意目录运行均可）:
    python 工具/生成关卡.py             # 生成 10 个 HTML（地图 + 8 关 + 模拟关）
    python 工具/生成关卡.py --verify    # 先实跑全部编程任务参考解法比对预期输出，再生成
    python 工具/生成关卡.py --selftest  # 归一化与报错判定自测

环境：Python 3.9+ 标准库，Windows 10，离线。
"""

import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from html import escape as html_escape

TEACHER_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 01_编程闯关/教师与教案/
BASE = os.path.dirname(TEACHER_DIR)                                        # 01_编程闯关/
REPO = os.path.dirname(BASE)                                               # 仓库根
OUT_LEVELS = os.path.join(BASE, "练习与模拟")
OUT_INDEX = os.path.join(BASE, "index.html")
OUT_ALL = os.path.join(BASE, "编程闯关全课程.html")


# ---------------------------------------------------------------------------
# 输出归一化与报错判定（页面 JS 与本脚本 --verify 使用同一套规则）
# ---------------------------------------------------------------------------

def normalize_output(text):
    """归一化程序输出：逐行去首尾空白（含全角空格），去掉末尾空行。"""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    lines = [ln.strip(" \t　") for ln in lines]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def detect_traceback(text):
    """判断粘贴内容是否为 Python 报错信息。"""
    return "Traceback" in text


# ---------------------------------------------------------------------------
# --selftest：先于实现编写（TDD）
# ---------------------------------------------------------------------------

def run_selftest():
    cases = []

    # 用例 1：行尾空格 + 行首空格 + 末尾空行 应与紧凑版本等价
    cases.append(("归一化_去首尾空白与末尾空行",
                  normalize_output("a \n b\n\n") == "a\nb"))

    # 用例 2：多行中文输出全等比对
    expect = "你好，我是闯关新手\n这是我的第一个程序\n闯关开始"
    cases.append(("归一化_中文多行全等",
                  normalize_output(expect + "\n") == expect))

    # 用例 3：粘贴报错信息应被识别
    tb = "Traceback (most recent call last):\n  File \"t.py\", line 1, in <module>\nNameError: name 'n' is not defined"
    cases.append(("报错判定_Traceback被识别", detect_traceback(tb) is True))
    cases.append(("报错判定_正常输出不误判", detect_traceback(expect) is False))

    # 用例 4：全角空格被视为空白去除
    cases.append(("归一化_全角空格去除",
                  normalize_output("你好　世界　") == "你好　世界"))

    # 用例 5：客观题文本中的 < 必须转义，不得以原始 HTML 进入页面
    LEVELS[0]["index"] = 0
    host_html = render_page(LEVELS[0])
    cases.append(("转义_选项尖括号转义",
                  "&lt;!--" in host_html and "C. <!--" not in host_html))

    # 用例 6：判断题「对」「错」两个选项的 value 必须互异（对=true、错=false），
    # 否则任选其一都能命中答案，判断题判分失效
    cases.append(("判断题_两选项value互异",
                  '<input type="radio" name="q4" value="true"> 对</label>' in host_html and
                  '<input type="radio" name="q4" value="false"> 错</label>' in host_html))

    # 用例 7：全库客观题题干去重自检
    stems = []
    for lv in LEVELS + [FIN] + DRILLS:
        for q in lv["obj"]:
            stems.append(q["q"].strip())
    cases.append(("题库去重_无完全重复题干", len(stems) == len(set(stems))))

    failed = [name for name, ok in cases if not ok]
    for name, ok in cases:
        print(("PASS " if ok else "FAIL ") + name)
    total = len(cases)
    print("selftest: %d/%d 通过" % (total - len(failed), total))
    return 0 if not failed else 1


# ---------------------------------------------------------------------------
# 关卡数据（唯一内容源；单选题 a=正确选项下标，判断题 a=True/False）
# ---------------------------------------------------------------------------

LEVELS = [
    {
        "id": "L01", "file": "level01.html", "title": "初识 print", "topic": "print() 与注释",
        "obj": [
            {"t": "single", "q": "在 IDLE 中运行当前 .py 文件，按哪个键？",
             "opts": ["F1", "F5", "Ctrl + S", "Enter"], "a": 1,
             "why": "F5 是 Run Module（运行模块）；Ctrl + S 只是保存，不会运行。"},
            {"t": "single", "q": "下面哪一行能在屏幕上输出「你好」？",
             "opts": ["print(你好)", "print(\"你好\")", "print 你好", "echo(\"你好\")"], "a": 1,
             "why": "print 输出的文字要加引号；echo 不是 Python 的输出命令。"},
            {"t": "single", "q": "Python 的注释用什么符号开头？",
             "opts": ["//", "<!--", "#", "*"], "a": 2,
             "why": "Python 用 # 写注释；// 是某些其他语言的注释符，在 Python 里是整除运算。"},
            {"t": "single", "q": "运行下面两行代码，屏幕上输出几行？\nprint(\"a\")\nprint(\"b\")",
             "opts": ["0 行", "1 行", "2 行", "3 行"], "a": 2,
             "why": "每个 print 输出完会自动换行，所以 a 和 b 各占一行。"},
            {"t": "judge", "q": "代码 print（\"你好\"） 里的中文括号会让程序报错。",
             "a": True,
             "why": "Python 只认英文标点，中文括号、中文引号都会导致语法错误。"},
        ],
        "tasks": [
            {"id": "T1", "title": "第一声问候", "input": "无", "optional": False,
             "desc": "用 3 个 print，在屏幕上依次输出下面三行（文字要一模一样）：\n你好，我是闯关新手\n这是我的第一个程序\n闯关开始\n写好后按 F5 运行，把输出结果整段粘贴到下面的框里核对。",
             "starter": "# 用 3 个 print 输出三句话\n# 注意：只用英文标点\n",
             "expect": "你好，我是闯关新手\n这是我的第一个程序\n闯关开始",
             "hints": ["思路：一行输出用一个 print，三行就写三个 print。",
                       "步骤：每个 print 里的文字用英文引号包住，一行一句。",
                       "局部代码：print(\"你好，我是闯关新手\")"]},
        ],
    },
    {
        "id": "L02", "file": "level02.html", "title": "变量与字符串", "topic": "变量、字符串、print 逗号拼接",
        "obj": [
            {"t": "single", "q": "name = \"Python\"，运行 print(\"我在学\", name) 输出什么？",
             "opts": ["我在学Python", "我在学 Python", "报错", "name"], "a": 1,
             "why": "print 用逗号连接时，各项之间自动加一个空格。"},
            {"t": "single", "q": "下面哪个是合法的变量名？",
             "opts": ["2name", "my-name", "my_name", "class"], "a": 2,
             "why": "变量名不能数字开头、不能有连字符、不能用 class 这类保留字；下划线可以。"},
            {"t": "single", "q": "print(\"a\" + \"b\") 输出什么？",
             "opts": ["a b", "ab", "a+b", "报错"], "a": 1,
             "why": "字符串 + 字符串是拼接，中间不加空格（和逗号拼接区分开）。"},
            {"t": "single", "q": "运行 x = 1，再运行 x = 2，最后 print(x)，输出什么？",
             "opts": ["1", "2", "1 2", "报错"], "a": 1,
             "why": "后一次赋值会覆盖前一次，x 最终是 2。"},
            {"t": "judge", "q": "运行 name = \"小明\" 后再运行 name = \"小红\"，name 的值会变成「小红」。",
             "a": True,
             "why": "变量可以被重新赋值，新值覆盖旧值。"},
        ],
        "tasks": [
            {"id": "T1", "title": "自我介绍", "input": "无", "optional": False,
             "desc": "先造两个变量：name 的值为 \"Python\"，hobby 的值为 \"闯关\"。\n再用两个 print 输出下面两行（逗号拼接，注意空格）：\n我在学 Python\n我的爱好是 闯关\n把输出结果整段粘贴到下面的框里核对。",
             "starter": "# 造两个变量，再用逗号拼接输出\n# name = \"Python\"\n",
             "expect": "我在学 Python\n我的爱好是 闯关",
             "hints": ["思路：变量先赋值，print 里用逗号把文字和变量连起来。",
                       "步骤：第 1、2 行给 name 和 hobby 赋值；第 3、4 行分别输出。",
                       "局部代码：print(\"我在学\", name)"]},
        ],
    },
    {
        "id": "L03", "file": "level03.html", "title": "四则运算与整除", "topic": "/、//、% 与运算顺序",
        "obj": [
            {"t": "single", "q": "7 // 2 的结果是？",
             "opts": ["3.5", "3", "4", "2"], "a": 1,
             "why": "// 是整除，只取商的整数部分，不要小数。"},
            {"t": "single", "q": "7 % 2 的结果是？",
             "opts": ["3", "3.5", "1", "2"], "a": 2,
             "why": "% 取余数：7 = 2 × 3 + 1，余 1。"},
            {"t": "single", "q": "17 个像素每行摆 5 个，「能摆满几行」应该用哪个表达式算？",
             "opts": ["17 / 5", "17 // 5", "17 % 5", "5 // 17"], "a": 1,
             "why": "摆满的整行数是商，用整除 17 // 5 = 3；剩下几个才用 %。"},
            {"t": "single", "q": "2 + 3 * 2 的结果是？",
             "opts": ["10", "8", "12", "6"], "a": 1,
             "why": "先乘除后加减：3 * 2 = 6，再加 2 得 8。"},
            {"t": "judge", "q": "在 Python 里，7 / 2 的结果一定是整数。",
             "a": False,
             "why": "/ 是普通除法，结果带小数（7 / 2 = 3.5）；想取整要用 //。"},
        ],
        "tasks": [
            {"id": "T1", "title": "像素摆放", "input": "无", "optional": False,
             "desc": "17 个像素，每行摆 5 个。用 // 和 % 各算一次，输出下面两行：\n能摆满 3 行\n还剩 2 个\n把输出结果整段粘贴到下面的框里核对。",
             "starter": "# pixels 是总数，per 是每行个数\npixels = 17\nper = 5\n# 用 // 和 % 输出两行\n",
             "expect": "能摆满 3 行\n还剩 2 个",
             "hints": ["思路：摆满的行数用 //，剩下几个用 %。",
                       "步骤：两个 print，每个里面用逗号连接文字和算式。",
                       "局部代码：print(\"能摆满\", pixels // per, \"行\")"]},
        ],
    },
    {
        "id": "L04", "file": "level04.html", "title": "输入与类型转换", "topic": "input() 与 int()",
        "obj": [
            {"t": "single", "q": "运行 n = input()，用户输入了 5，此时 n 是什么类型？",
             "opts": ["整数", "字符串", "小数", "布尔值"], "a": 1,
             "why": "input() 拿到的永远是字符串，就算看起来像数字。"},
            {"t": "single", "q": "想让输入的 5 能参与加法运算，应该先做哪一步？",
             "opts": ["int(n)", "str(n)", "print(n)", "不用处理"], "a": 0,
             "why": "用 int() 把字符串转成整数后才能做数学运算。"},
            {"t": "single", "q": "运行 int(\"abc\") 会发生什么？",
             "opts": ["得到 0", "报错", "得到 123", "得到 \"abc\""], "a": 1,
             "why": "\"abc\" 不是数字，int() 转不了，程序会报 ValueError。"},
            {"t": "single", "q": "n = int(\"12\")，那么 n + 3 的结果是？",
             "opts": ["15", "\"123\"", "123", "报错"], "a": 0,
             "why": "int(\"12\") 已经是数字 12，加 3 得 15。"},
            {"t": "judge", "q": "input(\"请输入：\") 括号里的文字会先显示在屏幕上提示用户。",
             "a": True,
             "why": "input 括号里的字符串是提示语，先显示再等用户输入。"},
        ],
        "tasks": [
            {"id": "T1", "title": "求和与差", "input": "7\n3", "optional": False,
             "desc": "程序运行后分两行读入两个整数（运行时先输 7 回车，再输 3 回车）。\n输出下面两行：\n两个数的和是 10\n两个数的差是 4\n把输出结果整段粘贴到下面的框里核对。",
             "starter": "# 用两次 int(input()) 读入两个数\n# a = int(input())\n",
             "expect": "两个数的和是 10\n两个数的差是 4",
             "hints": ["思路：input 拿到的是字符串，必须先 int() 再做加减。",
                       "步骤：读 a、b；一个 print 输出 a + b，一个输出 a - b。",
                       "局部代码：a = int(input())"]},
        ],
    },
    {
        "id": "L05", "file": "level05.html", "title": "让程序判断", "topic": "if / elif / else",
        "obj": [
            {"t": "single", "q": "x = 7，运行：\nif x > 5:\n    print(\"大\")\n输出什么？",
             "opts": ["大", "什么都不输出", "小", "报错"], "a": 0,
             "why": "7 > 5 成立，执行 if 下缩进的 print。"},
            {"t": "single", "q": "score = 85，规则：90 及以上「优秀」，80 及以上「良好」。运行：\nif score >= 90:\n    print(\"优秀\")\nelif score >= 80:\n    print(\"良好\")\n输出什么？",
             "opts": ["优秀", "良好", "优秀和良好", "报错"], "a": 1,
             "why": "条件从上往下检查，85 不满足第一个条件，落到 elif 输出「良好」。"},
            {"t": "single", "q": "判断两个值是否相等，用哪个符号？",
             "opts": ["=", "==", "===", "eq"], "a": 1,
             "why": "一个 = 是赋值，两个 == 才是比较是否相等。"},
            {"t": "single", "q": "运行 x = 10 之后，再运行 if x = 10: 会怎样？",
             "opts": ["正常判断", "报错", "输出 10", "死循环"], "a": 1,
             "why": "条件里不能用赋值的 =，会直接语法报错，必须写 ==。"},
            {"t": "judge", "q": "if 下面要执行的 print，必须缩进（前面加空格），否则报错。",
             "a": True,
             "why": "Python 用缩进表示「这行属于 if」，不缩进程序不知道哪些受 if 管。"},
        ],
        "tasks": [
            {"id": "T1", "title": "分数定等级", "input": "无", "optional": False,
             "desc": "score = 78。规则：90 及以上输出「优秀」，80 及以上输出「良好」，60 及以上输出「及格」，否则输出「不及格」。\n输出下面这一行：\n78 分的等级是：及格\n把输出结果整段粘贴到下面的框里核对。",
             "starter": "score = 78\n# 用 if / elif / elif / else 判断，把等级存进变量 level\n# 最后输出：print(\"78 分的等级是：\" + level)\n",
             "expect": "78 分的等级是：及格",
             "hints": ["思路：从大到小依次判断，先 90 再 80 再 60，都不满足用 else。",
                       "步骤：每个分支里给 level 赋一个等级文字，最后统一输出。",
                       "局部代码：elif score >= 80:（下一行写 level = \"良好\"）"]},
        ],
    },
    {
        "id": "L06", "file": "level06.html", "title": "for 循环", "topic": "for 与 range()、累加",
        "obj": [
            {"t": "single", "q": "range(1, 101) 包含的最大数是？",
             "opts": ["100", "101", "99", "1"], "a": 0,
             "why": "range 含头不含尾：从 1 开始，到 100 为止，不含 101。"},
            {"t": "single", "q": "用 for 循环累加时，total = 0 应该写在哪里？",
             "opts": ["循环外面（前面）", "循环里面", "程序最后一行", "不用写"], "a": 0,
             "why": "累加变量要在循环前清零一次；写进循环里每圈都被清成 0。"},
            {"t": "single", "q": "range(3) 生成的数是？",
             "opts": ["1, 2, 3", "0, 1, 2", "0, 1, 2, 3", "只有一个 3"], "a": 1,
             "why": "range(3) 等价于 range(0, 3)：从 0 数到 2。"},
            {"t": "single", "q": "for i in range(1, 4): print(i) 输出几行？",
             "opts": ["3 行", "4 行", "1 行", "2 行"], "a": 0,
             "why": "range(1, 4) 是 1、2、3 共三个数，每个数输出一行。"},
            {"t": "judge", "q": "for 循环里的 total = total + i，循环转一圈就执行一次。",
             "a": True,
             "why": "循环体每圈执行一遍，所以 total 一圈圈累加上去。"},
        ],
        "tasks": [
            {"id": "T1", "title": "一百的求和", "input": "无", "optional": False,
             "desc": "用 for 循环把 1 到 100 每个数加起来，输出下面这一行：\n1 到 100 的总和是 5050\n把输出结果整段粘贴到下面的框里核对。",
             "starter": "total = 0\n# 用 for 和 range(1, 101) 累加\n# 最后在循环外面输出 total\n",
             "expect": "1 到 100 的总和是 5050",
             "hints": ["思路：total 在循环外先置 0，循环里一圈加一个数。",
                       "步骤：for i in range(1, 101): 循环体写 total = total + i。",
                       "局部代码：total = total + i"]},
            {"id": "T2", "title": "乘法口诀第 3 行（选做）", "input": "无", "optional": True,
             "desc": "用 for 循环输出乘法口诀第 3 行（一行内，用空格分隔）：\n3x1=3 3x2=6 3x3=9\n提示：end=\" \" 能让 print 不换行。选做不影响盖章，做出来很厉害。",
             "starter": "# for i in range(1, 4):\n#     print(..., end=\" \")\n# 最后补一个 print() 换行\n",
             "expect": "3x1=3 3x2=6 3x3=9",
             "hints": ["思路：循环 3 次，每次输出一段，用 end=\" \" 防止换行。",
                       "步骤：循环里把 3、i、3*i 拼起来输出，循环后写一个 print()。",
                       "局部代码：print(\"3x\" + str(i) + \"=\" + str(3 * i), end=\" \")"]},
        ],
    },
    {
        "id": "L07", "file": "level07.html", "title": "字符串索引与 len", "topic": "len()、s[i] 取字符",
        "obj": [
            {"t": "single", "q": "s = \"1011010\"，s[0] 是什么？",
             "opts": ["\"1\"", "\"0\"", "数字 1", "报错"], "a": 0,
             "why": "索引从 0 开始数，s[0] 是第一个字符 \"1\"。"},
            {"t": "single", "q": "len(\"1011010\") 的结果是？",
             "opts": ["6", "7", "8", "0"], "a": 1,
             "why": "len 数出字符串共 7 个字符。"},
            {"t": "single", "q": "s = \"1011010\"，想取「第 3 个字符」（按人类习惯从 1 数），用哪个写法？",
             "opts": ["s[3]", "s[2]", "s[1]", "s[4]"], "a": 1,
             "why": "第 1 个是 s[0]，第 2 个是 s[1]，第 3 个是 s[2]。"},
            {"t": "single", "q": "s 是 7 个字符，运行 s[7] 会怎样？",
             "opts": ["输出 \"0\"", "报错 IndexError", "输出空", "输出 7"], "a": 1,
             "why": "索引最大到 6；s[7] 越界，报 IndexError。"},
            {"t": "judge", "q": "s[-1] 表示字符串的最后一个字符。",
             "a": True,
             "why": "负索引从后往前数，-1 就是最后一个。"},
        ],
        "tasks": [
            {"id": "T1", "title": "检查 0/1 串", "input": "无", "optional": False,
             "desc": "s = \"1011010\"。输出下面三行：\n长度是 7\n第 3 个字符是 1\n最后一个字符是 0\n把输出结果整段粘贴到下面的框里核对。",
             "starter": "s = \"1011010\"\n# 用 len(s)、s[2]、s[6] 输出三行\n",
             "expect": "长度是 7\n第 3 个字符是 1\n最后一个字符是 0",
             "hints": ["思路：长度用 len；第 3 个字符按 0 起算取 s[2]；最后一个取 s[6]。",
                       "步骤：三个 print，都用逗号连接文字和取值。",
                       "局部代码：print(\"第 3 个字符是\", s[2])"]},
        ],
    },
    {
        "id": "L08", "file": "level08.html", "title": "综合小试", "topic": "读代码、累乘、综合排查",
        "obj": [
            {"t": "single", "q": "运行：\ntotal = 0\nfor i in range(1, 4):\n    total = total + i\nprint(total)\n输出什么？",
             "opts": ["6", "4", "10", "3"], "a": 0,
             "why": "range(1, 4) 是 1、2、3，累加得 6。"},
            {"t": "single", "q": "运行：\nresult = 1\nfor i in range(1, 4):\n    result = result * i\nprint(result)\n输出什么？",
             "opts": ["6", "12", "3", "1"], "a": 0,
             "why": "累乘从 1 开始：1 × 1 × 2 × 3 = 6。"},
            {"t": "single", "q": "输入 5，运行 n = int(input())，那么 range(1, n + 1) 里有几个数？",
             "opts": ["5", "6", "4", "1"], "a": 0,
             "why": "range(1, 6) 含头不含尾，是 1 到 5 共 5 个数；n + 1 正好把 n 自己包进来。"},
            {"t": "single", "q": "n 是整数，下面哪种写法会报错？",
             "opts": ["print(\"结果是\", n)", "print(\"结果是\" + n)", "print(\"结果是\" + str(n))", "print(f\"结果是{n}\")"], "a": 1,
             "why": "字符串 + 数字不能直接相加；逗号、str() 转换、f-string 都可以。"},
            {"t": "single", "q": "程序报错 NameError: name 'n' is not defined，最可能的原因是？",
             "opts": ["使用了没赋值过的变量名", "语法错误", "缩进错误", "用了中文标点"], "a": 0,
             "why": "NameError 是「变量名未定义」：用了一个从没赋过值的变量。"},
        ],
        "tasks": [
            {"id": "T1", "title": "阶乘计算器", "input": "5", "optional": False,
             "desc": "程序运行后读入一个整数（运行时输入 5 回车），用 for 循环算 1 × 2 × … × n，输出下面这一行：\n5 的阶乘是 120\n把输出结果整段粘贴到下面的框里核对。",
             "starter": "n = int(input())\nresult = 1\n# 用 for 和 range(1, n + 1) 累乘\n",
             "expect": "5 的阶乘是 120",
             "hints": ["思路：累乘器和累加器类似，但要从 1 开始，循环里乘。",
                       "步骤：for i in range(1, n + 1): 循环体写 result = result * i。",
                       "局部代码：result = result * i"]},
        ],
    },
]

FIN = {
    "id": "FIN", "file": "final.html", "title": "全真模拟关", "topic": "限时 40 分钟 · 覆盖 L1–L8",
    "timeLimitMin": 40,
    "obj": [
        {"t": "single", "q": "9 // 4 的结果是？",
         "opts": ["2.25", "2", "3", "2.0"], "a": 1,
         "why": "// 整除取商的整数部分：9 = 4 × 2 + 1。"},
        {"t": "single", "q": "input() 从键盘拿到的东西是什么类型？",
         "opts": ["整数", "字符串", "小数", "取决于输入内容"], "a": 1,
         "why": "永远是字符串，需要数字时要 int() 转换。"},
        {"t": "single", "q": "判断两个值是否相等用哪个符号？",
         "opts": ["=", "==", "===", "!="], "a": 1,
         "why": "= 是赋值，== 才是判断相等；!= 是判断不等。"},
        {"t": "single", "q": "range(1, 6) 一共生成几个数？",
         "opts": ["5", "6", "4", "7"], "a": 0,
         "why": "含头不含尾：1、2、3、4、5 共 5 个。"},
        {"t": "single", "q": "s = \"110\"，len(s) 的结果是？",
         "opts": ["3", "2", "4", "110"], "a": 0,
         "why": "len 数字符个数。"},
        {"t": "single", "q": "用 for 累加 1 到 n，total = 0 应写在哪里？",
         "opts": ["循环外面前面", "循环里面", "循环后面", "随意"], "a": 0,
         "why": "清零一次放在循环前；放循环里会被反复清零。"},
        {"t": "single", "q": "s = \"1010\"，s[1] 是哪个字符？",
         "opts": ["\"0\"", "\"1\"", "报错", "整个字符串"], "a": 0,
         "why": "索引从 0 起：s[0] 是 \"1\"，s[1] 是 \"0\"。"},
        {"t": "judge", "q": "Python 的注释用 # 开头。",
         "a": True, "why": "# 后面的内容程序不执行。"},
        {"t": "judge", "q": "print(\"a\", \"b\") 的输出是 ab（中间没有空格）。",
         "a": False, "why": "逗号拼接会自动加一个空格，输出是 a b。"},
        {"t": "judge", "q": "if 下面要执行的代码必须缩进。",
         "a": True, "why": "缩进表明这些代码受 if 管理，不缩进会报错。"},
    ],
    "tasks": [
        {"id": "TA", "title": "商与余数", "input": "17\n5", "optional": False,
         "desc": "程序运行后分两行读入两个整数（先输 17 回车，再输 5 回车），输出下面两行：\n17 // 5 = 3\n17 % 5 = 2\n把输出结果整段粘贴到下面的框里核对。",
         "starter": "# 读入 a、b，用 // 和 % 输出两行\n",
         "expect": "17 // 5 = 3\n17 % 5 = 2",
         "hints": ["思路：两个 int(input()) 读入，// 一行、% 一行。",
                   "步骤：print 里逗号连接 a、\"//\"、b、\"=\"、算式。",
                   "局部代码：print(a, \"//\", b, \"=\", a // b)"]},
        {"id": "TB", "title": "三的倍数", "input": "无", "optional": False,
         "desc": "输出 1 到 20 中所有 3 的倍数，每个数占一行，共 6 行：\n3\n6\n9\n12\n15\n18\n把输出结果整段粘贴到下面的框里核对。",
         "starter": "# for 循环 1 到 20，用 % 判断是不是 3 的倍数\n",
         "expect": "3\n6\n9\n12\n15\n18",
         "hints": ["思路：循环 1 到 20，if i % 3 == 0 就输出。",
                   "步骤：for 和 if 嵌套时，if 的输出行要缩进两层。",
                   "局部代码：if i % 3 == 0:"]},
    ],
}


# ---------------------------------------------------------------------------
# 赛前加练卷（2026-11-16 新增）：不限时练习卷，随时可练；obj 不与各关重复
# ---------------------------------------------------------------------------

DRILLS = [
    {
        "id": "DRA", "file": "drillA.html", "title": "加练 A · 基础巩固卷", "topic": "覆盖 L1–L5：print、变量、运算、输入、判断", "drill": True,
        "obj": [
            {"t": "single", "q": "运行 print(\"3+4\")，屏幕上输出什么？",
             "opts": ["3+4", "7", "34", "报错"], "a": 0,
             "why": "引号里是文字，原样显示；想让 Python 算出 7，要去掉引号写 print(3 + 4)。"},
            {"t": "single", "q": "price = 5，运行 print(\"price\") 输出什么？",
             "opts": ["5", "price", "报错", "空白"], "a": 1,
             "why": "引号里的 price 是文字，不是变量；想输出变量的值要去掉引号写 print(price)。"},
            {"t": "single", "q": "下面哪个变量名是合法的？",
             "opts": ["my name", "2pm", "score_1", "for"], "a": 2,
             "why": "变量名不能有空格、不能数字开头、不能用 for 这类保留字；score_1 合法。"},
            {"t": "single", "q": "10 % 4 的结果是？",
             "opts": ["2", "2.5", "1", "0"], "a": 0,
             "why": "% 取余数：10 = 4 × 2 + 2，余 2。"},
            {"t": "single", "q": "2 + 3 * 4 的结果是？",
             "opts": ["20", "14", "24", "10"], "a": 1,
             "why": "先乘除后加减：3 × 4 = 12，再加 2 得 14。"},
            {"t": "single", "q": "n = int(\"15\")，n + 5 的结果是？",
             "opts": ["155", "报错", "\"155\"", "20"], "a": 3,
             "why": "int(\"15\") 已经是数字 15，15 + 5 = 20。"},
            {"t": "single", "q": "运行：\nnum = 7\nif num % 2 == 0:\n    print(\"偶数\")\nelse:\n    print(\"奇数\")\n输出什么？",
             "opts": ["偶数", "偶数和奇数", "奇数", "报错"], "a": 2,
             "why": "7 % 2 = 1，不等于 0，条件不成立，走 else 输出「奇数」。"},
            {"t": "judge", "q": "变量名不区分大小写：Age 和 age 是同一个变量。",
             "a": False,
             "why": "Python 区分大小写，Age、age、AGE 是三个互相独立的变量名，改成 age 不会影响 Age。"},
            {"t": "judge", "q": "输入 8 后运行 n = input()，接着运行 n + 1 会报错。",
             "a": True,
             "why": "input() 拿到的是字符串 \"8\"，文字不能和数字相加；要先 n = int(input())。"},
            {"t": "judge", "q": "print() 的括号里可以一次写多项，用逗号隔开，输出时各项之间自动加一个空格。",
             "a": True,
             "why": "逗号拼接是 print 的基本用法：print(\"a\", \"b\") 输出 a b。"},
        ],
        "tasks": [
            {"id": "TA", "title": "身份卡", "input": "无", "optional": False,
             "desc": "先造两个变量：name 的值为 \"小明\"，score 的值为 96。用 + 拼接输出下面两行：\n姓名：小明\n得分：96\n提示：数字拼进文字前要用 str() 转换。把输出结果整段粘贴到下面的框里核对。",
             "starter": "# 造 name 和 score 两个变量，再用 + 拼接输出\n",
             "expect": "姓名：小明\n得分：96",
             "hints": ["思路：文字和变量用 + 拼接；数字拼进文字前要 str() 转换。",
                       "步骤：前两行给 name、score 赋值；后两行 print 用 + 连接。",
                       "局部代码：print(\"得分：\" + str(score))"]},
            {"id": "TB", "title": "较大的数", "input": "7\n3", "optional": False,
             "desc": "程序运行后分两行读入两个整数（先输 7 回车，再输 3 回车），比较后输出下面这一行：\n较大的数是 7\n把输出结果整段粘贴到下面的框里核对。",
             "starter": "# 用两次 int(input()) 读入 a、b\n# 用 if / else 比较大小，输出较大的\n",
             "expect": "较大的数是 7",
             "hints": ["思路：if a > b 输出 a，否则输出 b。",
                       "步骤：读入后比较，print 里逗号连接文字和较大的数。",
                       "局部代码：if a > b:"]},
            {"id": "TC", "title": "秒数换算", "input": "130", "optional": False,
             "desc": "程序运行后读入一个秒数（运行时输入 130 回车），换算成几分几秒，输出下面这一行：\n130 秒 = 2 分 10 秒\n提示：分用 // 60 算，秒用 % 60 算。把输出结果整段粘贴到下面的框里核对。",
             "starter": "n = int(input())\n# 用 // 和 % 算出分与秒\n",
             "expect": "130 秒 = 2 分 10 秒",
             "hints": ["思路：分 = n // 60，秒 = n % 60。",
                       "步骤：一个 print，逗号连接 n、\"秒 =\"、算式、单位。",
                       "局部代码：print(n, \"秒 =\", n // 60, \"分\", n % 60, \"秒\")"]},
        ],
    },
    {
        "id": "DRB", "file": "drillB.html", "title": "加练 B · 综合模拟卷", "topic": "覆盖 L1–L8：判断、循环、字符串、综合排查", "drill": True,
        "obj": [
            {"t": "single", "q": "运行：\nn = 3\nif n > 1:\n    print(\"甲\")\nprint(\"乙\")\n输出几行？",
             "opts": ["0 行", "1 行", "2 行", "报错"], "a": 2,
             "why": "print(\"乙\") 没有缩进，不受 if 管，无论条件是否成立都会执行；所以甲、乙各一行。"},
            {"t": "single", "q": "下面四行代码里，哪一行有错误？\n① total = 0\n② for i in range(1, 4)\n③     total = total + i\n④ print(total)",
             "opts": ["①", "②", "③", "④"], "a": 1,
             "why": "for 那一行行末缺英文冒号，会报 SyntaxError；补上 : 即可。"},
            {"t": "single", "q": "\"7\" + \"8\" 的结果是？",
             "opts": ["78", "15", "7 8", "报错"], "a": 0,
             "why": "两个都是字符串，+ 是拼接，得到 \"78\"；想算出 15 要先 int(\"7\") + int(\"8\")。"},
            {"t": "single", "q": "len(\"hello world\") 的结果是？",
             "opts": ["9", "10", "11", "报错"], "a": 2,
             "why": "空格也是字符：5 个字母 + 1 个空格 + 5 个字母 = 11 个字符。"},
            {"t": "single", "q": "s = \"Python\"，print(s[1] + s[0]) 输出什么？",
             "opts": ["Py", "yt", "报错", "yP"], "a": 3,
             "why": "s[1] 是 \"y\"，s[0] 是 \"P\"，+ 拼接得 \"yP\"（顺序按写的来）。"},
            {"t": "single", "q": "运行：\nresult = 1\nfor i in range(1, 7):\n    result = result * i\nprint(result)\n输出什么？",
             "opts": ["720", "21", "5040", "7"], "a": 0,
             "why": "range(1, 7) 是 1 到 6，累乘 1×2×3×4×5×6 = 720（6 的阶乘）。"},
            {"t": "single", "q": "print(\"总分:\", 80 + 20) 输出什么？",
             "opts": ["总分: 80 + 20", "总分: 100", "总分:80+20", "报错"], "a": 1,
             "why": "引号外的 80 + 20 先算出 100，再和文字逗号拼接，中间自动加一个空格。"},
            {"t": "judge", "q": "range(1, 10) 能生成 10。",
             "a": False,
             "why": "range 含头不含尾：到 9 为止，不含 10；想包含 10 要写 range(1, 11)。"},
            {"t": "judge", "q": "str(45) 的结果是字符串 \"45\"，可以和别的文字拼接。",
             "a": True,
             "why": "str() 把数字变成文字；\"得分：\" + str(45) 就能拼出「得分：45」。"},
            {"t": "judge", "q": "print() 括号里什么都不写，运行后会输出一个空行。",
             "a": True,
             "why": "print() 不带参数就是换一行，常用来在循环输出后补一个空行。"},
        ],
        "tasks": [
            {"id": "TA", "title": "偶数求和", "input": "10", "optional": False,
             "desc": "程序运行后读入一个整数 n（运行时输入 10 回车），算出 1 到 n 中所有偶数的和，输出下面这一行：\n10 以内偶数的和是 30\n把输出结果整段粘贴到下面的框里核对。",
             "starter": "n = int(input())\ntotal = 0\n# for 循环 1 到 n，if i % 2 == 0 就累加\n",
             "expect": "10 以内偶数的和是 30",
             "hints": ["思路：循环 1 到 n（range(1, n + 1)），if i % 2 == 0 就 total = total + i。",
                       "步骤：循环结束后，在循环外输出 total。",
                       "局部代码：if i % 2 == 0:"]},
            {"id": "TB", "title": "数 1 的个数", "input": "1011010", "optional": False,
             "desc": "程序运行后读入一行 0/1 串（运行时输入 1011010 回车），数出其中字符 \"1\" 的个数，输出下面这一行：\n1 的个数是 4\n提示：for i in range(len(s)): 用 s[i] 取出每个字符和 \"1\" 比较。把输出结果整段粘贴到下面的框里核对。",
             "starter": "s = input()\ncount = 0\n# for 循环 len(s) 次，s[i] 是第 i 个字符\n",
             "expect": "1 的个数是 4",
             "hints": ["思路：for i in range(len(s)): 一圈取一个字符 s[i]。",
                       "步骤：if s[i] == \"1\": 就 count = count + 1。",
                       "局部代码：if s[i] == \"1\":"],
             },
            {"id": "TC", "title": "乘法口诀第 n 行", "input": "4", "optional": False,
             "desc": "程序运行后读入一个整数 n（运行时输入 4 回车），输出乘法口诀第 n 行（一行内，用空格分隔）：\n4x1=4 4x2=8 4x3=12 4x4=16\n提示：end=\" \" 能让 print 不换行；数字拼进文字用 str()。把输出结果整段粘贴到下面的框里核对。",
             "starter": "n = int(input())\n# for i in range(1, n + 1):\n#     print(..., end=\" \")\n# 循环后补一个 print()\n",
             "expect": "4x1=4 4x2=8 4x3=12 4x4=16",
             "hints": ["思路：循环 n 次，每次输出一段，用 end=\" \" 防止换行。",
                       "步骤：循环里把 n、i、n*i 拼起来输出，循环后写一个 print()。",
                       "局部代码：print(str(n) + \"x\" + str(i) + \"=\" + str(n * i), end=\" \")"]},
        ],
    },
    {
        "id": "MK1", "file": "mock01.html", "title": "每日模拟一 · 60 分钟综合卷", "topic": "限时 60 分钟 · 15 道客观题 + 4 道编程题（覆盖 L1–L8，零重复）", "drill": True, "timeLimitMin": 60,
        "obj": [
            {"t": "single", "q": "运行：\na = 3\nb = 8\nt = a\na = b\nb = t\nprint(a, b)\n输出什么？",
             "opts": ["8 3", "3 8", "8 8", "3 3"], "a": 0,
             "why": "t 先暂存了 a 原来的值 3，然后 b 的 8 覆盖 a，最后把 t 里的 3 放进 b，完成两个变量的值交换，输出 8 3。"},
            {"t": "single", "q": "表达式 (2 + 1) ** 2 - 4 的结果是？",
             "opts": ["2", "3", "5", "1"], "a": 2,
             "why": "** 是幂运算（乘方）。先算括号里 2 + 1 = 3，再算 3 的 2 次方等于 9，最后 9 - 4 = 5。"},
            {"t": "single", "q": "运行：\nm = 10\nm = m - 3\nm = m * 2\nprint(m)\n输出什么？",
             "opts": ["10", "4", "17", "14"], "a": 3,
             "why": "按从上到下顺序一步步更新：m 先变成 10 - 3 = 7，再变成 7 × 2 = 14。"},
            {"t": "single", "q": "执行 print(\"2026\", \"11\", \"30\", sep=\"-\")，屏幕上显示什么？",
             "opts": ["2026 11 30", "2026-11-30", "20261130", "报错"], "a": 1,
             "why": "sep=\"-\" 可以把 print 逗号之间的默认分隔符（空格）改成短横线 \"-\"，所以输出 2026-11-30。"},
            {"t": "single", "q": "运行 print(\"得分：\" + 95) 时，程序会报哪一种错误？",
             "opts": ["TypeError", "SyntaxError", "IndexError", "ValueError"], "a": 0,
             "why": "字符串和整数不能直接用 + 相加，这是类型不匹配，报 TypeError；改成 str(95) 或用逗号分隔即可。"},
            {"t": "single", "q": "运行：\nn = 12\nif n % 2 == 0:\n    print(\"偶\")\nif n % 3 == 0:\n    print(\"三\")\n输出什么？",
             "opts": ["只输出「偶」", "只输出「三」", "两行：先「偶」再「三」", "什么都不输出"], "a": 2,
             "why": "这是两个独立的 if（不是 elif），12 既能被 2 整除又能被 3 整除，所以两个条件都会成立并依次执行。"},
            {"t": "single", "q": "某项目限高规则：\nif h >= 140:\n    print(\"全票\")\nelif h >= 110:\n    print(\"半票\")\nelse:\n    print(\"免票\")\n当 h = 140 时，输出什么？",
             "opts": ["半票", "全票", "免票", "全票和半票"], "a": 1,
             "why": ">= 包含等于，140 >= 140 成立，直接命中第一条分支输出「全票」，后面的 elif 不再检查。"},
            {"t": "single", "q": "运行：\nans = 0\nfor i in range(1, 5):\n    if i % 2 == 0:\n        ans = ans + i\n    else:\n        ans = ans - 1\nprint(ans)\n输出什么？",
             "opts": ["10", "2", "6", "4"], "a": 3,
             "why": "i=1 奇数减 1 得 -1；i=2 偶数加 2 得 1；i=3 奇数减 1 得 0；i=4 偶数加 4 得 4。"},
            {"t": "single", "q": "运行：\nc = 0\nfor i in range(3):\n    for j in range(4):\n        c = c + 1\nprint(c)\n输出什么？",
             "opts": ["12", "7", "3", "4"], "a": 0,
             "why": "外层循环走 3 圈，每走 1 圈内层循环都走 4 圈，一共执行 3 × 4 = 12 次，c 最终为 12。"},
            {"t": "single", "q": "s = \"ABCDEF\"，执行 print(s[1:4]) 输出什么？",
             "opts": ["ABCD", "BCDE", "BCD", "CDE"], "a": 2,
             "why": "切片 s[1:4] 含头不含尾：从下标 1（'B'）切到下标 3（'D'），不含下标 4（'E'），结果是 BCD。"},
            {"t": "single", "q": "msg = \"2026 python\"，运行 print(\"py\" in msg, \"Py\" in msg) 输出什么？",
             "opts": ["True True", "True False", "False True", "报错"], "a": 1,
             "why": "in 检查子串是否出现且区分大小写：\"py\" 在 msg 里为 True，大写的 \"Py\" 不在里面为 False。"},
            {"t": "judge", "q": "当 a = 9、b = 4 时，a // b 和 int(a / b) 计算得到的结果都是整数 2。",
             "a": True,
             "why": "9 // 4 = 2；9 / 4 = 2.25，套一层 int(2.25) 会截断小数部分，同样得到整数 2。"},
            {"t": "judge", "q": "已知 s = \"hello\"，运行 s[0] = \"H\" 可以把字符串首字母改成大写的 \"H\"。",
             "a": False,
             "why": "Python 的字符串是不可变类型，不能通过 s[0] = ... 直接修改其中某个字符，会报 TypeError。"},
            {"t": "judge", "q": "在循环里写 print(i, end=\"\")，所有输出会紧挨着显示在同一行，中间没有任何空格。",
             "a": True,
             "why": "end=\"\" 把默认的换行符替换成了空字符串，所以每次打印后既不换行也不多加空格。"},
            {"t": "judge", "q": "for i in range(10, 1): 会让 i 从 10 倒着数到 2，一共执行 9 圈。",
             "a": False,
             "why": "不写第 3 个步长参数时默认每次 +1，起始值 10 比结束值 1 大时，range(10, 1) 为空，循环 0 圈直接跳过。"},
        ],
        "tasks": [
            {"id": "TA", "title": "到达时间计算", "input": "8\n40\n135", "optional": False,
             "desc": "分三行读入三个整数：出发小时 h（输入 8 回车）、出发分钟 m（输入 40 回车）、路程总耗时分钟数 add（输入 135 回车，保证不跨天）。\n请算出一共是几时几分，输出格式如下：\n到达时间 10:55\n提示：先算出总分钟数 total = h * 60 + m + add，再用 // 60 和 % 60 拆成时和分。",
             "starter": "h = int(input())\nm = int(input())\nadd = int(input())\n# 先转成总分钟数，再加上耗时，最后拆回时和分\n",
             "expect": "到达时间 10:55",
             "hints": ["思路：直接给 m 加 135 会超过 60，先全部换算成分钟 total = h * 60 + m + add 最不容易出错。",
                       "步骤：小时 new_h = total // 60，分钟 new_m = total % 60；注意用 str() 和 \":\" 拼在一起。",
                       "局部代码：print(\"到达时间\", str(new_h) + \":\" + str(new_m))"]},
            {"id": "TB", "title": "阶梯电费计费", "input": "180", "optional": False,
             "desc": "读入本月用电度数 kwh（输入 180 回车）。按阶梯累加收费：前 100 度（含 100 度）每度 0.5 元；超出 100 度的部分每度 0.8 元。\n输入 180 应输出：\n总电费 114.0 元\n提示：先判断 kwh <= 100；若超过 100，前 100 度按 0.5 元算，多出的 (kwh - 100) 度按 0.8 元算后相加。",
             "starter": "kwh = int(input())\n# 用 if / else 分别计算不超过 100 度和超过 100 度的电费\n",
             "expect": "总电费 114.0 元",
             "hints": ["思路：阶梯计费不是整体乘 0.8，而是把 180 度拆成「前 100 度」和「超出的 80 度」两段分别计价再相加。",
                       "步骤：if kwh <= 100: fee = kwh * 0.5，else: fee = 100 * 0.5 + (kwh - 100) * 0.8。",
                       "局部代码：fee = 100 * 0.5 + (kwh - 100) * 0.8"]},
            {"id": "TC", "title": "数字串求和与非零统计", "input": "20261130", "optional": False,
             "desc": "读入一串纯数字字符串 s（运行时输入 20261130 回车），用 for 循环逐个取出每一位，累加全部数字的和，同时统计其中非零数字（不是 \"0\"）的个数，输出两行：\n各位数字之和是 15\n非零数字有 6 个",
             "starter": "s = input()\ntotal = 0\nnonzero = 0\n# for i in range(len(s)):\n#     把 s[i] 转成 int(s[i]) 累加，并判断是否 > 0\n",
             "expect": "各位数字之和是 15\n非零数字有 6 个",
             "hints": ["思路：把输入当字符串读进来就能用下标 s[i] 逐位访问，再用 int(s[i]) 转成整数加进 total。",
                       "步骤：循环里写 d = int(s[i])，total = total + d，再 if d != 0: 让 nonzero 加 1。",
                       "局部代码：d = int(s[i])\n    total = total + d\n    if d != 0:\n        nonzero = nonzero + 1"]},
            {"id": "TD", "title": "字符串数字脱敏", "input": "ab12c34d", "optional": False,
             "desc": "读入一行包含字母和数字的字符串 s（运行时输入 ab12c34d 回车）。逐个检查每个字符，把所有数字字符（\"0\" <= ch <= \"9\"）替换成 \"*\" 拼成新串 res，并统计共替换了多少个数字，输出两行：\n脱敏结果：ab**c**d\n共替换了 4 个数字",
             "starter": "s = input()\nres = \"\"\ncnt = 0\n# for i in range(len(s)):\n#     ch = s[i]\n#     如果是数字字符，res 拼 \"*\" 且 cnt 加 1；否则直接拼 ch\n",
             "expect": "脱敏结果：ab**c**d\n共替换了 4 个数字",
             "hints": ["思路：准备空字符串 res = \"\" 和计数器 cnt = 0，逐字符判断是否在 \"0\" 到 \"9\" 之间。",
                       "步骤：if ch >= \"0\" and ch <= \"9\":（或用两层 if）时 res = res + \"*\" 且 cnt = cnt + 1，else: res = res + ch。",
                       "局部代码：if \"0\" <= ch <= \"9\":\n        res = res + \"*\"\n        cnt = cnt + 1"]},
        ],
    },
    {
        "id": "MK2", "file": "mock02.html", "title": "每日模拟二 · 60 分钟进阶卷", "topic": "限时 60 分钟 · 逻辑运算、while、列表与字符串拆分（零重复）", "drill": True, "timeLimitMin": 60,
        "obj": [
            {"t": "single", "q": "已知 x = 15，表达式 x > 10 and x < 20 与 not (x == 15) 的结果分别是？",
             "opts": ["True 和 True", "True 和 False", "False 和 False", "False 和 True"], "a": 1,
             "why": "15 同时大于 10 且小于 20，所以 and 结果为 True；x == 15 为 True，前面加 not 取反变成 False。"},
            {"t": "single", "q": "运行：\nnums = [2, 4, 6]\nnums.append(8)\nnums[1] = nums[0] + nums[2]\nprint(nums)\n输出什么？",
             "opts": ["[2, 4, 6, 8]", "[8, 4, 6, 8]", "[2, 6, 6, 8]", "[2, 8, 6, 8]"], "a": 3,
             "why": "append(8) 后列表变为 [2, 4, 6, 8]；接着 nums[1] 被改写为 nums[0] + nums[2] = 2 + 6 = 8，得到 [2, 8, 6, 8]。"},
            {"t": "single", "q": "已知列表 a = [10, 20, 30, 40, 50]，运行 print(sum(a[1:4])) 输出什么？",
             "opts": ["90", "100", "60", "150"], "a": 0,
             "why": "a[1:4] 取出下标 1、2、3 的三个元素 [20, 30, 40]，sum 求和得 20 + 30 + 40 = 90。"},
            {"t": "single", "q": "表达式 list(range(10, 0, -3)) 的结果是？",
             "opts": ["[10, 7, 4]", "[10, 7, 4, 1, -2]", "[10, 7, 4, 1]", "[7, 4, 1]"], "a": 2,
             "why": "从 10 开始每次减 3，到大于 0 的 1 为止（不含 0 及负数），依次得到 10、7、4、1。"},
            {"t": "single", "q": "运行：\nn = 1\nstep = 0\nwhile n < 20:\n    n = n * 2\n    step = step + 1\nprint(n, step)\n输出什么？",
             "opts": ["32 5", "16 4", "32 4", "20 5"], "a": 0,
             "why": "n 依次变为 2(1步)、4(2步)、8(3步)、16(4步)、32(5步)，32 不满足 < 20 停止，输出 32 5。"},
            {"t": "single", "q": "运行：\nfor i in range(1, 10):\n    if i % 4 == 0:\n        break\n    print(i, end=\" \")\n输出什么？",
             "opts": ["1 2 3 4", "1 2 3", "4", "1 2 3 5 6 7 9"], "a": 1,
             "why": "i 为 1、2、3 时均打印出来；当 i = 4 时 4 % 4 == 0 触发 break，立刻跳出整个循环，后面不再打印。"},
            {"t": "single", "q": "运行：\ns = 0\nfor i in range(1, 6):\n    if i == 3:\n        continue\n    s = s + i\nprint(s)\n输出什么？",
             "opts": ["15", "3", "6", "12"], "a": 3,
             "why": "continue 只跳过当前这一圈后面的语句（不加 3），循环继续往下走到 4 和 5，总和 1 + 2 + 4 + 5 = 12。"},
            {"t": "single", "q": "line = \"90 85 100\"，运行 parts = line.split(); print(len(parts), parts[1]) 输出什么？",
             "opts": ["9 0", "3 90", "3 85", "报错"], "a": 2,
             "why": "split() 按空格把字符串拆成列表 [\"90\", \"85\", \"100\"]，共 3 项，下标 1 是 \"85\"。"},
            {"t": "single", "q": "已知三位数整数 n = 479，想单独算出它的十位数字 7，正确的整数表达式是？",
             "opts": ["n // 10 % 10", "n % 10", "n // 100", "n % 100"], "a": 0,
             "why": "479 // 10 = 47 去掉个位，再 % 10 取出 47 的末位即原十位数字 7。"},
            {"t": "single", "q": "运行：\ncnt = 0\nfor i in range(1, 5):\n    for j in range(i):\n        cnt = cnt + 1\nprint(cnt)\n输出什么？",
             "opts": ["4", "10", "16", "6"], "a": 1,
             "why": "i 取 1、2、3、4 时，内层 j 分别走 1、2、3、4 圈，总次数 1 + 2 + 3 + 4 = 10。"},
            {"t": "single", "q": "公历年份 y 为闰年的条件是「能被 4 整除且不能被 100 整除，或者能被 400 整除」。下面写法完全正确的是？",
             "opts": ["y % 4 == 0 and y % 400 == 0", "y % 4 == 0 or y % 100 != 0", "(y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)", "y % 400 == 0 and y % 100 != 0"], "a": 2,
             "why": "百年不闰、四百年再闰：例如 1900 满足被 4 整除但被 100 整除所以不是闰年，2000 满足被 400 整除所以是闰年。"},
            {"t": "judge", "q": "写 while 循环时如果忘了更新判断用到的变量，很可能会造成停不下来的死循环。",
             "a": True,
             "why": "条件一直保持为 True 就会无限重复执行，写 while 必须保证每轮变量都在向结束条件逼近。"},
            {"t": "judge", "q": "执行 a = [1, 2, 3]; b = a; b.append(4) 后，列表 a 仍然只有 [1, 2, 3] 三个元素。",
             "a": False,
             "why": "b = a 只是给同一个列表起了第二个名字，没有复制新列表；修改 b 同样会改变 a。"},
            {"t": "judge", "q": "在 Python 3 中，round(2.5) 会遵循「奇进偶舍（银行家舍入）」，返回 2 而不是 3。",
             "a": True,
             "why": "Python 3 的 round 对正好处于中间的 .5 会向最近的偶数舍入：round(2.5)=2，round(3.5)=4。"},
            {"t": "judge", "q": "表达式 \"apple\" in [\"banana\", \"app\"] 的结果是 True。",
             "a": False,
             "why": "对列表用 in 是检查有没有哪个元素完全等于 \"apple\"；列表里只有 \"banana\" 和 \"app\"，结果为 False。"},
        ],
        "tasks": [
            {"id": "TA", "title": "区间闰年筛选", "input": "1996\n2026", "optional": False,
             "desc": "分两行读入起止年份 start（输入 1996 回车）和 end（输入 2026 回车），把 [start, end] 之间所有闰年存进列表 years，最后输出两行：\n1996 2000 2004 2008 2012 2016 2020 2024\n共有 8 个闰年",
             "starter": "start = int(input())\nend = int(input())\nyears = []\n# for y in range(start, end + 1):\n#     判断闰年并 append 进 years\n",
             "expect": "1996 2000 2004 2008 2012 2016 2020 2024\n共有 8 个闰年",
             "hints": ["思路：闰年条件为 (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)，成立就 append(str(y))。",
                       "步骤：第一行用 \" \".join(years) 输出，第二行输出 \"共有\" + len(years) + \"个闰年\"。",
                       "局部代码：print(\" \".join(years))\nprint(\"共有\", len(years), \"个闰年\")"]},
            {"id": "TB", "title": "角谷猜想模拟", "input": "7", "optional": False,
             "desc": "读入正整数 n（输入 7 回车）。按角谷猜想规则重复变换直到 n 变成 1：若当前 n 为偶数则变为 n // 2，若为奇数则变为 3 * n + 1。统计一共变换了多少步，以及过程中出现过的最大数值（含初始值），输出两行：\n总步数是 16\n过程最大值是 52",
             "starter": "n = int(input())\nsteps = 0\nbest = n\n# while n != 1:\n#     按奇偶更新 n，steps 加 1，若 n > best 更新 best\n",
             "expect": "总步数是 16\n过程最大值是 52",
             "hints": ["思路：用 while n != 1: 循环，每轮用 if n % 2 == 0: ... else: ... 算新的 n。",
                       "步骤：每次算完新的 n 后，立刻让 steps 加 1，并用 if n > best: best = n 更新最大值。",
                       "局部代码：if n % 2 == 0:\n        n = n // 2\n    else:\n        n = 3 * n + 1"]},
            {"id": "TC", "title": "多行/空格成绩统计", "input": "80 95 70 85 90", "optional": False,
             "desc": "读入一行用空格隔开的整数成绩（输入 80 95 70 85 90 回车），拆分成整数列表后算出最高分、最低分和平均分，再数一数有多少人的成绩严格大于平均分，输出两行：\n最高分 95 最低分 70\n高于平均分有 3 人",
             "starter": "parts = input().split()\nscores = []\n# 把 parts 里的字符串逐个 int() 放进 scores，再算 max/min/avg 并统计大于平均分人数\n",
             "expect": "最高分 95 最低分 70\n高于平均分有 3 人",
             "hints": ["思路：先用 for p in parts: scores.append(int(p)) 转成整数列表，再用 sum(scores) / len(scores) 求平均分。",
                       "步骤：再写一个循环统计有多少个 x > avg。",
                       "局部代码：print(\"最高分\", max(scores), \"最低分\", min(scores))"]},
            {"id": "TD", "title": "忽略大小写判断回文串", "input": "Level", "optional": False,
             "desc": "读入一个单词字符串 s（输入 Level 回车）。先用 s.lower() 转成全小写，再用循环从后往前反着拼出 rev（或者用切片 s[::-1]），判断原小写串与反转串是否相等，输出两行：\n小写形式：level\n是回文串：True",
             "starter": "s = input().lower()\n# 构造反转串 rev，再判断 s == rev\n",
             "expect": "小写形式：level\n是回文串：True",
             "hints": ["思路：如果不用切片，可以写 rev = \"\"，用 for ch in s: rev = ch + rev（把每个字符插到最前面）完成反转。",
                       "步骤：比较 s == rev 得到布尔值，再按格式输出两行。",
                       "局部代码：print(\"小写形式：\" + s)\nprint(\"是回文串：\" + str(s == rev))"]},
        ],
    },
    {
        "id": "EXT1", "file": "ext01.html", "title": "拓展拔高 · 算法思维特训卷", "topic": "限时 60 分钟 · 嵌套循环、枚举、递推、数位拆分与排序去重", "drill": True, "timeLimitMin": 60,
        "obj": [
            {"t": "single", "q": "如果把处理 n 个数据的两层嵌套循环（每层都跑 n 次）优化成只用一层循环（跑 n 次），当 n = 1000 时，内层操作大约从多少次降到 1000 次？",
             "opts": ["2000 次", "10000 次", "1000000 次", "100000 次"], "a": 2,
             "why": "两层各跑 1000 圈的总次数是 1000 × 1000 = 1000000（一百万次），优化成单层后只需 1000 次，相差一千倍。"},
            {"t": "single", "q": "鸡兔同笼共 35 个头，用 for chicken in range(36): 枚举鸡的数量时，兔的数量直接写成 35 - chicken。这种做法需要几层循环？",
             "opts": ["1 层循环（36 次）", "2 层循环（1296 次）", "3 层循环", "不能用循环求解"], "a": 0,
             "why": "利用「总数已知」消去第二个未知数，把二维枚举降成一维枚举，1 层循环 36 次就能做完。"},
            {"t": "single", "q": "运行：\na, b = 1, 1\nfor i in range(4):\n    a, b = b, a + b\nprint(b)\n输出什么？",
             "opts": ["3", "5", "13", "8"], "a": 3,
             "why": "这是斐波那契递推：4 圈之后 (a, b) 依次变成 (1,2) -> (2,3) -> (3,5) -> (5,8)，所以最终 b 为 8。"},
            {"t": "single", "q": "对列表 [5, 2, 8, 1] 从左到右做一轮相邻比较（若左边比右边大就交换），这一轮结束后列表变成？",
             "opts": ["[1, 2, 5, 8]", "[2, 5, 1, 8]", "[2, 1, 5, 8]", "[5, 2, 1, 8]"], "a": 1,
             "why": "5>2 交换得 [2,5,8,1]；5<8 不换；8>1 交换得 [2,5,1,8]。最大值 8 像气泡一样冒到了最右端。"},
            {"t": "single", "q": "判断整数 n（n >= 2）是否为质数，为什么循环除数只需要试到 i * i <= n（即 √n）就够了？",
             "opts": ["因为合数必有一对一大一小因数，较小的那个不会超过 √n", "因为质数不可能有大于 √n 的因数", "因为 Python 无法对大于 √n 的数取余", "因为超过 √n 一定是偶数"], "a": 0,
             "why": "若 n = a × b，如果 a 和 b 都大于 √n，则 a × b > n 矛盾，所以至少有一个因数 <= √n。"},
            {"t": "single", "q": "用辗转相除法 a, b = b, a % b 求 48 和 18 的最大公约数直到 b == 0，依次经过的 (a, b) 是？",
             "opts": ["(48, 18) -> (30, 18) -> (12, 6)", "(48, 18) -> (18, 6) -> (6, 0)", "(48, 18) -> (18, 12) -> (12, 6) -> (6, 0)", "(48, 18) -> (18, 2) -> (2, 0)"], "a": 2,
             "why": "48 % 18 = 12 得 (18, 12)；18 % 12 = 6 得 (12, 6)；12 % 6 = 0 得 (6, 0)，最大公约数是 6。"},
            {"t": "single", "q": "二维列表 mat = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]，运行 print(mat[1][2] + mat[2][0]) 输出什么？",
             "opts": ["11", "13", "10", "14"], "a": 1,
             "why": "mat[1][2] 是第 1 行第 2 列的 6，mat[2][0] 是第 2 行第 0 列的 7，6 + 7 = 13。"},
            {"t": "single", "q": "nums = [2, 2, 3, 2]，运行：\nfor x in nums:\n    if x == 2:\n        nums.remove(x)\n发现删不干净，最根本的原因是？",
             "opts": ["remove 只能删偶数", "for 循环里不能写 if", "nums 必须先排序", "边遍历列表边删除元素会导致后面元素左移、下标跳格漏判"], "a": 3,
             "why": "删掉第 0 个 2 后，原本第 1 个 2 左移到 0 号位，循环下一步直接跳去查 1 号位的 3，从而漏掉了中间的 2。"},
            {"t": "single", "q": "小写字母 'x' 在字母表中往后循环移动 5 位（'z' 的下一位回到 'a'），用 chr((ord('x') - ord('a') + 5) % 26 + ord('a')) 算出的结果是？",
             "opts": ["'c'", "'b'", "'d'", "'}'"], "a": 0,
             "why": "'x' 是第 23 号字母（从 0 数），(23 + 5) % 26 = 2，第 2 号字母是 'c'。"},
            {"t": "single", "q": "运行：\nd = {}\nfor ch in \"ababa\":\n    d[ch] = d.get(ch, 0) + 1\nprint(d[\"a\"])\n输出什么？",
             "opts": ["1", "2", "3", "报错"], "a": 2,
             "why": "字典统计每个字符出现次数，\"ababa\" 里 'a' 出现了 3 次，所以 d[\"a\"] 是 3。"},
            {"t": "single", "q": "在 1024 个已经从小到大排好序的数中用「二分查找」找目标值（每次对比中间数排除一半），最多只需要查几次？",
             "opts": ["约 512 次", "约 10 次（2 的 10 次方等于 1024）", "约 100 次", "必须 1024 次"], "a": 1,
             "why": "每查 1 次数据规模减半：1024 -> 512 -> 256 -> ... -> 1，最多约 10~11 次就能锁定目标。"},
            {"t": "judge", "q": "在 Python 中，写法 a, b = b, a 可以不用第三个临时变量直接交换 a 和 b 的值。",
             "a": True,
             "why": "Python 会先把右边的 (b, a) 打包算好，再同时拆包赋给左边的 a 和 b，不会互相覆盖。"},
            {"t": "judge", "q": "for 循环一定比 while 循环快，所以能用 for 的地方绝对不能用 while。",
             "a": False,
             "why": "两者只是控制循环的写法不同：固定次数常用 for，按条件停下常用 while，没有谁绝对更快。"},
            {"t": "judge", "q": "用列表 cnt = [0] * 10 配合 cnt[d] += 1 可以一次统计 0–9 十个数字各自的频次，比写十个变量更简洁。",
             "a": True,
             "why": "这就是桶计数（频次表）思想，用数字本身作下标直接定位计数器。"},
            {"t": "judge", "q": "解决「百钱买百鸡」时，如果公鸡、母鸡、小鸡各套一层 0 到 100 的循环，即使不优化也只需要执行 100 次。",
             "a": False,
             "why": "三层 0..100 嵌套总次数是 101 × 101 × 101 ≈ 103 万次；通过数量关系剪枝或消元能大幅减少次数。"},
        ],
        "tasks": [
            {"id": "TA", "title": "下三角九九乘法表", "input": "4", "optional": False,
             "desc": "读入一个整数 n（1 <= n <= 9，运行时输入 4 回车），用嵌套 for 循环输出九九乘法表的前 n 行（第 i 行有 i 个式子，式子之间用一个空格分隔），输入 4 应输出：\n1x1=1\n2x1=2 2x2=4\n3x1=3 3x2=6 3x3=9\n4x1=4 4x2=8 4x3=12 4x4=16",
             "starter": "n = int(input())\n# 外层 i 从 1 到 n，内层 j 从 1 到 i，用列表或字符串拼好一行再打印\n",
             "expect": "1x1=1\n2x1=2 2x2=4\n3x1=3 3x2=6 3x3=9\n4x1=4 4x2=8 4x3=12 4x4=16",
             "hints": ["思路：外层循环管行号 i（1 到 n），内层循环管列号 j（1 到 i），每行攒成列表 parts 再 \" \".join(parts) 打印就不会多尾部空格。",
                       "步骤：内层里把 f\"{i}x{j}={i * j}\" 放进 parts，内层结束后顶格一级写 print(\" \".join(parts))。",
                       "局部代码：parts.append(str(i) + \"x\" + str(j) + \"=\" + str(i * j))"]},
            {"id": "TB", "title": "水仙花数筛选", "input": "100\n500", "optional": False,
             "desc": "如果一个三位数等于它各位数字的立方和（例如 153 = 1^3 + 5^3 + 3^3），就称它为「水仙花数」。\n分两行读入起止范围 a（100）和 b（500），依次逐行输出区间内所有水仙花数，最后一行输出总个数：\n153\n370\n371\n407\n共找到 4 个",
             "starter": "a = int(input())\nb = int(input())\ncnt = 0\n# for n in range(a, b + 1):\n#     用 // 和 % 拆出百位、十位、个位，判断立方和是否等于 n\n",
             "expect": "153\n370\n371\n407\n共找到 4 个",
             "hints": ["思路：百位 h = n // 100，十位 t = n // 10 % 10，个位 u = n % 10。",
                       "步骤：判断 h ** 3 + t ** 3 + u ** 3 == n，成立就 print(n) 且 cnt 加 1。",
                       "局部代码：if h ** 3 + t ** 3 + u ** 3 == n:\n        print(n)\n        cnt = cnt + 1"]},
            {"id": "TC", "title": "斐波那契数列与求和", "input": "10", "optional": False,
             "desc": "斐波那契数列前两项为 1、1，从第 3 项起每项等于前两项之和。读入整数 n（n >= 2，输入 10 回车），生成前 n 项存入列表并输出两行：\n1 1 2 3 5 8 13 21 34 55\n前 10 项之和是 143",
             "starter": "n = int(input())\nfib = [1, 1]\n# 用循环补齐到第 n 项，再输出空格拼接行与总和\n",
             "expect": "1 1 2 3 5 8 13 21 34 55\n前 10 项之和是 143",
             "hints": ["思路：如果 n > 2，用 for i in range(2, n): 每次把 fib[-1] + fib[-2] append 进 fib。",
                       "步骤：打印第一行时可把每个整数转 str 后用 \" \".join(...)，第二行用 sum(fib) 求总和。",
                       "局部代码：fib.append(fib[-1] + fib[-2])"]},
            {"id": "TD", "title": "保序去重与第二大值", "input": "12 45 23 45 67 12 89 67", "optional": False,
             "desc": "读入一行空格分隔的多个整数（输入 12 45 23 45 67 12 89 67 回车，至少含 2 个不同整数）。按首次出现的顺序去掉重复数字并存入新列表 uniq，再找出其中第二大的数，输出两行：\n去重结果：12 45 23 67 89\n第二大的数是 67",
             "starter": "parts = input().split()\nuniq = []\n# 1. 转整数后若不在 uniq 中就 append，保持原顺序去重\n# 2. 对拷贝列表 sorted(uniq) 取倒数第二项 [-2] 得到第二大值\n",
             "expect": "去重结果：12 45 23 67 89\n第二大的数是 67",
             "hints": ["思路：不能用 set()（set 会打乱顺序）；遍历时写 x = int(p)，if x not in uniq: uniq.append(x) 就能完美保序去重。",
                       "步骤：注意千万别在 uniq 上直接 sort()（会破坏原有顺序输出），用 sorted(uniq)[-2] 拿第二大的数。",
                       "局部代码：if x not in uniq:\n        uniq.append(x)"]},
        ],
    },
]


# ---------------------------------------------------------------------------
# 参考解法（教师参考；键 = 关卡id_任务id）
# ---------------------------------------------------------------------------

REF = {
    "L01_T1": "print(\"你好，我是闯关新手\")\nprint(\"这是我的第一个程序\")\nprint(\"闯关开始\")\n",
    "L02_T1": "name = \"Python\"\nhobby = \"闯关\"\nprint(\"我在学\", name)\nprint(\"我的爱好是\", hobby)\n",
    "L03_T1": "pixels = 17\nper = 5\nprint(\"能摆满\", pixels // per, \"行\")\nprint(\"还剩\", pixels % per, \"个\")\n",
    "L04_T1": "a = int(input())\nb = int(input())\nprint(\"两个数的和是\", a + b)\nprint(\"两个数的差是\", a - b)\n",
    "L05_T1": ("score = 78\n"
               "if score >= 90:\n"
               "    level = \"优秀\"\n"
               "elif score >= 80:\n"
               "    level = \"良好\"\n"
               "elif score >= 60:\n"
               "    level = \"及格\"\n"
               "else:\n"
               "    level = \"不及格\"\n"
               "print(\"78 分的等级是：\" + level)\n"),
    "L06_T1": "total = 0\nfor i in range(1, 101):\n    total = total + i\nprint(\"1 到 100 的总和是\", total)\n",
    "L06_T2": "for i in range(1, 4):\n    print(\"3x\" + str(i) + \"=\" + str(3 * i), end=\" \")\nprint()\n",
    "L07_T1": "s = \"1011010\"\nprint(\"长度是\", len(s))\nprint(\"第 3 个字符是\", s[2])\nprint(\"最后一个字符是\", s[6])\n",
    "L08_T1": ("n = int(input())\n"
               "result = 1\n"
               "for i in range(1, n + 1):\n"
               "    result = result * i\n"
               "print(n, \"的阶乘是\", result)\n"),
    "FIN_TA": "a = int(input())\nb = int(input())\nprint(a, \"//\", b, \"=\", a // b)\nprint(a, \"%\", b, \"=\", a % b)\n",
    "FIN_TB": "for i in range(1, 21):\n    if i % 3 == 0:\n        print(i)\n",
    "DRA_TA": "name = \"小明\"\nscore = 96\nprint(\"姓名：\" + name)\nprint(\"得分：\" + str(score))\n",
    "DRA_TB": "a = int(input())\nb = int(input())\nif a > b:\n    print(\"较大的数是\", a)\nelse:\n    print(\"较大的数是\", b)\n",
    "DRA_TC": "n = int(input())\nprint(n, \"秒 =\", n // 60, \"分\", n % 60, \"秒\")\n",
    "DRB_TA": ("n = int(input())\n"
               "total = 0\n"
               "for i in range(1, n + 1):\n"
               "    if i % 2 == 0:\n"
               "        total = total + i\n"
               "print(n, \"以内偶数的和是\", total)\n"),
    "DRB_TB": ("s = input()\n"
               "count = 0\n"
               "for i in range(len(s)):\n"
               "    if s[i] == \"1\":\n"
               "        count = count + 1\n"
               "print(\"1 的个数是\", count)\n"),
    "DRB_TC": ("n = int(input())\n"
               "for i in range(1, n + 1):\n"
               "    print(str(n) + \"x\" + str(i) + \"=\" + str(n * i), end=\" \")\n"
               "print()\n"),
    "MK1_TA": ("h = int(input())\n"
               "m = int(input())\n"
               "add = int(input())\n"
               "total = h * 60 + m + add\n"
               "new_h = total // 60\n"
               "new_m = total % 60\n"
               "print(\"到达时间\", str(new_h) + \":\" + str(new_m))\n"),
    "MK1_TB": ("kwh = int(input())\n"
               "if kwh <= 100:\n"
               "    fee = kwh * 0.5\n"
               "else:\n"
               "    fee = 100 * 0.5 + (kwh - 100) * 0.8\n"
               "print(\"总电费\", fee, \"元\")\n"),
    "MK1_TC": ("s = input()\n"
               "total = 0\n"
               "nonzero = 0\n"
               "for i in range(len(s)):\n"
               "    d = int(s[i])\n"
               "    total = total + d\n"
               "    if d != 0:\n"
               "        nonzero = nonzero + 1\n"
               "print(\"各位数字之和是\", total)\n"
               "print(\"非零数字有\", nonzero, \"个\")\n"),
    "MK1_TD": ("s = input()\n"
               "res = \"\"\n"
               "cnt = 0\n"
               "for i in range(len(s)):\n"
               "    ch = s[i]\n"
               "    if \"0\" <= ch <= \"9\":\n"
               "        res = res + \"*\"\n"
               "        cnt = cnt + 1\n"
               "    else:\n"
               "        res = res + ch\n"
               "print(\"脱敏结果：\" + res)\n"
               "print(\"共替换了\", cnt, \"个数字\")\n"),
    "MK2_TA": ("start = int(input())\n"
               "end = int(input())\n"
               "years = []\n"
               "for y in range(start, end + 1):\n"
               "    if (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0):\n"
               "        years.append(str(y))\n"
               "print(\" \".join(years))\n"
               "print(\"共有\", len(years), \"个闰年\")\n"),
    "MK2_TB": ("n = int(input())\n"
               "steps = 0\n"
               "best = n\n"
               "while n != 1:\n"
               "    if n % 2 == 0:\n"
               "        n = n // 2\n"
               "    else:\n"
               "        n = 3 * n + 1\n"
               "    steps = steps + 1\n"
               "    if n > best:\n"
               "        best = n\n"
               "print(\"总步数是\", steps)\n"
               "print(\"过程最大值是\", best)\n"),
    "MK2_TC": ("parts = input().split()\n"
               "scores = []\n"
               "for p in parts:\n"
               "    scores.append(int(p))\n"
               "avg = sum(scores) / len(scores)\n"
               "above = 0\n"
               "for x in scores:\n"
               "    if x > avg:\n"
               "        above = above + 1\n"
               "print(\"最高分\", max(scores), \"最低分\", min(scores))\n"
               "print(\"高于平均分有\", above, \"人\")\n"),
    "MK2_TD": ("s = input().lower()\n"
               "rev = \"\"\n"
               "for ch in s:\n"
               "    rev = ch + rev\n"
               "print(\"小写形式：\" + s)\n"
               "print(\"是回文串：\" + str(s == rev))\n"),
    "EXT1_TA": ("n = int(input())\n"
                "for i in range(1, n + 1):\n"
                "    parts = []\n"
                "    for j in range(1, i + 1):\n"
                "        parts.append(str(i) + \"x\" + str(j) + \"=\" + str(i * j))\n"
                "    print(\" \".join(parts))\n"),
    "EXT1_TB": ("a = int(input())\n"
                "b = int(input())\n"
                "cnt = 0\n"
                "for n in range(a, b + 1):\n"
                "    h = n // 100\n"
                "    t = n // 10 % 10\n"
                "    u = n % 10\n"
                "    if h ** 3 + t ** 3 + u ** 3 == n:\n"
                "        print(n)\n"
                "        cnt = cnt + 1\n"
                "print(\"共找到\", cnt, \"个\")\n"),
    "EXT1_TC": ("n = int(input())\n"
                "fib = [1, 1]\n"
                "for i in range(2, n):\n"
                "    fib.append(fib[-1] + fib[-2])\n"
                "out = []\n"
                "for x in fib:\n"
                "    out.append(str(x))\n"
                "print(\" \".join(out))\n"
                "print(\"前\", n, \"项之和是\", sum(fib))\n"),
    "EXT1_TD": ("parts = input().split()\n"
                "uniq = []\n"
                "for p in parts:\n"
                "    x = int(p)\n"
                "    if x not in uniq:\n"
                "        uniq.append(x)\n"
                "out = []\n"
                "for x in uniq:\n"
                "    out.append(str(x))\n"
                "print(\"去重结果：\" + \" \".join(out))\n"
                "print(\"第二大的数是\", sorted(uniq)[-2])\n"),
}


# ---------------------------------------------------------------------------
# --verify：实跑参考解法，比对预期输出
# ---------------------------------------------------------------------------

def run_verify():
    verify_tmp = tempfile.mkdtemp(prefix="ck_verify_")
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    total = 0
    failed = []
    try:
        for level in LEVELS + [FIN] + DRILLS:
            for task in level["tasks"]:
                total += 1
                tid = level["id"] + "_" + task["id"]
                path = os.path.join(verify_tmp, tid + ".py")
                with io.open(path, "w", encoding="utf-8", newline="\n") as f:
                    f.write(REF[tid])
                stdin_text = "" if task["input"] == "无" else task["input"]
                try:
                    proc = subprocess.run(
                        [sys.executable, path],
                        input=stdin_text, capture_output=True, text=True,
                        encoding="utf-8", timeout=30, env=env)
                except subprocess.TimeoutExpired:
                    failed.append((tid, "超时（30 秒未结束）"))
                    continue
                if proc.returncode != 0:
                    failed.append((tid, "非零退出：" + proc.stderr.strip()[:200]))
                    continue
                if proc.stderr.strip():
                    failed.append((tid, "stderr 非空：" + proc.stderr.strip()[:200]))
                    continue
                got = normalize_output(proc.stdout)
                want = normalize_output(task["expect"])
                if got != want:
                    failed.append((tid, "输出不一致\n  期望: %r\n  实际: %r" % (want, got)))
    finally:
        shutil.rmtree(verify_tmp, ignore_errors=True)
    for tid, msg in failed:
        print("FAIL " + tid + " " + msg)
    print("verify: %d/%d 通过" % (total - len(failed), total))
    return 0 if not failed else 1


# ---------------------------------------------------------------------------
# 关卡页引擎（Task 3）：单文件 HTML，CSS/JS 全内嵌，ES2017 以内，零外部请求
# ---------------------------------------------------------------------------

PAGE_CSS = r'''
  :root { --blue:#0b5fff; --blue2:#2fa4ff; --ink:#1c2b3a; --muted:#6f8096;
          --line:#e3ebf5; --bg:#eef3fa; --green:#18a058; --orange:#ff9800; --purple:#7c5cff; }
  * { box-sizing: border-box; }
  body { margin:0; font-family:"Microsoft YaHei","PingFang SC",system-ui,sans-serif;
         background:var(--bg); color:var(--ink); line-height:1.6; font-size:16px; }
  .wrap { max-width:900px; margin:0 auto; padding:0 20px 40px; }
  header.top { background:linear-gradient(135deg,#0b5fff 0%,#2fa4ff 100%); color:#fff; padding:26px 0 22px; }
  .crumb a { color:rgba(255,255,255,.85); font-size:13px; text-decoration:none; }
  .badge { display:inline-block; background:rgba(255,255,255,.22); border-radius:999px;
           padding:2px 12px; font-size:13px; margin:10px 0 6px; }
  h1 { font-size:28px; margin:0 0 4px; }
  .topic { font-size:15px; color:rgba(255,255,255,.9); margin:0; }
  .card { background:#fff; border:1px solid var(--line); border-radius:14px;
          padding:18px 20px; margin-top:18px; box-shadow:0 8px 22px rgba(30,70,140,.06); }
  .card h2 { font-size:19px; margin:0 0 4px; color:#14417e; }
  .hintline { font-size:13px; color:var(--muted); margin:0 0 12px; }
  .q { border:1px solid var(--line); border-radius:10px; padding:12px 14px; margin:10px 0; }
  .q .qt { white-space:pre-wrap; font-size:15px; margin:0 0 8px; }
  .q label { display:block; padding:5px 10px; border-radius:8px; cursor:pointer; font-size:15px; }
  .q label:hover { background:#f2f7ff; }
  .q.correct { border-color:var(--green); background:#f2fbf6; }
  .q.wrong { border-color:#e5484d; background:#fdf3f3; }
  .why { display:none; font-size:13.5px; color:#8a5a00; background:#fff8ec;
         border:1px solid #ffe0b0; border-radius:8px; padding:8px 12px; margin-top:8px; }
  .why.show { display:block; }
  .task-head { display:flex; align-items:center; margin:0 0 6px; }
  .task-head > * + * { margin-left:10px; }
  .task-head h3 { font-size:17px; margin:0; color:#14417e; }
  .opt-tag { font-size:12px; color:var(--muted); background:#f5f8fc; border:1px solid var(--line);
             border-radius:999px; padding:1px 9px; }
  .desc { white-space:pre-wrap; font-size:15px; background:#f7fafd; border:1px solid var(--line);
          border-radius:10px; padding:10px 14px; margin:8px 0; }
  pre.starter { background:#f2f6fb; border:1px solid var(--line); border-radius:10px;
                padding:10px 14px; font:14px/1.5 Consolas,monospace; white-space:pre-wrap; margin:8px 0; }
  textarea { width:100%; min-height:110px; font:14px/1.55 Consolas,monospace; color:var(--ink);
             border:1px solid #c9d8ea; border-radius:10px; padding:10px 12px; resize:vertical; }
  textarea:focus { outline:2px solid #b9d4ff; }
  .row { display:flex; flex-wrap:wrap; margin:10px 0 4px; }
  .row > * + * { margin-left:8px; margin-top:4px; }
  .btn { display:inline-block; border:1px solid var(--blue); background:var(--blue); color:#fff;
         font-size:14px; padding:7px 16px; border-radius:9px; cursor:pointer; text-decoration:none; }
  .btn:hover { background:#074fd6; }
  .btn.ghost { background:#fff; color:var(--blue); }
  .btn.ghost:hover { background:#eef5ff; }
  .btn.gray { background:#fff; color:#3b4a5f; border-color:#c9d8ea; }
  .btn.gray:hover { background:#f2f7ff; }
  .btn:disabled { opacity:.45; cursor:not-allowed; }
  .hintbox { background:#fff8ec; border:1px solid #ffe0b0; color:#8a5a00; border-radius:10px;
             padding:8px 14px; font-size:14px; margin-top:8px; white-space:pre-wrap; }
  .msg { font-size:14px; border-radius:10px; padding:8px 14px; margin-top:8px; display:none; white-space:pre-wrap; }
  .msg.show { display:block; }
  .msg.ok { background:#f2fbf6; border:1px solid #bfe6cf; color:#116a3c; }
  .msg.bad { background:#fdf3f3; border:1px solid #f3c2c4; color:#a32629; }
  .msg.info { background:#f2f7ff; border:1px solid #c9d8ea; color:#14417e; }
  .gate { text-align:center; padding:8px 0 0; }
  .stamp { display:none; font-size:22px; color:var(--green); font-weight:700; margin:6px 0; }
  .stamp.show { display:block; }
  .timer { font:700 26px/1 Consolas,monospace; letter-spacing:2px; color:#fff;
           background:rgba(255,255,255,.22); border-radius:10px; padding:8px 18px; display:inline-block; }
  .banner { display:none; background:#fff8ec; border:1px solid #ffe0b0; color:#8a5a00;
            border-radius:10px; padding:10px 16px; font-size:14px; margin:14px 0 0; }
  .banner.show { display:block; }
  footer.foot { border-top:1px solid var(--line); background:#fff; color:var(--muted);
                font-size:13px; padding:14px 0; margin-top:28px; text-align:center; }
'''

PAGE_JS = r'''
(function () {
  'use strict';
  var LV = PAGE_DATA;
  var KEY = 'ck_progress_v1';
  var storeOK = true;
  var DEF = { v: 1, unlocked: 1, stamps: {}, obj: {}, hints: {}, tasks: {}, final: { started: false, left: 2400 } };

  function $(id) { return document.getElementById(id); }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  function loadProg() {
    var p;
    try {
      var raw = localStorage.getItem(KEY);
      if (raw) p = JSON.parse(raw);
    } catch (e) { storeOK = false; p = null; }
    if (!p || typeof p !== 'object') p = {};
    for (var k in DEF) { if (!(k in p)) p[k] = DEF[k]; }
    if (!p.stamps) p.stamps = {};
    if (!p.obj) p.obj = {};
    if (!p.hints) p.hints = {};
    if (!p.tasks) p.tasks = {};
    if (!p.final) p.final = { started: false, left: 2400 };
    return p;
  }
  function saveProg() {
    try { localStorage.setItem(KEY, JSON.stringify(prog)); }
    catch (e) { if (storeOK) { storeOK = false; showBanner(); } }
  }
  function showBanner() {
    var b = $('storeBanner');
    if (b) b.className = 'banner show';
  }

  /* -- 与教师脚本 --verify 同一套归一化规则 -- */
  function normalize(s) {
    var lines = s.replace(/\r\n/g, '\n').replace(/\r/g, '\n').split('\n');
    var i;
    for (i = 0; i < lines.length; i++) {
      lines[i] = lines[i].replace(/^[\s　]+/, '').replace(/[\s　]+$/, '');
    }
    while (lines.length && lines[lines.length - 1] === '') lines.pop();
    return lines.join('\n');
  }

  function draftKey(taskId) { return 'ck_draft_' + LV.id + '_' + taskId + '_v1'; }
  function getDraft(taskId) {
    try { return localStorage.getItem(draftKey(taskId)); } catch (e) { return null; }
  }
  function setDraft(taskId, text) {
    try { localStorage.setItem(draftKey(taskId), text); } catch (e) {}
  }

  /* -- 客观题 -- */
  function chosenAnswer(qi) {
    var radios = document.getElementsByName('q' + qi);
    for (var i = 0; i < radios.length; i++) { if (radios[i].checked) return radios[i].value; }
    return null;
  }
  function restoreAnswers() {
    var saved = prog.obj[LV.id];
    if (!saved) return;
    for (var qi = 0; qi < LV.obj.length; qi++) {
      var v = saved['q' + qi];
      if (v === undefined) continue;
      var radios = document.getElementsByName('q' + qi);
      for (var i = 0; i < radios.length; i++) {
        var rv = radios[i].value;
        if (rv === 'true') rv = true; else if (rv === 'false') rv = false; else rv = Number(rv);
        if (rv === v) radios[i].checked = true;
      }
    }
  }
  function submitObj() {
    var saved = {};
    var score = 0;
    for (var qi = 0; qi < LV.obj.length; qi++) {
      var v = chosenAnswer(qi);
      var card = $('q' + qi);
      var why = card.querySelector('.why');
      if (why) why.className = 'why show';
      if (v === null) {
        card.className = 'q wrong';
        continue;
      }
      var ans = LV.obj[qi].a;
      var norm = (v === 'true') ? true : (v === 'false') ? false : Number(v);
      var ok = (norm === ans);
      if (ok) score++;
      card.className = 'q ' + (ok ? 'correct' : 'wrong');
      saved['q' + qi] = norm;
    }
    prog.obj[LV.id] = saved;
    saveProg();
    $('objScore').textContent = '得分：' + score + ' / ' + LV.obj.length;
    updateGate();
  }
  function redoObj() {
    for (var qi = 0; qi < LV.obj.length; qi++) {
      $('q' + qi).className = 'q';
      var radios = document.getElementsByName('q' + qi);
      for (var i = 0; i < radios.length; i++) radios[i].checked = false;
      var why = $('q' + qi).querySelector('.why');
      if (why) why.className = 'why';
    }
    delete prog.obj[LV.id];
    saveProg();
    $('objScore').textContent = '';
    updateGate();
  }

  function objPassed() {
    var saved = prog.obj[LV.id];
    if (!saved) return false;
    for (var qi = 0; qi < LV.obj.length; qi++) {
      if (saved['q' + qi] !== LV.obj[qi].a) return false;
    }
    return true;
  }

  /* -- 编程任务 -- */
  function buildTasks() {
    var host = $('tasks');
    for (var ti = 0; ti < LV.tasks.length; ti++) {
      var t = LV.tasks[ti];
      var card = el('div', 'card');
      card.id = 'task' + ti;
      var head = el('div', 'task-head');
      head.appendChild(el('h3', null, '任务 ' + (ti + 1) + '：' + t.title));
      head.appendChild(el('span', 'opt-tag', t.optional ? '选做 · 不影响盖章' : '必做'));
      card.appendChild(head);
      card.appendChild(el('div', 'desc', t.desc));
      if (t.input !== '无') card.appendChild(el('p', 'hintline', '运行时的输入样例（一行一个回车）：' + t.input.replace(/\n/g, ' ↦ ')));
      var pre = el('pre', 'starter');
      pre.textContent = t.starter;
      card.appendChild(pre);
      var row1 = el('div', 'row');
      var copyBtn = el('button', 'btn ghost', '复制起步代码');
      copyBtn.onclick = (function (t2) { return function () { copyStarter(t2); }; })(t);
      row1.appendChild(copyBtn);
      card.appendChild(row1);
      var lbl = el('p', 'hintline', '代码草稿（可在这里先写，复制到 IDLE 运行；自动保存）：');
      card.appendChild(lbl);
      var code = el('textarea');
      code.id = 'code' + ti;
      var d = getDraft(t.id);
      code.value = (d === null || d === '') ? t.starter : d;
      code.oninput = (function (t2) { return function () { setDraft(t2.id, this.value); }; })(t);
      card.appendChild(code);
      var row2 = el('div', 'row');
      var fmtBtn = el('button', 'btn gray', '格式检查（不判分）');
      fmtBtn.onclick = (function (ti2) { return function () { checkFormat(ti2); }; })(ti);
      var expBtn = el('button', 'btn gray', '草稿导出 .py');
      expBtn.onclick = (function (ti2, t2) { return function () { exportPy(ti2, t2); }; })(ti, t);
      var hintBtn = el('button', 'btn ghost', '提示');
      hintBtn.id = 'hintbtn' + ti;
      hintBtn.onclick = (function (ti2) { return function () { revealHint(ti2); }; })(ti);
      row2.appendChild(fmtBtn);
      row2.appendChild(expBtn);
      row2.appendChild(hintBtn);
      card.appendChild(row2);
      var hintHost = el('div');
      hintHost.id = 'hints' + ti;
      card.appendChild(hintHost);
      card.appendChild(el('p', 'hintline', '把 IDLE 里运行后的输出整段粘贴到这里核对：'));
      var out = el('textarea');
      out.id = 'out' + ti;
      out.placeholder = '粘贴运行结果…';
      card.appendChild(out);
      var row3 = el('div', 'row');
      var chkBtn = el('button', 'btn', '核对输出');
      chkBtn.onclick = (function (ti2) { return function () { verifyOutput(ti2); }; })(ti);
      row3.appendChild(chkBtn);
      card.appendChild(row3);
      var msg = el('div', 'msg');
      msg.id = 'msg' + ti;
      card.appendChild(msg);
      host.appendChild(card);
      refreshHints(ti);
    }
  }

  function copyStarter(t) {
    copyText(t.starter, '起步代码已复制，去 IDLE 里粘贴');
  }
  function copyText(text, tip) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    var ok = false;
    try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
    document.body.removeChild(ta);
    toast(ok ? tip : '复制失败，请手动选择复制');
  }
  function toast(text) {
    var m = el('div', 'msg info show');
    m.textContent = text;
    m.style.position = 'fixed';
    m.style.left = '50%';
    m.style.transform = 'translateX(-50%)';
    m.style.bottom = '26px';
    m.style.zIndex = '99';
    m.style.boxShadow = '0 8px 22px rgba(30,70,140,.25)';
    document.body.appendChild(m);
    setTimeout(function () { document.body.removeChild(m); }, 1800);
  }

  function revealHint(ti) {
    var t = LV.tasks[ti];
    var used = prog.hints[LV.id] && prog.hints[LV.id][t.id] ? prog.hints[LV.id][t.id] : 0;
    if (used >= t.hints.length) return;
    used++;
    if (!prog.hints[LV.id]) prog.hints[LV.id] = {};
    prog.hints[LV.id][t.id] = used;
    saveProg();
    refreshHints(ti);
  }
  function refreshHints(ti) {
    var t = LV.tasks[ti];
    var used = prog.hints[LV.id] && prog.hints[LV.id][t.id] ? prog.hints[LV.id][t.id] : 0;
    var btn = $('hintbtn' + ti);
    if (btn) btn.textContent = '提示（已用 ' + used + '/3）';
    var host = $('hints' + ti);
    if (!host) return;
    host.innerHTML = '';
    for (var i = 0; i < used && i < t.hints.length; i++) {
      var box = el('div', 'hintbox', '提示 ' + (i + 1) + '/3：' + t.hints[i]);
      host.appendChild(box);
    }
  }

  function checkFormat(ti) {
    var code = $('code' + ti).value;
    var msg = $('msg' + ti);
    var issues = [];
    if (code.trim() === '') {
      msg.className = 'msg info show';
      msg.textContent = '代码草稿是空的--先在「代码草稿」里写下或粘贴你的代码。';
      return;
    }
    if (/[“”‘’]/.test(code)) issues.push('发现中文引号 “ ” ‘ ’：Python 只认英文引号 " 和 \'');
    if (/&&|\|\|/.test(code)) issues.push('发现 && 或 ||：Python 里表示「并且/或者」用 and、or');
    var lines = code.replace(/\r\n/g, '\n').split('\n');
    var tabIndent = false, spaceIndent = false;
    for (var i = 0; i < lines.length; i++) {
      var raw = lines[i];
      if (/^\t+/.test(raw)) tabIndent = true;
      if (/^ {2,}/.test(raw)) spaceIndent = true;
      var hashIdx = raw.indexOf('#');
      var codePart = hashIdx === -1 ? raw : raw.slice(0, hashIdx);
      var hasQuote = codePart.indexOf('"') !== -1 || codePart.indexOf("'") !== -1;
      var t = codePart.replace(/[\s　]+$/, '');
      if (!hasQuote && /^(if|elif|else|for|while)\b/.test(t) && t.charAt(t.length - 1) !== ':') {
        issues.push('第 ' + (i + 1) + ' 行以 ' + t.split(' ')[0] + ' 开头，行尾缺英文冒号 :');
      }
    }
    if (tabIndent && spaceIndent) issues.push('缩进混用了 Tab 和空格：统一只用 4 个空格');
    var open = (code.match(/\(/g) || []).length;
    var close = (code.match(/\)/g) || []).length;
    if (open !== close) issues.push('圆括号不成对：( 有 ' + open + ' 个，) 有 ' + close + ' 个');
    msg.className = issues.length ? 'msg bad show' : 'msg info show';
    msg.textContent = issues.length
      ? '格式检查只提示、不判分。发现：\n· ' + issues.join('\n· ')
      : '格式检查只提示、不判分。没发现常见格式问题，可以拿去 IDLE 运行了。';
  }

  function exportPy(ti, t) {
    var code = $('code' + ti).value;
    if (code.trim() === '') { toast('草稿是空的，先写点代码再导出'); return; }
    var blob = new Blob([code], { type: 'text/plain;charset=utf-8' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = LV.id + '_' + t.id + '.py';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    toast('已导出 ' + LV.id + '_' + t.id + '.py');
  }

  function verifyOutput(ti) {
    var t = LV.tasks[ti];
    var pasted = $('out' + ti).value;
    var msg = $('msg' + ti);
    if (pasted.trim() === '') {
      msg.className = 'msg info show';
      msg.textContent = '先把 IDLE 里运行的输出整段粘贴到上面的框里，再点「核对输出」。';
      return;
    }
    if (pasted.indexOf('Traceback') !== -1) {
      msg.className = 'msg bad show';
      msg.textContent = '你粘贴的是报错信息（Traceback），不是运行结果。\n回 IDLE 看红字最后一行：那是错误类型和行号；改正后再运行、再粘贴。拿不准就点「提示」。';
      return;
    }
    if (normalize(pasted) === normalize(t.expect)) {
      if (!prog.tasks[LV.id]) prog.tasks[LV.id] = {};
      prog.tasks[LV.id][t.id] = true;
      saveProg();
      msg.className = 'msg ok show';
      msg.textContent = '输出一致，这个任务通过了！';
      updateGate();
    } else {
      msg.className = 'msg bad show';
      msg.textContent = '还不一致。检查：文字是不是一模一样？行数对不对？标点是英文的吗？需要的话点「提示」。';
    }
  }

  function tasksPassed() {
    for (var ti = 0; ti < LV.tasks.length; ti++) {
      var t = LV.tasks[ti];
      if (t.optional) continue;
      var st = prog.tasks[LV.id];
      if (!st || !st[t.id]) return false;
    }
    return true;
  }

  /* -- 通关 -- */
  function nextHref() {
    if (LV.drill) return '../index.html';
    var i = LV.index;
    if (LV.id === 'FIN') return '../index.html';
    if (i + 1 < 8) return 'level0' + (i + 2) + '.html';
    return 'final.html';
  }
  function updateGate() {
    var gate = $('gate');
    var stamped = !!prog.stamps[LV.id];
    var done = stamped || (objPassed() && tasksPassed());
    if (done && !stamped) {
      prog.stamps[LV.id] = true;
      var nextIdx = LV.id === 'FIN' ? 9 : (LV.drill ? prog.unlocked : LV.index + 2);
      if (nextIdx > prog.unlocked) prog.unlocked = nextIdx;
      saveProg();
    }
    var stamp = $('stamp');
    var next = $('next');
    if (done) {
      stamp.className = 'stamp show';
      next.style.display = 'inline-block';
      gate.style.display = 'block';
      if (LV.id === 'FIN' || LV.drill) {
        next.textContent = '返回地图';
      } else {
        next.textContent = stamped ? '继续 · 下一关' : '通关！进入下一关';
      }
      next.href = nextHref();
    } else {
      stamp.className = 'stamp';
      next.style.display = 'none';
    }
  }

  /* -- 模拟关计时 -- */
  var timerId = null;
  function pad2(n) { return (n < 10 ? '0' : '') + n; }
  function renderTimer(left) {
    var m = Math.floor(left / 60);
    var s = left % 60;
    $('timer').textContent = pad2(m) + ':' + pad2(s);
  }
  function lockAll() {
    var list = document.querySelectorAll('textarea, button, input');
    for (var i = 0; i < list.length; i++) {
      var e = list[i];
      if (e.id === 'revealBtn' || e.id === 'newRoundBtn') continue;
      e.disabled = true;
    }
    $('timeup').style.display = 'block';
    $('revealBtn').style.display = 'inline-block';
    $('newRoundBtn').style.display = 'inline-block';
  }
  function timerState() {
    if (LV.id === 'FIN') return prog.final;
    if (!prog.timers[LV.id]) prog.timers[LV.id] = { started: false, left: LV.timeLimitMin * 60 };
    return prog.timers[LV.id];
  }
  function newRound() {
    var ts = timerState();
    ts.started = false;
    ts.left = LV.timeLimitMin * 60;
    saveProg();
    window.location.reload();
  }
  function revealWhy() {
    var whys = document.querySelectorAll('.why');
    for (var i = 0; i < whys.length; i++) whys[i].className = 'why show';
  }
  function startTimer() {
    var ts = timerState();
    if (ts.started && ts.left <= 0) {
      renderTimer(0);
      lockAll();
      return;
    }
    if (!ts.started) {
      ts.started = true;
      ts.left = LV.timeLimitMin * 60;
      saveProg();
    }
    renderTimer(ts.left);
    timerId = setInterval(function () {
      ts.left--;
      if (ts.left <= 0) {
        ts.left = 0;
        renderTimer(0);
        saveProg();
        clearInterval(timerId);
        lockAll();
        return;
      }
      renderTimer(ts.left);
      saveProg();
    }, 1000);
  }

  /* -- 启动 -- */
  var prog = loadProg();
  function init() {
    if (!storeOK) showBanner();
    if (LV.timeLimitMin) {
      $('timerBox').style.display = 'inline-block';
      startTimer();
    }
    buildTasks();
    restoreAnswers();
    var saved = prog.obj[LV.id];
    if (saved) {
      var score = 0;
      for (var qi = 0; qi < LV.obj.length; qi++) {
        if (saved['q' + qi] === LV.obj[qi].a) score++;
        $('q' + qi).className = 'q ' + (saved['q' + qi] === LV.obj[qi].a ? 'correct' : 'wrong');
        var why = $('q' + qi).querySelector('.why');
        if (why) why.className = 'why show';
      }
      $('objScore').textContent = '上次成绩：' + score + ' / ' + LV.obj.length + '（可重做）';
    }
    updateGate();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
  /* 内联 onclick 用的函数暴露到全局 */
  window.submitObj = submitObj;
  window.redoObj = redoObj;
  window.revealWhy = revealWhy;
  window.newRound = newRound;
})();
'''

LEVEL_PAGE_HEAD = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__ID__ __TITLE__ · 编程闯关</title>
<style>__CSS__</style>
</head>
<body>
<header class="top">
  <div class="wrap">
    <p class="crumb"><a href="../index.html">← 返回闯关地图</a></p>
    <span class="badge">__BADGE__</span>
    <h1>__TITLE__</h1>
    <p class="topic">__TOPIC__<span id="timerBox" style="display:none;margin-left:16px;"><span class="timer" id="timer">40:00</span></span></p>
  </div>
</header>
<main class="wrap">
  <div class="banner" id="storeBanner">进度无法保存（浏览器禁用了本地存储），本页功能仍可用，但刷新后记录会丢失。</div>
  <div class="hintbox" id="timeup" style="display:none;">时间到！输入已锁定，点下面「查看全部解析」对照自查；刷新不会解除锁定，想再练一轮点「开始新一轮模拟」。</div>
  <div class="row"><button class="btn ghost" id="revealBtn" style="display:none;" onclick="revealWhy()">查看全部解析</button><button class="btn ghost" id="newRoundBtn" style="display:none;" onclick="newRound()">开始新一轮模拟</button></div>
  <section class="card">
    <h2>第一部分 · 客观题</h2>
    <p class="hintline">全部作答后点「提交判分」，全对是盖章条件之一；做错会显示解析，可重做。</p>
    <div id="objHost"></div>
    <div class="row">
      <button class="btn" id="submitObj" onclick="submitObj()">提交判分</button>
      <button class="btn ghost" id="redoObj" onclick="redoObj()">重做客观题</button>
      <span class="hintline" id="objScore" style="margin:4px 0 0;"></span>
    </div>
  </section>
  <section id="tasks"></section>
  <section class="card gate" id="gate" style="display:none;">
    <div class="stamp" id="stamp">✅ 本关通过，已盖章！</div>
    <a class="btn" id="next" href="../index.html">继续</a>
  </section>
</main>
<footer class="foot">编程闯关备赛 · 离线练习 · 不联网、不上传 · 进度只保存在本机</footer>
<script>
var PAGE_DATA = __DATA__;
</script>
<script>
__JS__
</script>
</body>
</html>
'''


def badge_of(level):
    if level["id"] == "FIN":
        return "终极模拟 · 限时 40 分钟"
    if level["id"].startswith("EXT"):
        return "拓展拔高 · 限时 %d 分钟" % level.get("timeLimitMin", 60)
    if level.get("drill") and level.get("timeLimitMin"):
        return "每日模拟 · 限时 %d 分钟" % level["timeLimitMin"]
    if level.get("drill"):
        return "赛前加练 · 不限时（建议 40 分钟内完成）"
    return "第 %d 关" % (level["index"] + 1)


def render_page(level):
    obj_host = []
    for qi, q in enumerate(level["obj"]):
        is_judge = q["t"] == "judge"
        opts = ["对", "错"] if is_judge else q["opts"]
        lines = ['<div class="q" id="q%d">' % qi,
                 '<p class="qt">%d. %s</p>' % (qi + 1, html_escape(q["q"]))]
        for oi, opt in enumerate(opts):
            val = ('true' if oi == 0 else 'false') if is_judge else str(oi)
            label = "%s. %s" % ("ABCD"[oi], opt) if not is_judge else opt
            lines.append('<label><input type="radio" name="q%d" value="%s"> %s</label>'
                         % (qi, val, html_escape(label)))
        lines.append('<div class="why">解析：%s</div>' % html_escape(q["why"]))
        lines.append('</div>')
        obj_host.append("\n".join(lines))

    html = (LEVEL_PAGE_HEAD
            .replace("__CSS__", PAGE_CSS)
            .replace("__ID__", level["id"])
            .replace("__TITLE__", level["title"])
            .replace("__BADGE__", badge_of(level))
            .replace("__TOPIC__", level["topic"])
            .replace("__JS__", PAGE_JS)
            .replace("__DATA__", json.dumps(level, ensure_ascii=False).replace("</", "<\\/")))
    # 客观题 HTML 由 Python 直接生成（静态），插在占位 div 前
    html = html.replace('<div id="objHost"></div>', '<div id="objHost">\n' + "\n".join(obj_host) + '\n</div>')
    # 判断题答案存为布尔：把 judge 的 radio value 换成 true/false 由 JS 端归一化处理
    return html


# ---------------------------------------------------------------------------
# 闯关地图 index.html（Task 4）
# ---------------------------------------------------------------------------

INDEX_HEAD = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>编程闯关 · 闯关地图</title>
<style>__CSS__</style>
</head>
<body>
<header class="top">
  <div class="wrap">
    <p style="margin:0 0 8px;"><a href="../index.html" style="color:rgba(255,255,255,.88);text-decoration:none;font-size:13.5px;">← 返回三大赛项总入口</a></p>
    <p class="kicker">2026 人工智能素养提升实践活动 · 备赛训练</p>
    <h1>01 编程闯关 · 闯关地图</h1>
    <p class="sub">每关一个知识点：客观题全对 + 编程核对通过就盖章，解锁下一关</p>
    <div class="meta">
      <span>共 <b>8</b> 关 + 1 个模拟关 + <b>2</b> 套加练 + <b>2</b> 套模拟 + <b>1</b> 套拓展</span>
      <span>日常训练 <b>60</b> 分钟 / 模拟关 <b>40</b> 分钟</span>
      <span>环境 <b>Python 3.9 + IDLE</b></span>
      <span>离线可用 · 不联网 · 不上传</span>
    </div>
  </div>
</header>
<main class="wrap">
  <div class="banner" id="storeBanner">进度无法保存（浏览器禁用了本地存储），本页功能仍可用，但刷新后记录会丢失。</div>
  <div class="notice">学习记录只保存在本机浏览器，换电脑或清理浏览器数据会丢失；进度条只作参考，关卡里随时可以重做。</div>
  <div class="notice" style="background:#eef4ff;border-color:#bfd6ff;color:#14417e;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">
    <span><b>单页全课程合集：</b>可在同一页面内切换全部 14 个关卡、模拟卷与拓展卷，进度与地图实时互通。</span>
    <a class="btn" href="编程闯关全课程.html" style="margin-top:4px;">打开「编程闯关全课程.html」 →</a>
  </div>
  <p class="progress-line" id="progressLine"></p>
  <div class="grid" id="map"></div>
  <div class="row" style="margin-top:20px;">
    <button class="btn gray" id="unlockAllBtn" onclick="doUnlockAll()">教师：解锁全部关卡</button>
    <button class="btn gray" id="resetBtn" onclick="doReset()">重置进度</button>
    <span class="hintline" style="margin:6px 0 0;">解锁/重置都会弹出确认框，请谨慎操作。</span>
  </div>
</main>
<footer class="foot">编程闯关备赛 · 零基础 20 天速成 · 离线练习 · 不联网、不上传</footer>
<script>
var MAP_DATA = __DATA__;
</script>
<script>
__JS__
</script>
</body>
</html>
'''

INDEX_JS = r'''
(function () {
  'use strict';
  var KEY = 'ck_progress_v1';
  var storeOK = true;
  var DEF = { v: 1, unlocked: 1, stamps: {}, obj: {}, hints: {}, tasks: {}, final: { started: false, left: 2400 }, timers: {} };

  function loadProg() {
    var p;
    try {
      var raw = localStorage.getItem(KEY);
      if (raw) p = JSON.parse(raw);
    } catch (e) { storeOK = false; p = null; }
    if (!p || typeof p !== 'object') p = {};
    for (var k in DEF) { if (!(k in p)) p[k] = DEF[k]; }
    if (!p.stamps) p.stamps = {};
    if (!p.obj) p.obj = {};
    if (!p.hints) p.hints = {};
    if (!p.tasks) p.tasks = {};
    if (!p.final) p.final = { started: false, left: 2400 };
    if (!p.timers) p.timers = {};
    return p;
  }
  function saveProg() {
    try { localStorage.setItem(KEY, JSON.stringify(prog)); }
    catch (e) { storeOK = false; showBanner(); }
  }
  function showBanner() {
    var b = document.getElementById('storeBanner');
    if (b) b.className = 'banner show';
  }

  function doUnlockAll() {
    var ok = window.confirm('教师模式：解锁全部关卡？（学生将可以自由选择任意关卡）');
    if (!ok) return;
    prog.unlocked = 99;
    saveProg();
    render();
  }
  window.doUnlockAll = doUnlockAll;

  function stateOf(node, prog) {
    var stamped = !!prog.stamps[node.id];
    if (node.drill) return { stamped: stamped, unlocked: true };
    var unlocked = prog.unlocked >= node.index + 1;
    return { stamped: stamped, unlocked: unlocked };
  }

  function render() {
    var map = document.getElementById('map');
    map.innerHTML = '';
    var done = 0;
    var totalMain = 0;
    var drillDone = 0;
    var drillTotal = 0;
    for (var i = 0; i < MAP_DATA.length; i++) {
      var node = MAP_DATA[i];
      var st = stateOf(node, prog);
      if (node.drill) {
        drillTotal++;
        if (st.stamped) drillDone++;
      } else {
        totalMain++;
        if (st.stamped) done++;
      }
      var card = document.createElement('div');
      card.className = 'card ' + (st.stamped ? 'st' : st.unlocked ? 'open' : 'lock');
      var head = document.createElement('div');
      head.className = 'card-head';
      var no = document.createElement('span');
      no.className = 'no';
      no.textContent = node.id === 'FIN' ? '终' : (node.id.indexOf('EXT') === 0 ? '拓' : (node.timeLimitMin ? '模' : (node.drill ? '练' : String(node.index + 1))));
      head.appendChild(no);
      var h3 = document.createElement('h3');
      h3.textContent = node.title;
      head.appendChild(h3);
      card.appendChild(head);
      var desc = document.createElement('p');
      desc.className = 'desc';
      desc.textContent = node.topic;
      card.appendChild(desc);
      var stline = document.createElement('p');
      stline.className = 'state';
      if (st.stamped) {
        stline.textContent = '✅ 已盖章';
      } else if (node.drill && node.timeLimitMin) {
        stline.textContent = '⏱ 限时 ' + node.timeLimitMin + ' 分钟 · 随时可练';
      } else if (node.drill) {
        stline.textContent = '✍ 随时可练 · 不限时';
      } else if (st.unlocked) {
        stline.textContent = node.id === 'FIN' ? '⏱ 限时 40 分钟 · 解锁' : '▶ 可挑战';
      } else {
        stline.textContent = '🔒 未解锁（先通过上一关）';
      }
      card.appendChild(stline);
      if (st.unlocked || st.stamped) {
        var a = document.createElement('a');
        a.className = 'btn';
        a.href = '练习与模拟/' + node.file;
        a.textContent = st.stamped ? '重闯' : '进入关卡';
        card.appendChild(a);
      }
      map.appendChild(card);
    }
    var line = document.getElementById('progressLine');
    line.textContent = '当前进度：已通过 ' + done + ' / ' + totalMain + ' 关' +
      (drillTotal ? '，加练卷已盖章 ' + drillDone + ' / ' + drillTotal : '') +
      (prog.unlocked >= 99 ? '（教师模式：全部已解锁）' : '');
  }

  function doReset() {
    var ok = window.confirm('重置将清空本机全部闯关记录（含各关草稿与盖章），确定继续吗？');
    if (!ok) return;
    try {
      var keys = [];
      for (var i = 0; i < localStorage.length; i++) {
        var k = localStorage.key(i);
        if (k && k.indexOf('ck_') === 0) keys.push(k);
      }
      for (var j = 0; j < keys.length; j++) localStorage.removeItem(keys[j]);
    } catch (e) { showBanner(); }
    prog = loadProg();
    render();
  }
  window.doReset = doReset;

  var prog = loadProg();
  if (!storeOK) showBanner();
  render();
})();
'''

INDEX_CSS = r'''
  :root { --blue:#0b5fff; --blue2:#2fa4ff; --ink:#1c2b3a; --muted:#6f8096;
          --line:#e3ebf5; --bg:#eef3fa; --green:#18a058; --orange:#ff9800; }
  * { box-sizing: border-box; }
  body { margin:0; font-family:"Microsoft YaHei","PingFang SC",system-ui,sans-serif;
         background:var(--bg); color:var(--ink); line-height:1.6; font-size:16px; }
  .wrap { max-width:1080px; margin:0 auto; padding:0 24px 40px; }
  header.top { background:linear-gradient(135deg,#0b5fff 0%,#2fa4ff 100%); color:#fff; padding:34px 0 28px; }
  .kicker { font-size:13px; letter-spacing:3px; color:rgba(255,255,255,.84); margin:0 0 8px; }
  h1 { font-size:32px; margin:0 0 8px; }
  .sub { font-size:15px; color:rgba(255,255,255,.88); margin:0; }
  .meta { display:flex; flex-wrap:wrap; margin-top:14px; font-size:13.5px; color:rgba(255,255,255,.82); }
  .meta > * + * { margin-left:22px; }
  .meta b { color:#fff; }
  .notice { background:#fff8ec; border:1px solid #ffe0b0; color:#8a5a00; border-radius:12px;
            padding:10px 16px; font-size:13.5px; margin:20px 0 0; }
  .banner { display:none; background:#fff8ec; border:1px solid #ffe0b0; color:#8a5a00;
            border-radius:10px; padding:10px 16px; font-size:14px; margin:12px 0 0; }
  .banner.show { display:block; }
  .progress-line { font-size:15px; font-weight:700; color:#14417e; margin:16px 0 12px; }
  .grid { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }
  .card { background:#fff; border:1px solid var(--line); border-radius:14px; padding:16px 18px;
          box-shadow:0 8px 22px rgba(30,70,140,.06); display:flex; flex-direction:column; }
  .card-head { display:flex; align-items:center; margin-bottom:6px; }
  .card-head > * + * { margin-left:10px; }
  .no { width:34px; height:34px; line-height:34px; text-align:center; border-radius:10px;
        background:var(--blue); color:#fff; font-weight:700; font-size:14px; flex:0 0 auto; }
  .card h3 { font-size:17px; margin:0; color:#14417e; }
  .desc { font-size:13.5px; color:#3b4a5f; margin:2px 0 8px; flex:1; }
  .state { font-size:13.5px; color:var(--muted); margin:0 0 10px; }
  .card.st { border-color:#bfe6cf; }
  .card.st .no { background:var(--green); }
  .card.lock { opacity:.62; }
  .card.lock .no { background:#9db2c9; }
  .btn { display:inline-block; border:1px solid var(--blue); background:var(--blue); color:#fff;
         font-size:14px; padding:7px 16px; border-radius:9px; cursor:pointer; text-decoration:none;
         text-align:center; }
  .btn:hover { background:#074fd6; }
  .btn.gray { background:#fff; color:#3b4a5f; border-color:#c9d8ea; }
  .btn.gray:hover { background:#f2f7ff; }
  .row { display:flex; align-items:center; }
  .row > * + * { margin-left:10px; }
  .hintline { font-size:13px; color:var(--muted); }
  footer.foot { border-top:1px solid var(--line); background:#fff; color:var(--muted);
                font-size:13px; padding:16px 0; margin-top:32px; text-align:center; }
  @media (max-width:900px) { .grid { grid-template-columns:repeat(2,1fr); } }
  @media (max-width:600px) { .grid { grid-template-columns:1fr; } }
'''


def render_index():
    nodes = [{"id": lv["id"], "file": lv["file"], "title": lv["title"],
              "topic": lv["topic"], "index": lv["index"]} for lv in LEVELS + [FIN]]
    nodes += [{"id": d["id"], "file": d["file"], "title": d["title"],
               "topic": d["topic"], "drill": True,
               "timeLimitMin": d.get("timeLimitMin", 0)} for d in DRILLS]
    data = json.dumps(nodes, ensure_ascii=False).replace("</", "<\\/")
    return (INDEX_HEAD
            .replace("__CSS__", INDEX_CSS)
            .replace("__DATA__", data)
            .replace("__JS__", INDEX_JS))


ALL_IN_ONE_HEAD = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>01 编程闯关 · 全课程与关卡合集</title>
<style>
__CSS__
.app { display:flex; min-height:100vh; }
.sidebar { width:280px; flex:0 0 280px; background:#fff; border-right:1px solid var(--line); position:sticky; top:0; height:100vh; overflow-y:auto; padding-bottom:20px; }
.side-top { background:linear-gradient(135deg,#0b5fff 0%,#2fa4ff 100%); color:#fff; padding:18px 16px; }
.side-top a { color:rgba(255,255,255,.88); text-decoration:none; font-size:12.5px; }
.side-top h2 { margin:6px 0 4px; font-size:18px; color:#fff; }
.side-top p { margin:0; font-size:12.5px; opacity:.9; }
.nav-sec { font-size:12px; font-weight:700; color:var(--muted); padding:10px 14px 4px; }
.nav-btn { display:flex; justify-content:space-between; align-items:center; padding:8px 14px; margin:2px 8px; border-radius:8px; cursor:pointer; font-size:13.5px; color:var(--ink); }
.nav-btn:hover { background:#f2f7ff; }
.nav-btn.active { background:#eaf2ff; color:var(--blue); font-weight:700; }
.main-area { flex:1; min-width:0; padding:0 0 40px; }
@media (max-width:840px) { .app { flex-direction:column; } .sidebar { width:100%; height:auto; position:static; } }
</style>
</head>
<body>
<div class="app">
  <aside class="sidebar">
    <div class="side-top">
      <a href="index.html">← 返回闯关地图</a> · <a href="../index.html">总入口</a>
      <h2>01 编程闯关全课程</h2>
      <p>8 关教学 + 终极模拟 + 2 加练 + 2 模拟 + 1 拓展</p>
    </div>
    <div id="sideNav"></div>
  </aside>
  <div class="main-area">
    <header class="top">
      <div class="wrap">
        <span class="badge" id="allBadge">第 1 关</span>
        <h1 id="allTitle">初识 print</h1>
        <p class="topic"><span id="allTopic"></span></p>
      </div>
    </header>
    <main class="wrap">
      <div class="banner" id="storeBanner">进度无法保存（浏览器禁用了本地存储），本页功能仍可用。</div>
      <section class="card">
        <h2>第一部分 · 客观题</h2>
        <p class="hintline">全部作答后点「提交判分」，全对是盖章条件之一；做错会显示解析，可重做。</p>
        <div id="objHost"></div>
        <div class="row">
          <button class="btn" onclick="submitObj()">提交判分</button>
          <button class="btn ghost" onclick="redoObj()">重做客观题</button>
          <span class="hintline" id="objScore" style="margin:4px 0 0;"></span>
        </div>
      </section>
      <section id="tasks"></section>
      <section class="card gate" id="gate" style="display:none;">
        <div class="stamp show" id="stamp">✅ 本关通过，已盖章！</div>
      </section>
    </main>
  </div>
</div>
<script>
var ALL_LEVELS = __ALL_DATA__;
</script>
<script>
(function () {
  'use strict';
  var KEY = 'ck_progress_v1';
  var storeOK = true;
  var DEF = { v: 1, unlocked: 1, stamps: {}, obj: {}, hints: {}, tasks: {}, final: { started: false, left: 2400 }, timers: {} };
  var curIdx = 0;
  var LV = ALL_LEVELS[0];

  function $(id) { return document.getElementById(id); }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }
  function loadProg() {
    var p;
    try { var raw = localStorage.getItem(KEY); if (raw) p = JSON.parse(raw); } catch (e) { storeOK = false; p = null; }
    if (!p || typeof p !== 'object') p = {};
    for (var k in DEF) { if (!(k in p)) p[k] = DEF[k]; }
    if (!p.stamps) p.stamps = {};
    if (!p.obj) p.obj = {};
    if (!p.hints) p.hints = {};
    if (!p.tasks) p.tasks = {};
    return p;
  }
  function saveProg() {
    try { localStorage.setItem(KEY, JSON.stringify(prog)); } catch (e) { storeOK = false; $('storeBanner').className = 'banner show'; }
  }
  function normalize(s) {
    var lines = s.replace(/\r\n/g, '\n').replace(/\r/g, '\n').split('\n');
    for (var i = 0; i < lines.length; i++) lines[i] = lines[i].replace(/^[\s　]+/, '').replace(/[\s　]+$/, '');
    while (lines.length && lines[lines.length - 1] === '') lines.pop();
    return lines.join('\n');
  }
  function draftKey(taskId) { return 'ck_draft_' + LV.id + '_' + taskId + '_v1'; }
  function getDraft(taskId) { try { return localStorage.getItem(draftKey(taskId)); } catch (e) { return null; } }
  function setDraft(taskId, text) { try { localStorage.setItem(draftKey(taskId), text); } catch (e) {} }

  function renderSide() {
    var host = $('sideNav');
    var html = '<div class="nav-sec">主线 8 关 + 终极模拟</div>';
    for (var i = 0; i < ALL_LEVELS.length; i++) {
      var item = ALL_LEVELS[i];
      if (i === 9) html += '<div class="nav-sec">赛前加练与每日模拟 / 拓展</div>';
      var st = prog.stamps[item.id] ? '✓' : '';
      html += '<div class="nav-btn' + (i === curIdx ? ' active' : '') + '" data-i="' + i + '"><span>' + item.id + ' · ' + item.title + '</span><span style="color:var(--green);font-weight:700;">' + st + '</span></div>';
    }
    host.innerHTML = html;
    var btns = host.querySelectorAll('.nav-btn');
    for (var b = 0; b < btns.length; b++) {
      btns[b].addEventListener('click', function () {
        curIdx = Number(this.getAttribute('data-i'));
        LV = ALL_LEVELS[curIdx];
        renderSide();
        renderCurrent();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    }
  }

  function renderCurrent() {
    $('allBadge').textContent = LV.badge;
    $('allTitle').textContent = LV.title;
    $('allTopic').textContent = LV.topic;
    var objHost = $('objHost');
    objHost.innerHTML = '';
    for (var qi = 0; qi < LV.obj.length; qi++) {
      var q = LV.obj[qi], isJ = (q.t === 'judge');
      var opts = isJ ? ['对', '错'] : q.opts;
      var card = el('div', 'q'); card.id = 'q' + qi;
      card.appendChild(el('p', 'qt', (qi + 1) + '. ' + q.q));
      for (var oi = 0; oi < opts.length; oi++) {
        var val = isJ ? (oi === 0 ? 'true' : 'false') : String(oi);
        var lblText = isJ ? opts[oi] : ('ABCD'.charAt(oi) + '. ' + opts[oi]);
        var lb = document.createElement('label');
        var inp = document.createElement('input');
        inp.type = 'radio'; inp.name = 'q' + qi; inp.value = val;
        lb.appendChild(inp);
        lb.appendChild(document.createTextNode(' ' + lblText));
        card.appendChild(lb);
      }
      card.appendChild(el('div', 'why', '解析：' + q.why));
      objHost.appendChild(card);
    }
    // 恢复已保存答案
    var saved = prog.obj[LV.id];
    $('objScore').textContent = '';
    if (saved) {
      var score = 0;
      for (var qi2 = 0; qi2 < LV.obj.length; qi2++) {
        var v = saved['q' + qi2];
        var radios = document.getElementsByName('q' + qi2);
        for (var r = 0; r < radios.length; r++) {
          var rv = radios[r].value === 'true' ? true : (radios[r].value === 'false' ? false : Number(radios[r].value));
          if (rv === v) radios[r].checked = true;
        }
        var ok = (v === LV.obj[qi2].a);
        if (ok) score++;
        $('q' + qi2).className = 'q ' + (ok ? 'correct' : 'wrong');
        $('q' + qi2).querySelector('.why').className = 'why show';
      }
      $('objScore').textContent = '上次成绩：' + score + ' / ' + LV.obj.length;
    }

    var thost = $('tasks'); thost.innerHTML = '';
    for (var ti = 0; ti < LV.tasks.length; ti++) {
      (function (ti2) {
        var t = LV.tasks[ti2];
        var card = el('div', 'card');
        var head = el('div', 'task-head');
        head.appendChild(el('h3', null, '任务 ' + (ti2 + 1) + '：' + t.title));
        head.appendChild(el('span', 'opt-tag', t.optional ? '选做 · 不影响盖章' : '必做'));
        card.appendChild(head);
        card.appendChild(el('div', 'desc', t.desc));
        if (t.input !== '无') card.appendChild(el('p', 'hintline', '运行时的输入样例：' + t.input.replace(/\n/g, ' ↦ ')));
        var code = el('textarea'); code.id = 'code' + ti2;
        var d = getDraft(t.id);
        code.value = (d === null || d === '') ? t.starter : d;
        code.oninput = function () { setDraft(t.id, this.value); };
        card.appendChild(code);
        var row2 = el('div', 'row');
        var hBtn = el('button', 'btn ghost', '提示'); hBtn.id = 'hintbtn' + ti2;
        hBtn.onclick = function () {
          var u = prog.hints[LV.id] && prog.hints[LV.id][t.id] ? prog.hints[LV.id][t.id] : 0;
          if (u < t.hints.length) {
            if (!prog.hints[LV.id]) prog.hints[LV.id] = {};
            prog.hints[LV.id][t.id] = u + 1;
            saveProg(); refreshHints(ti2);
          }
        };
        row2.appendChild(hBtn); card.appendChild(row2);
        var hHost = el('div'); hHost.id = 'hints' + ti2; card.appendChild(hHost);
        var out = el('textarea'); out.id = 'out' + ti2; out.placeholder = '把 IDLE 运行输出粘贴到这里核对…';
        card.appendChild(out);
        var row3 = el('div', 'row');
        var cBtn = el('button', 'btn', '核对输出');
        cBtn.onclick = function () {
          var pasted = $('out' + ti2).value, msg = $('msg' + ti2);
          if (pasted.indexOf('Traceback') !== -1) { msg.className = 'msg bad show'; msg.textContent = '发现报错 Traceback，请回 IDLE 检查红字最后一行。'; return; }
          if (normalize(pasted) === normalize(t.expect)) {
            if (!prog.tasks[LV.id]) prog.tasks[LV.id] = {};
            prog.tasks[LV.id][t.id] = true; saveProg();
            msg.className = 'msg ok show'; msg.textContent = '输出一致，通过！'; updateGate();
          } else {
            msg.className = 'msg bad show'; msg.textContent = '输出还不一致，请核对文字、行数与标点。';
          }
        };
        row3.appendChild(cBtn); card.appendChild(row3);
        var msg = el('div', 'msg'); msg.id = 'msg' + ti2; card.appendChild(msg);
        thost.appendChild(card);
        refreshHints(ti2);
      })(ti);
    }
    updateGate();
  }

  function refreshHints(ti) {
    var t = LV.tasks[ti];
    var u = prog.hints[LV.id] && prog.hints[LV.id][t.id] ? prog.hints[LV.id][t.id] : 0;
    $('hintbtn' + ti).textContent = '提示（已用 ' + u + '/' + t.hints.length + '）';
    var host = $('hints' + ti); host.innerHTML = '';
    for (var i = 0; i < u && i < t.hints.length; i++) host.appendChild(el('div', 'hintbox', '提示 ' + (i + 1) + '：' + t.hints[i]));
  }

  function submitObj() {
    var saved = {}, score = 0;
    for (var qi = 0; qi < LV.obj.length; qi++) {
      var radios = document.getElementsByName('q' + qi), v = null;
      for (var r = 0; r < radios.length; r++) if (radios[r].checked) v = radios[r].value;
      var card = $('q' + qi); card.querySelector('.why').className = 'why show';
      if (v === null) { card.className = 'q wrong'; continue; }
      var norm = v === 'true' ? true : (v === 'false' ? false : Number(v));
      var ok = (norm === LV.obj[qi].a);
      if (ok) score++;
      card.className = 'q ' + (ok ? 'correct' : 'wrong');
      saved['q' + qi] = norm;
    }
    prog.obj[LV.id] = saved; saveProg();
    $('objScore').textContent = '得分：' + score + ' / ' + LV.obj.length;
    updateGate();
  }
  function redoObj() { delete prog.obj[LV.id]; saveProg(); renderCurrent(); }
  function updateGate() {
    var saved = prog.obj[LV.id], objOk = !!saved;
    if (objOk) {
      for (var qi = 0; qi < LV.obj.length; qi++) if (saved['q' + qi] !== LV.obj[qi].a) objOk = false;
    }
    var taskOk = true;
    for (var ti = 0; ti < LV.tasks.length; ti++) {
      var t = LV.tasks[ti];
      if (!t.optional && (!prog.tasks[LV.id] || !prog.tasks[LV.id][t.id])) taskOk = false;
    }
    if (objOk && taskOk) {
      prog.stamps[LV.id] = true; saveProg(); renderSide();
    }
    $('gate').style.display = prog.stamps[LV.id] ? 'block' : 'none';
  }
  window.submitObj = submitObj;
  window.redoObj = redoObj;

  var prog = loadProg();
  renderSide();
  renderCurrent();
})();
</script>
</body>
</html>
'''


def render_all_in_one():
    items = []
    for idx, lv in enumerate(LEVELS + [FIN]):
        lv["index"] = idx
        cp = dict(lv)
        cp["badge"] = badge_of(lv)
        items.append(cp)
    for dr in DRILLS:
        cp = dict(dr)
        cp["badge"] = badge_of(dr)
        items.append(cp)
    data = json.dumps(items, ensure_ascii=False).replace("</", "<\\/")
    return ALL_IN_ONE_HEAD.replace("__CSS__", PAGE_CSS).replace("__ALL_DATA__", data)


def generate():
    os.makedirs(OUT_LEVELS, exist_ok=True)
    made = []
    for idx, level in enumerate(LEVELS + [FIN]):
        level["index"] = idx
        path = os.path.join(OUT_LEVELS, level["file"])
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(render_page(level))
        made.append(os.path.relpath(path, REPO))
    for drill in DRILLS:
        path = os.path.join(OUT_LEVELS, drill["file"])
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(render_page(drill))
        made.append(os.path.relpath(path, REPO))
    with io.open(OUT_INDEX, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_index())
    made.append(os.path.relpath(OUT_INDEX, REPO))
    with io.open(OUT_ALL, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_all_in_one())
    made.append(os.path.relpath(OUT_ALL, REPO))
    for m in made:
        print("生成 " + m)
    print("共生成 %d 个文件" % len(made))
    return 0


def main(argv):
    if "--selftest" in argv:
        return run_selftest()
    if "--verify" in argv:
        rc = run_verify()
        if rc != 0:
            return rc
        return generate()
    return generate()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成课件.py -- 大数分解课程 5 份 PPTX 课件的内容源（教师包专属）。

用法：
    python 生成课件.py 01     # 生成第 01 讲 课件.pptx
    python 生成课件.py all    # 生成全部讲次

约定（00_制作规范.md §6）：16:9；微软雅黑 + Consolas；显式声明东亚字体 a:ea；
教师内容（完整答案、讲稿）只进演讲者备注，正文页只放任务与预期输出。
"""
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

TRACK_ROOT = Path(__file__).resolve().parent.parent   # 02_大数分解/
COURSE_ROOT = TRACK_ROOT / "练习与模拟"

BLUE = RGBColor(0x24, 0x46, 0x6E)   # 主色
INK = RGBColor(0x24, 0x32, 0x4A)    # 正文
MUT = RGBColor(0x51, 0x60, 0x7A)    # 次要
CODE_BG = RGBColor(0xF4, 0xF6, 0xFA)
WARN = RGBColor(0xC0, 0x39, 0x2B)   # 强调（陷阱/错误）
OKG = RGBColor(0x2E, 0x8B, 0x57)    # 通过
GOLD = RGBColor(0x8A, 0x6D, 0x1A)

YAHEI = "微软雅黑"
MONO = "Consolas"


def _set_ea(run, name):
    """显式声明东亚字体，防止中文缺字。"""
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = rPr.makeelement(qn("a:ea"), {})
        rPr.append(ea)
    ea.set("typeface", name)


def style_run(run, text, size, bold=False, color=INK, font=YAHEI):
    run.text = text
    f = run.font
    f.size = Pt(size)
    f.bold = bold
    f.color.rgb = color
    f.name = font
    _set_ea(run, YAHEI if font == YAHEI else YAHEI)  # 代码里的中文注释回退雅黑


def text_box(slide, x, y, w, h):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    return tf


def para(tf, text, size, bold=False, color=INK, font=YAHEI, align=None, space_after=6, first=False):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    if align is not None:
        p.alignment = align
    p.space_after = Pt(space_after)
    style_run(p.add_run(), text, size, bold, color, font)
    return p


def code_box(slide, x, y, w, h, lines, size=15, color=INK, bg=CODE_BG):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = bg
    shp.line.fill.background()
    shp.shadow.inherit = False
    tf = shp.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.18)
    tf.margin_top = Inches(0.12)
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        style_run(p.add_run(), ln, size, color=color, font=MONO)
    return shp


def badge(slide, x, y, w, h, text, bg, fg):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = bg
    shp.line.fill.background()
    shp.shadow.inherit = False
    tf = shp.text_frame
    tf.margin_left = Inches(0.05)
    tf.margin_top = Inches(0.02)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    style_run(p.add_run(), text, 14, True, fg)
    return shp


def content_slide(prs, title, notes, kicker=None):
    """内容页骨架：标题 +（可选角标）；返回 slide。"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    tf = text_box(slide, 0.6, 0.32, 11.2, 0.9)
    para(tf, title, 28, True, BLUE, first=True, space_after=0)
    if kicker:
        kb = badge(slide, 11.0, 0.38, 1.7, 0.42, kicker, CODE_BG, MUT)
    slide.notes_slide.notes_text_frame.text = notes
    return slide


def table(slide, x, y, w, rows_data, col_widths, size=16, head=True, row_h=0.42):
    n_rows = len(rows_data)
    n_cols = len(rows_data[0])
    shp = slide.shapes.add_table(n_rows, n_cols, Inches(x), Inches(y), Inches(w), Inches(row_h * n_rows))
    tbl = shp.table
    for ci, cw in enumerate(col_widths):
        tbl.columns[ci].width = Inches(cw)
    for ri, row in enumerate(rows_data):
        for ci, val in enumerate(row):
            cell = tbl.cell(ri, ci)
            cell.margin_left = Inches(0.08)
            cell.margin_top = Inches(0.03)
            cell.margin_bottom = Inches(0.03)
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            is_head = head and ri == 0
            font = MONO if (not is_head and ci >= 1 and _is_code_col(rows_data, ci)) else YAHEI
            style_run(p.add_run(), str(val), size - (1 if not is_head else 0), is_head,
                      BLUE if is_head else INK, font)
    return tbl


def _is_code_col(rows_data, ci):
    """启发式：列内容多含代码特征（=、(、//、_) 时用等宽字体。"""
    sample = "".join(str(r[ci]) for r in rows_data[1:4])
    return any(tok in sample for tok in ("=", "(", "//", ">>", "<<", "%", "_", "x ="))


# ============================================================
# 第 01 讲课件：Python 基础速通（11 页）
# ============================================================

def build_ppt01(out_path):
    prs = Presentation()
    prs.slide_width = Emu(12192000)  # 标准 16:9 宽（13.333 英寸写法取整有偏差）
    prs.slide_height = Inches(7.5)

    # ---- 1 封面 ----
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bgshape = slide_bg(s, BLUE)
    tf = text_box(s, 1.0, 2.2, 11.3, 2.2)
    para(tf, "第 01 讲 · Python 基础速通", 40, True, RGBColor(0xFF, 0xFF, 0xFF), first=True, space_after=10)
    para(tf, "大数分解备赛课程 · 从零开始，学会六个句型", 20, False, RGBColor(0xCA, 0xDC, 0xFC))
    tf2 = text_box(s, 1.0, 5.9, 11.3, 0.5)
    para(tf2, "配套：练习.html（客观题 6 道 + 任务 3 个）· 代码/demo1_六大句型.py", 14, False,
         RGBColor(0xCA, 0xDC, 0xFC), first=True, space_after=0)
    s.notes_slide.notes_text_frame.text = (
        "开场 1 分钟：这一讲从零开始，不需要任何编程经验，只要会开机打字。"
        "今天只学六件事（六大句型），比赛要用的分解程序就是这六件事拼起来的。"
        "提醒学生打开练习.html 与 demo1_六大句型.py。"
    )

    # ---- 2 Python 能做什么：大数演示 ----
    s = content_slide(prs, "Python 能做什么？先看一个大数", "现场把左边代码跑一遍，让 31 位数在投影上出现。"
         "问一句：这要是笔算要多久？--Python 一瞬间。这就是比赛选 Python 的底气。"
         "再强调：比赛用的分解程序，只需要今天这六件事，谁都学得会。")
    code_box(s, 0.6, 1.6, 6.2, 2.6, [
        ">>> 2 ** 100",
        "1267650600228229401496703205376",
        "",
        "（31 位，精确无误差）",
    ], size=17, bg=RGBColor(0xF2, 0xFB, 0xF6))
    tf = text_box(s, 7.2, 1.6, 5.5, 4.4)
    para(tf, "为什么大数分解比赛适合用 Python？", 19, True, BLUE, first=True, space_after=8)
    for t in (
        "计算器、Excel 到十几位就不够用了",
        "Python 的整数要多大有多大：12 位、18 位直接乘除",
        "今天只学六个句型，就能让 Python 替你分解大数",
    ):
        para(tf, t, 17, False, INK, space_after=10)
    badge(s, 0.6, 4.6, 6.2, 0.5, "大数不溢出 = 比赛的底气", CODE_BG, BLUE)

    # ---- 3 六大句型总览 ----
    s = content_slide(prs, "六大句型：今天全部内容", "这一页是今天的地图，每格后面有一页精讲。"
         "跟学生说：看懂这张表，今天就毕业了。每个句型先看例子、再自己照打一遍。")
    table(s, 0.6, 1.5, 12.1, [
        ["句型", "一句话", "例子"],
        ["1 输出", "让 Python 显示东西", "print(\"你好\")"],
        ["2 变量", "给一个值起个名字", "n = 7"],
        ["3 输入", "等用户敲一个数进来", "n = int(input())"],
        ["4 判断", "满足条件做甲，否则做乙", "if n % 2 == 0: ... else: ..."],
        ["5 循环累加", "从 1 数到 n，边数边加", "for i in range(1, n + 1):"],
        ["6 函数", "把一段活打包，随取随用", "def add(a, b): return a + b"],
    ], [2.0, 4.6, 5.5], size=16, row_h=0.62)

    # ---- 4 句型 1+2：输出与变量 ----
    s = content_slide(prs, "句型 1 输出 · 句型 2 变量", "逐行现场跑。关键一句：引号包住的叫字符串，原样显示；"
         "不带引号的才算数。变量像贴了名字的盒子，n = 7 之后，说 n 就是说 7。")
    code_box(s, 0.6, 1.5, 5.9, 3.0, [
        "print(\"你好，Python\")",
        "你好，Python",
        "",
        "print(2 + 3)",
        "5            ← 不带引号才计算",
    ], size=17)
    code_box(s, 6.8, 1.5, 5.9, 3.0, [
        "n = 7        ← 把 7 存进 n",
        "print(n)",
        "7",
        "",
        "n = n + 1    ← n 变成 8",
    ], size=17)
    tf = text_box(s, 0.6, 5.0, 12.1, 1.4)
    para(tf, "跟做：在 IDLE 里打出左边 4 行，对照输出。", 18, True, BLUE, first=True, space_after=0)

    # ---- 5 句型 3：输入 ----
    s = content_slide(prs, "句型 3 输入：int(input())", "现场演示报错再演示正确写法。收口口诀齐读："
         "读进来的数，用之前先转；一行两个数，先 split 再逐个 int。", kicker="高频报错")
    code_box(s, 0.6, 1.5, 5.9, 2.9, [
        "n = input()        # 读到 '8'，是文字",
        "print(n % 2)",
        "",
        "TypeError: ...     ← 文字不能算术",
    ], size=17, color=WARN)
    code_box(s, 6.8, 1.5, 5.9, 2.9, [
        "n = int(input())        # 一个数",
        "a, b = input().split()  # 一行两个",
        "a = int(a)              # 逐个转",
        "b = int(b)",
    ], size=17, color=OKG, bg=RGBColor(0xF2, 0xFB, 0xF6))
    tf = text_box(s, 0.6, 4.9, 12.1, 1.6)
    para(tf, "口诀：读进来的数，用之前先转；一行多个数，先 split 再逐个 int。", 19, True, BLUE, first=True, space_after=0)

    # ---- 6 句型 4：判断 ----
    s = content_slide(prs, "句型 4 判断：if / else", "两个铁律现场演示：漏冒号报 SyntaxError；缩进不齐报 IndentationError。"
         "n % 2 == 0 读作「n 除以 2 余 0」，两个等号是比较，一个等号是存值。")
    code_box(s, 0.6, 1.5, 5.9, 3.4, [
        "n = 8",
        "if n % 2 == 0:      ← 行末冒号",
        "    print(\"偶数\")    ← 缩进 4 格",
        "else:",
        "    print(\"奇数\")",
    ], size=17)
    tf = text_box(s, 6.8, 1.5, 5.9, 3.4)
    para(tf, "两个铁律", 19, True, BLUE, first=True, space_after=8)
    para(tf, "1. if、else 行末都要英文冒号 :", 17, False, INK, space_after=8)
    para(tf, "2. 该缩进的地方缩 4 个空格", 17, False, INK, space_after=8)
    para(tf, "比较用 ==（两个等号）", 17, False, INK, space_after=8)
    para(tf, "存值用 =（一个等号）", 17, False, WARN, space_after=0)

    # ---- 7 句型 5：循环累加 ----
    s = content_slide(prs, "句型 5 循环累加：分解程序的发动机", "左边从 1 加到 4，右边是累加器三件套。"
         "收口：把 total 换成「收集因数的列表」、把加法换成「除」，就是第 02 讲的分解程序--这句话一定要说。")
    code_box(s, 0.6, 1.5, 5.9, 3.4, [
        "total = 0",
        "for i in range(1, 5):",
        "    total = total + i",
        "print(total)",
        "10            ← 1+2+3+4",
    ], size=17)
    tf = text_box(s, 6.8, 1.5, 5.9, 3.4)
    para(tf, "累加器三件套", 19, True, BLUE, first=True, space_after=8)
    para(tf, "1. 先给 total 一个起点 0", 17, False, INK, space_after=8)
    para(tf, "2. range(1, n + 1)：从 1 数到 n", 17, False, INK, space_after=8)
    para(tf, "3. 循环体里 total = total + i", 17, False, INK, space_after=8)
    para(tf, "（以后还会把结果收集进「列表」，第 02 讲学）", 15, False, MUT, space_after=0)

    # ---- 8 句型 6：函数 ----
    s = content_slide(prs, "句型 6 函数：把活打包", "函数就是「起个名字的一段活」：def 定义、参数是原料、return 是成品。"
         "比赛程序会把「判断质数」「分解」打包成函数，让主程序像点菜一样调用。")
    code_box(s, 0.6, 1.5, 5.9, 3.4, [
        "def add(a, b):        ← 定义，a b 是原料",
        "    return a + b      ← 成品交回去",
        "",
        "print(add(3, 4))",
        "7                     ← 随取随用",
    ], size=17)
    tf = text_box(s, 6.8, 1.5, 5.9, 3.4)
    para(tf, "为什么要打包？", 19, True, BLUE, first=True, space_after=8)
    para(tf, "写一次，到处用", 17, False, INK, space_after=8)
    para(tf, "出错只改一处", 17, False, INK, space_after=8)
    para(tf, "主程序一眼能读懂", 17, False, INK, space_after=8)
    para(tf, "评分表「模块划分明确」说的就是这个", 15, False, MUT, space_after=0)

    # ---- 9 练习页任务 ----
    s = content_slide(prs, "练习页任务（T1–T3）", "T1 参考解：s=input(); a,b=s.split(); a=int(a); b=int(b); print(a+b); print(a-b)"
         "　T2：n=int(input()); if n%2==0: print('yes') else: print('no')"
         "　T3：n=int(input()); total=0; for i in range(1,n+1): total=total+i; print(total)。"
         "核对方式：IDLE 运行 → 复制全部输出 → 练习页粘贴核对。卡住先点三级提示，别直接问。")
    table(s, 0.6, 1.5, 12.1, [
        ["任务", "做什么", "输入", "预期输出"],
        ["T1 和与差", "读一行两个整数，输出和、差各一行", "10 3", "13 与 7 两行"],
        ["T2 奇偶判断", "偶数输出 yes，否则 no", "8", "yes"],
        ["T3 求和（选做）", "1 + 2 + …… + n", "100", "5050"],
    ], [2.2, 5.6, 1.8, 2.5], size=17, row_h=0.7)
    tf = text_box(s, 0.6, 4.6, 12.1, 1.6)
    para(tf, "流程：IDLE 写码 → 运行 → 复制输出 → 练习页「核对输出」", 18, True, BLUE, first=True, space_after=6)
    para(tf, "客观题 6 道（4 单选 + 2 填空）做满分；三级提示按需取用，用了会记账。", 17, False, MUT, space_after=0)

    # ---- 10 课堂安排 ----
    s = content_slide(prs, "40 分钟怎么用", "前 20 分钟跟做为主：每句型教师打一行、学生照打一行，别赶。"
         "20 分钟后的任务环节巡视三件事：冒号、缩进、int 转换。提前完成的做客观题。"
         "0-5 分钟的大数演示一定要跑，学生的印象大多来自这一下。")
    table(s, 0.6, 1.6, 12.1, [
        ["时间", "环节", "做什么"],
        ["0–5", "Python 能做什么", "跑 2 ** 100 大数演示，立「学得会」的信心"],
        ["5–20", "六大句型跟做", "demo1_六大句型.py 逐节：教师打一行，学生照打一行"],
        ["20–32", "任务 T1 / T2", "模仿改：改输入、改输出；T3 选做"],
        ["32–37", "客观题", "练习页 6 道，对照解析"],
        ["37–40", "收口", "齐读六句型；预告：下一讲拼出分解程序"],
    ], [1.6, 2.4, 8.1], size=17, row_h=0.66)

    # ---- 11 小结 ----
    s = content_slide(prs, "小结与作业", "六句型齐读一遍。作业 2 手算题目下讲开头对答案。"
         "预告要说清：今天学的输入、判断、循环累加，拼起来就是分解程序--学生带着「我会用」的感觉出教室。")
    tf = text_box(s, 0.6, 1.4, 6.0, 4.8)
    para(tf, "带走六大句型", 20, True, BLUE, first=True, space_after=8)
    for t in ("print() 显示", "n = 7 存值", "int(input()) 读入", "if / else 判断", "for + 累加", "def + return 打包"):
        para(tf, t, 18, False, INK, space_after=6)
    tf2 = text_box(s, 7.0, 1.4, 5.7, 4.8)
    para(tf2, "作业", 20, True, BLUE, first=True, space_after=8)
    for t in ("1. 练习页 T1、T2 核对通过，T3 选做；客观题满分", "2. 手算：8、12、15 各有哪些因数（下讲开头对答案）", "3. 预告：下一讲把六句型拼成「因数分解」程序"):
        para(tf2, t, 17, False, INK, space_after=10)
    badge(s, 7.0, 5.6, 5.7, 0.5, "六大句型 = 分解程序的全部零件", CODE_BG, BLUE)

    prs.save(out_path)


SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)


def slide_bg(slide, color):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


# ============================================================
# 第 02 讲课件：因数分解实战（12 页，含 2 页零基础概念铺垫）
# ============================================================

def build_ppt02(out_path):
    prs = Presentation()
    prs.slide_width = Emu(12192000)  # 标准 16:9 宽（13.333 英寸写法取整有偏差）
    prs.slide_height = Inches(7.5)

    # ---- 1 封面 ----
    s = prs.slides.add_slide(prs.slide_layouts[6])
    slide_bg(s, BLUE)
    tf = text_box(s, 1.0, 2.2, 11.3, 2.2)
    para(tf, "第 02 讲 · 因数分解实战", 40, True, RGBColor(0xFF, 0xFF, 0xFF), first=True, space_after=10)
    para(tf, "对准评分表「数字分解与处理 15 分」--分解、成分提取、统计、格式规范", 20, False,
         RGBColor(0xCA, 0xDC, 0xFC))
    tf2 = text_box(s, 1.0, 5.9, 11.3, 0.5)
    para(tf2, "配套：练习.html（6 道客观题 + T1–T3）· 代码/ 质因数分解与成分提取", 14, False,
         RGBColor(0xCA, 0xDC, 0xFC), first=True, space_after=0)
    s.notes_slide.notes_text_frame.text = (
        "开场：上一讲从零学会了六大句型，这一讲把它们拼成真正的分解程序，开始挣分。评分表「数字分解与处理」原文要求："
        "正确实现分解、指定成分提取、分类筛选与统计结果准确、输出完整格式规范--15 分里格式分最容易丢也最容易拿。"
        "本讲先手算后代码：因数与质数从零讲（前 8 分钟），再分步搭双循环。"
    )

    # ---- 2 本讲对准的评分项 ----
    s = content_slide(prs, "评分表原文与本讲目标", "把评分表原文读一遍：正确实现指定的大数分解、指定成分提取，"
         "分类筛选与统计结果准确，输出完整、格式规范。T1 对分解、T2 对成分提取与筛选统计，格式贯穿全部。")
    tf = text_box(s, 0.6, 1.35, 7.3, 2.2)
    para(tf, "评分表原文（数字分解与处理 · 15 分）", 18, True, BLUE, first=True, space_after=8)
    code_box(s, 0.6, 2.0, 7.3, 1.5, [
        "能正确实现题目指定的大数分解、指定成分提取，",
        "分类筛选与统计结果准确，输出完整、格式规范。",
    ], size=16, bg=CODE_BG)
    tf2 = text_box(s, 0.6, 4.0, 7.3, 2.6)
    para(tf2, "学习目标", 18, True, BLUE, first=True, space_after=8)
    for t in ("写出三种分解程序：全因数、质因数分解式、成分统计",
              "输出逐字符符合题面格式（本讲主战场）",
              "用因数个数定理验算程序结果"):
        para(tf2, t, 17, False, INK, space_after=8)
    badge(s, 8.3, 1.5, 4.4, 0.6, "格式分 = 白送的分，也最容易丢", RGBColor(0xFD, 0xF5, 0xF4), WARN)

    # ---- 3 输出格式规范 ----
    s = content_slide(prs, "格式三查：对照卡", "逐行念错误样例，让学生说错在哪。乘号 × 是半角字符，两侧各一个空格；"
         "等号两侧各一个空格；末尾不能有尾巴。宣布规矩：交核对前先自己比对预期输出。")
    table(s, 0.6, 1.5, 12.1, [
        ["样例", "错在哪"],
        ["180=2×2×3×3×5", "等号、乘号两侧缺空格"],
        ["180 = 2 X 2 X 3", "用了字母 X，不是乘号 ×"],
        ["180 = 2 * 2 * 3", "用了星号 *，题面要 ×"],
        ["180 = 2 × 2 × 3 × 3 × 5 ␣", "末尾多了空格"],
        ["2 × 2 × 3 × 3 × 5", "漏了 180 = 前缀"],
    ], [6.2, 5.9], size=17, row_h=0.62)
    tf = text_box(s, 0.6, 5.4, 12.1, 0.8)
    para(tf, "口诀：照抄模板，逐字符对；× 从 starter 里复制，不手打。", 19, True, BLUE, first=True, space_after=0)

    # ---- 4 因数与质数（零基础概念铺垫）----
    s = content_slide(prs, "从零讲：因数与质数", "零基础开场 0–8 分钟，先不写代码。手算 12 的因数：1×12、2×6、3×4，"
         "从小到大排成 1,2,3,4,6,12。质数一句话：只能被 1 和自己整除。两个判断题活跃气氛："
         "1 是质数吗（不是，因数只有它自己）；91 是质数吗（7×13=91，不是--会分解就知道答案）。")
    tf = text_box(s, 0.6, 1.35, 6.4, 3.4)
    para(tf, "手算：12 的全部因数", 17, True, BLUE, first=True, space_after=8)
    para(tf, "1 × 12 = 12", 16, False, INK, font=MONO, space_after=2)
    para(tf, "2 × 6  = 12", 16, False, INK, font=MONO, space_after=2)
    para(tf, "3 × 4  = 12", 16, False, INK, font=MONO, space_after=2)
    para(tf, "从小到大：1, 2, 3, 4, 6, 12（共 6 个）", 16, False, MUT, space_after=0)
    code_box(s, 7.2, 1.4, 5.5, 1.9, [
        "质数：只能被 1 和自己整除",
        "2, 3, 5, 7, 11, 13 ……",
        "1 不是质数（因数只有它自己）",
    ], size=16)
    tf2 = text_box(s, 0.6, 5.2, 12.1, 1.5)
    para(tf2, "想一想：91 是质数吗？--7 × 13 = 91，不是。会分解就有答案。", 18, True, BLUE, first=True, space_after=6)
    para(tf2, "今天的任务：让计算机替我们做这套手算。", 16, False, MUT, space_after=0)

    # ---- 5 短除法手算 + 列表三行（零基础概念铺垫）----
    s = content_slide(prs, "手算短除法，认识列表", "全班齐手算 60：除 2 两次、除 3 一次、除 5 一次，得 2×2×3×5。"
         "然后补六大句型之外唯一的新工具「列表」，三行跟做：parts = [] 空抽屉、parts.append(2) 往里放、"
         "print(parts) 看一眼。说明：分解程序就用列表装求出来的因子，最后拼成分解式。")
    tf = text_box(s, 0.6, 1.35, 4.2, 4.6)
    para(tf, "短除法竖式（60）", 17, True, BLUE, first=True, space_after=8)
    para(tf, "2 │ 60", 16, False, INK, font=MONO, space_after=2)
    para(tf, "2 │ 30", 16, False, INK, font=MONO, space_after=2)
    para(tf, "3 │ 15", 16, False, INK, font=MONO, space_after=2)
    para(tf, "5 │  5", 16, False, INK, font=MONO, space_after=2)
    para(tf, "  │  1  ← 除完", 16, False, MUT, font=MONO, space_after=6)
    para(tf, "60 = 2 × 2 × 3 × 5", 17, True, BLUE, space_after=0)
    tf3 = text_box(s, 5.2, 1.35, 7.5, 0.5)
    para(tf3, "新工具：列表（装一串数的抽屉）--三行跟做", 17, True, BLUE, first=True, space_after=0)
    code_box(s, 5.2, 1.95, 7.5, 2.3, [
        "parts = []           # 空列表：一个空的抽屉",
        "parts.append(2)      # 往抽屉里放一个 2",
        "print(parts)         # 看一眼：[2]",
        "parts.append(3)      # 再放一个 3",
        "print(parts)         # [2, 3]--按放的顺序排队",
    ], size=16)
    tf2 = text_box(s, 5.2, 4.5, 7.5, 1.5)
    para(tf2, "分解程序就用列表装因子，最后拼成「180 = 2 × 2 × 3 × 3 × 5」。", 16, False, INK, first=True, space_after=0)

    # ---- 6 短除法 → 双循环 ----
    s = content_slide(prs, "短除法 → 双循环（分步四步搭）", "分步教学 8–16 分钟：第一步只写内层 while（m = 60 反复除 2，"
         "print(m) 看着 60→30→15，跑通）；第二步加外层候选循环（除完 2 换 3）；第三步加 if m > 1 补质数尾巴；"
         "第四步拼输出格式。竖式按 180 演示完整版。强调两处：内层 while 是「同一个因子反复除」，m = m // i 是整除。"
         "starter 注释区的第 1–5 步与这四步一一对应。", kicker="核心页")
    tf = text_box(s, 0.6, 1.35, 4.2, 4.6)
    para(tf, "短除法竖式（180）", 17, True, BLUE, first=True, space_after=8)
    para(tf, "2 │ 180", 16, False, INK, font=MONO, space_after=2)
    para(tf, "2 │  90", 16, False, INK, font=MONO, space_after=2)
    para(tf, "3 │  45", 16, False, INK, font=MONO, space_after=2)
    para(tf, "3 │  15", 16, False, INK, font=MONO, space_after=2)
    para(tf, "5 │   5", 16, False, INK, font=MONO, space_after=2)
    para(tf, "  │   1  ← 除完", 16, False, MUT, font=MONO, space_after=2)
    code_box(s, 5.2, 1.5, 7.5, 3.6, [
        "m = n;  parts = [];  i = 2",
        "while i * i <= m:        # 外层：换下一个候选",
        "    while m % i == 0:    # 内层：反复除同一个",
        "        parts.append(i)",
        "        m = m // i       # 整除，别写 /",
        "    i = i + 1",
    ], size=16)
    tf2 = text_box(s, 5.2, 5.4, 7.5, 1.2)
    para(tf2, "180 → [2, 2, 3, 3, 5]，拼上「 × 」就是分解式。", 17, False, INK, first=True, space_after=0)
    badge(s, 0.6, 6.35, 12.1, 0.5, "分步搭：① 内层反复除 → ② 外层换候选 → ③ 质数尾巴 if m > 1 → ④ 拼输出", CODE_BG, BLUE)

    # ---- 7 质数边界 ----
    s = content_slide(prs, "质数边界：循环后 m > 1", "现场跑 7：外层 while 一次都不进（2×2>7），parts 是空的，"
         "但 7 自己是因子。所以循环结束后 m > 1 就 append。跑 2 验证最小边界。", kicker="易丢分点")
    code_box(s, 0.6, 1.5, 5.9, 2.6, [
        "if m > 1:",
        "    parts.append(m)",
        "",
        "# 循环结束时，m 要么是 1，",
        "# 要么是剩下的最大质因子",
    ], size=17)
    table(s, 6.8, 1.5, 5.9, [
        ["输入", "parts", "输出"],
        ["180", "[2,2,3,3,5]", "180 = 2 × 2 × 3 × 3 × 5"],
        ["7", "[7]", "7 = 7"],
        ["2", "[2]", "2 = 2"],
    ], [1.1, 1.9, 2.9], size=15, row_h=0.5)
    tf = text_box(s, 0.6, 4.7, 12.1, 1.4)
    para(tf, "不写这两行的后果：质数输入输出 n = （空），格式分直接归零。", 18, True, WARN, first=True, space_after=0)

    # ---- 8 T1 任务页 ----
    s = content_slide(prs, "任务 T1 · 质因数分解", "T1 参考解在 answer1_质因数分解.py。"
         "巡视盯三处：m = m // i 的整除、内层 while 反复除、输出拼接的「 × 」。"
         "提前完成的试 7 和 2（质数边界）。", kicker="必做 10 分钟")
    table(s, 0.6, 1.5, 12.1, [
        ["项目", "内容"],
        ["输入", "一个整数 n（2 ≤ n ≤ 10^9，可能是质数）"],
        ["输出", "一行：n = 因子1 × 因子2 × ……（因子从小到大）"],
        ["样例 1", "输入 180 → 180 = 2 × 2 × 3 × 3 × 5"],
        ["样例 2", "输入 7 → 7 = 7"],
    ], [2.0, 10.1], size=17, row_h=0.62)
    tf = text_box(s, 0.6, 5.0, 12.1, 1.2)
    para(tf, "流程：IDLE 写码 → 运行 → 复制输出 → 练习页「核对输出」；格式错一个字符都过不了核对--故意的。", 17, False, MUT, first=True, space_after=0)

    # ---- 9 T2 成分提取 ----
    s = content_slide(prs, "任务 T2 · 成分提取与统计", "T2 参考解在 answer2_成分提取.py（180 → 12 / 78 / 5）。"
         "第一部分枚举全因数分两类统计；第二部分复用短除法取最大质因数--"
         "短除法里 max_prime = i 每次覆盖，最后留下的就是最大质因子。先对数再对格式。", kicker="必做 8 分钟")
    table(s, 0.6, 1.5, 12.1, [
        ["问什么", "怎么算", "n = 180 时"],
        ["偶因数个数", "枚举 i：n % i == 0 且 i % 2 == 0 计数", "12"],
        ["奇因数之和", "枚举 i：n % i == 0 且 i 是奇数累加", "1+3+5+9+15+45 = 78"],
        ["最大质因数", "短除法，最后除掉的因子（或剩下的 m）", "5"],
    ], [2.6, 6.4, 3.1], size=16, row_h=0.62)
    tf = text_box(s, 0.6, 4.4, 12.1, 1.8)
    para(tf, "输出三行，每行一个数：12、78、5。写完先自己心算一遍再核对。", 18, True, BLUE, first=True, space_after=6)
    para(tf, "常见错：最大质因数直接输出 n（那是最大因数不是质因数）。", 16, False, WARN, space_after=0)

    # ---- 10 因数个数定理 ----
    s = content_slide(prs, "验算工具：因数个数定理", "360 例：4×3×2 = 24。让学生用程序枚举验证--"
         "数学方法和程序互相印证，这正是评委问「你怎么确认结果对」时最好的回答。这也是客观题第 3 题的考点。")
    code_box(s, 0.6, 1.5, 6.4, 2.8, [
        "360 = 2³ × 3² × 5",
        "",
        "因数个数 = (3+1) × (2+1) × (1+1)",
        "         = 4 × 3 × 2 = 24",
    ], size=17)
    tf = text_box(s, 0.6, 4.6, 12.1, 2.0)
    para(tf, "为什么每个质因子都是「指数 + 1」选法？", 18, True, BLUE, first=True, space_after=8)
    para(tf, "2 的幂选 0~3 次共 4 种，3 的幂选 0~2 次共 3 种，5 的幂选 0~1 次共 2 种，组合起来就是因数个数。", 16, False, INK, space_after=6)

    # ---- 11 练习页与课堂节奏 ----
    s = content_slide(prs, "练习页与课堂节奏", "客观题 6 道覆盖：循环范围、短除法顺序、因数个数定理、双条件筛选、"
         "整除更新、最大质因数。T3 选做的 √n 提示给快的学生。0–8 概念铺垫是零基础关键：手算先行，再上代码。")
    table(s, 0.6, 1.5, 12.1, [
        ["时间", "环节", "做什么"],
        ["0–8", "因数与质数从零讲", "手算 12 与 60；列表三行跟做"],
        ["8–16", "双循环分步精讲", "先内层再外层四步搭；跑 180 和 7"],
        ["16–24", "学生写 T1", "动笔前过格式三查对照卡；盯 //、内层 while、拼接"],
        ["24–31", "学生写 T2", "枚举统计 + 短除法复用；先对数再对格式"],
        ["31–36", "客观题 + T3", "6 道客观题；快的学生做 T3 选做"],
        ["36–40", "收口", "格式三查齐读；布置作业"],
    ], [1.6, 3.0, 7.5], size=16, row_h=0.6)

    # ---- 12 小结与作业 ----
    s = content_slide(prs, "小结与作业", "带走三句：双循环短除法、质数边界 m > 1、格式三查。"
         "作业 1 手算后程序验证，巩固「先手算再机器」。")
    tf = text_box(s, 0.6, 1.4, 6.0, 4.6)
    para(tf, "带走三句", 20, True, BLUE, first=True, space_after=8)
    for t in ("短除法 = 内层反复除 + 外层换下一个", "质数边界：循环后 if m > 1", "格式三查：= 空格 / × 空格 / 末尾干净"):
        para(tf, t, 17, False, INK, space_after=10)
    tf2 = text_box(s, 7.0, 1.4, 5.7, 4.6)
    para(tf2, "作业", 20, True, BLUE, first=True, space_after=8)
    for t in ("1. 手算 84 与 1001 的质因数分解，再用程序验证（84 = 2 × 2 × 3 × 7；1001 = 7 × 11 × 13）", "2. 练习页任务核对：T1、T2 必做，T3 选做"):
        para(tf2, t, 16, False, INK, space_after=10)
    badge(s, 7.0, 5.6, 5.7, 0.5, "分解是地基，下一讲比快慢", CODE_BG, BLUE)

    prs.save(out_path)


# ============================================================
# 第 03 讲课件：双算法效率对比（13 页，评分核心；三版试除逐版详解 + 实验一）
# ============================================================

def build_ppt03(out_path):
    prs = Presentation()
    prs.slide_width = Emu(12192000)  # 标准 16:9 宽（13.333 英寸写法取整有偏差）
    prs.slide_height = Inches(7.5)

    # ---- 1 封面 ----
    s = prs.slides.add_slide(prs.slide_layouts[6])
    slide_bg(s, BLUE)
    tf = text_box(s, 1.0, 2.2, 11.3, 2.2)
    para(tf, "第 03 讲 · 双算法效率对比", 40, True, RGBColor(0xFF, 0xFF, 0xFF), first=True, space_after=10)
    para(tf, "三版试除逐版详解 + 实验一：把「快」变成能得分的证据", 20, False,
         RGBColor(0xCA, 0xDC, 0xFC))
    tf2 = text_box(s, 1.0, 5.9, 11.3, 0.5)
    para(tf2, "配套：练习.html（T1/T2 判质数双算法）· 代码/ 素性检查与实验一脚本 · 数据/ 实验记录表", 14, False,
         RGBColor(0xCA, 0xDC, 0xFC), first=True, space_after=0)
    s.notes_slide.notes_text_frame.text = (
        "开场点题：第 02 讲把分解写对，这一讲开始把「快」变成能得分的证据。本讲只做实验一（单个数三档计时），"
        "把三版试除像上台阶一样一版一版讲透--每一版只改上一版的几行。批处理与埃氏筛整体放在下一讲。"
        "评分表六要点（多组测试、客观记录、控制变量、复杂度、数学原理、结论可信）由第 03、04 两讲合成完整证据链。"
    )

    # ---- 2 评分表拆解 ----
    s = content_slide(prs, "20 分怎么挣：评分表原文拆解", "逐条念原文。强调「客观记录」与「结论可信、数据真实」--"
         "超时也是数据，编造才是事故。本讲做实验一，下一讲做实验二，两讲合成这 20 分的完整证据链。")
    code_box(s, 0.6, 1.5, 12.1, 2.6, [
        "能针对数字进行多组测试，客观记录程序耗时或操作次数；",
        "控制变量对比两种算法的效率差异；",
        "分析时间复杂度和空间复杂度；",
        "总结优化策略及其数学原理，结论可信、数据真实。",
    ], size=18, bg=CODE_BG)
    tf = text_box(s, 0.6, 4.5, 12.1, 1.8)
    para(tf, "两讲分工", 18, True, BLUE, first=True, space_after=8)
    para(tf, "本讲（第 03 讲）：三版试除逐版详解 + 实验一（单个数三档计时）", 17, False, INK, space_after=6)
    para(tf, "下一讲（第 04 讲）：埃氏筛造素数表 + 实验二（一批数批处理）+ 结论句工坊", 17, False, INK, space_after=0)

    # ---- 3 第 1 版：朴素试除 ----
    s = content_slide(prs, "第 1 版 · 朴素试除：全都试一遍", "分步搭：i 从 2 走到 n−1，能整除就不是质数。现场跑 1000003：约 0.09 秒，"
         "看着不慢？算一笔账：判断 10^12 的数要除约 10^12 次，哪怕每次只花百万分之一秒也要按天算。"
         "让学生说结论：快不快是「算法的属性」，不是电脑快慢的问题。", kicker="第 1 版")
    code_box(s, 0.6, 1.5, 6.6, 3.2, [
        "i = 2",
        "not_prime = False",
        "while i < n:          # 从 2 试到 n−1，全都试",
        "    if n % i == 0:    # 能整除 → 找到因子",
        "        not_prime = True",
        "    i = i + 1         # 下一个候选",
    ], size=16)
    tf = text_box(s, 7.4, 1.5, 5.3, 3.2)
    para(tf, "这一版的问题", 17, True, BLUE, first=True, space_after=8)
    para(tf, "很多 i 白试（比到一半就能下结论）", 16, False, INK, space_after=6)
    para(tf, "n 很大时要除约 n 次", 16, False, INK, space_after=6)
    para(tf, "实测 1000003：约 0.09 秒", 16, False, MUT, space_after=6)
    para(tf, "推测 10^12 档：根本除不完", 16, False, WARN, space_after=0)
    badge(s, 0.6, 5.4, 12.1, 0.6, "快不快是算法的属性--这正是评分表「总结优化策略」要你写的东西", CODE_BG, BLUE)

    # ---- 4 图解一：√N 因数成对 ----
    s = content_slide(prs, "图解一：查到 √N 就查完了（因子成对）", "36 的因数全部成对：1×36、2×18、3×12、4×9、6×6，"
         "每对里小的那个都不超过 6 = √36。所以只查 2~6 就能断定 36 没有别的因子--朴素版查到 n、优化版查到 √n，"
         "差距全在这张表上。跟练 48：1×48、2×24、3×16、4×12、6×8，√48≈6.9，查到 6 就够。")
    tf = text_box(s, 0.6, 1.35, 6.4, 4.0)
    para(tf, "36 的因数成对表", 17, True, BLUE, first=True, space_after=8)
    for t in ("36 = 1 × 36", "36 = 2 × 18", "36 = 3 × 12", "36 = 4 × 9", "36 = 6 × 6"):
        para(tf, t, 17, False, INK, font=MONO, space_after=4)
    para(tf, "每对里小的那个 ≤ 6 = √36", 17, True, BLUE, space_after=0)
    code_box(s, 7.2, 1.5, 5.5, 2.2, [
        "朴素试除：查 2 ~ 35（34 个候选）",
        "优化试除：查 2 ~ 6（5 个候选）",
        "",
        "查到 √N 就查完了全部因数对",
    ], size=16)
    badge(s, 7.2, 4.3, 5.5, 0.6, "N = 10^12：约 10^12 次 → 约 10^6 次", RGBColor(0xFD, 0xF5, 0xF4), WARN)
    tf2 = text_box(s, 0.6, 5.8, 12.1, 0.8)
    para(tf2, "跟练：48 的因数对？（1×48、2×24、3×16、4×12、6×8--√48≈6.9，查到 6 就够）", 16, False, MUT, first=True, space_after=0)

    # ---- 5 第 2 版：优化试除（两处改动）----
    s = content_slide(prs, "第 2 版 · 优化试除：只改两处", "一次只改一处。改动 ①：循环条件改 i * i <= n--查到 √n 就查完了（上一页图解）。"
         "改动 ②：先特判 2，再把步长改成 i = i + 2--奇数没有偶数因子（下一页图解）。"
         "现场跑 1000003：约 0.0001 秒，比朴素快约 900 倍。", kicker="第 2 版")
    tf = text_box(s, 0.6, 1.3, 5.9, 0.5)
    para(tf, "第 1 版（慢）", 16, True, MUT, first=True, space_after=0)
    code_box(s, 0.6, 1.8, 5.9, 2.4, [
        "i = 2",
        "while i < n:       # ① 全都试",
        "    if n % i == 0:",
        "        not_prime = True",
        "    i = i + 1      # ② 每次走 1",
    ], size=15)
    tf = text_box(s, 6.8, 1.3, 5.9, 0.5)
    para(tf, "第 2 版（快约 900 倍）", 16, True, OKG, first=True, space_after=0)
    code_box(s, 6.8, 1.8, 5.9, 3.0, [
        "if n % 2 == 0:     # 改动 ②：特判 2",
        "    （偶数里只有 2 是质数）",
        "i = 3",
        "while i * i <= n:  # 改动 ①：只查到 √n",
        "    if n % i == 0:",
        "        not_prime = True",
        "    i = i + 2      # 改动 ②：跳偶",
    ], size=14, bg=RGBColor(0xF2, 0xFB, 0xF6))
    tf2 = text_box(s, 0.6, 5.1, 12.1, 1.6)
    para(tf2, "改动 ① 为什么行？因子成对：每对因子里小的那个 ≤ √n，查到 √n 就查完了全部因数对。", 17, False, INK, first=True, space_after=6)
    para(tf2, "改动 ② 为什么行？特判 2 之后 n 是奇数，奇数没有偶数因子，候选 3, 5, 7, 9 … 直接迈两步。", 17, False, INK, space_after=0)

    # ---- 6 图解二：跳偶 ----
    s = content_slide(prs, "图解二：跳偶--奇数没有偶数因子", "除完 2 之后 n 是奇数。偶数因子（4、6、8、10…）都含有 2，"
         "奇数不可能被它们整除--所以候选 3, 5, 7, 9, 11, … 每次直接 +2。让学生数一数：30 以内这样少试了一半候选。")
    tf = text_box(s, 0.6, 1.35, 12.1, 1.0)
    para(tf, "为什么敢跳过所有偶数？", 18, True, BLUE, first=True, space_after=6)
    para(tf, "特判 2 之后 n 是奇数；偶数因子都含 2，奇数除不尽它们。", 17, False, INK, space_after=0)
    code_box(s, 0.6, 2.5, 12.1, 2.4, [
        "候选（全试）：2, 3, 4, 5, 6, 7, 8, 9, 10, 11, …",
        "候选（跳偶）：3,    5,    7,    9,    11, …",
        "                ↑ 偶数 4, 6, 8, 10 全部跳过，候选少一半",
    ], size=16)
    badge(s, 0.6, 5.3, 12.1, 0.55, "两处改动合起来：查到 √n + 只试奇数 = 优化试除（练习页 T1）", CODE_BG, BLUE)

    # ---- 7 第 3 版：6k±1 试除 ----
    s = content_slide(prs, "第 3 版 · 6k±1：只剩两种位置", "在跳偶基础上再数一步：9, 15, 21 是 3 的倍数、必已被 3 除过--"
         "候选只剩 6k−1 与 6k+1 两种位置（5 和 7、11 和 13…）。特判 2 和 3 之后，每轮查 i 和 i+2 两个位置，然后 i += 6。"
         "易错点：49 = 7 × 7，由 i = 5 时查 i + 2 = 7 抓到；25 = 5 × 5 由第一查抓到--所以一轮必须查两个位置。",
         kicker="第 3 版")
    code_box(s, 0.6, 2.4, 5.9, 2.5, [
        "6k−1 位置：5, 11, 17, 23, …",
        "6k+1 位置：7, 13, 19, 25, …",
        "被跳过：6, 8, 9, 10, 12, …",
        "（全是 2 或 3 的倍数）",
    ], size=15)
    code_box(s, 6.8, 2.4, 5.9, 3.0, [
        "if n % 2 == 0: …   # 特判 2",
        "if n % 3 == 0: …   # 特判 3（新增）",
        "i = 5",
        "while i * i <= n:",
        "    if n % i == 0 or n % (i + 2) == 0:",
        "        not_prime = True",
        "    i = i + 6      # 下一对 6k±1",
    ], size=14, bg=RGBColor(0xF2, 0xFB, 0xF6))
    badge(s, 0.6, 5.9, 12.1, 0.55, "一轮查两个位置，再 +6：候选比跳偶再少约三分之一（练习页 T2）", CODE_BG, BLUE)

    # ---- 8 三版对比与操作次数 ----
    s = content_slide(prs, "三版对比：同一根代码，三条台阶", "带学生从左到右读表：改动越聪明，候选越少。"
         "复杂度「O」读作「阶」，比的是增长速度：N 扩大一万倍，O(√N) 的操作次数只扩大一百倍。"
         "空间复杂度一句带过：三版都是 O(1)；埃氏筛要一张素数表，下一讲讲。")
    table(s, 0.6, 1.5, 12.1, [
        ["版本", "循环到哪", "候选个数（10^12 档）", "时间复杂度", "1000003 实测"],
        ["朴素试除", "2 到 n − 1", "约 5 × 10^11", "O(N)", "约 0.09 秒"],
        ["优化试除", "√n，跳过偶数", "约 5 × 10^5", "O(√N)", "约 0.0001 秒"],
        ["6k±1 试除", "√n，只试 6k±1", "约 3.3 × 10^5", "O(√N / 3)", "<0.0001 秒"],
    ], [2.2, 2.9, 3.2, 2.0, 1.8], size=15, row_h=0.62)
    tf = text_box(s, 0.6, 4.7, 12.1, 1.4)
    para(tf, "每一版只改上一版的几行--这就是报告里「优化策略」的标准写法：改动 + 原因 + 数据。", 18, True, BLUE, first=True, space_after=0)

    # ---- 9 计时三规矩 + 实验一设计 ----
    s = content_slide(prs, "计时三规矩 + 实验一设计", "现场演示跑一次 1000003 朴素版再连跑三次取最小，让学生看见单次计时的抖动。"
         "三个档位全选质数--质数要把候选除满才能下结论，最能拉开版本差距；合数会被中途因子提前打断，差距失真。"
         "先跑 10^6 档建立直觉，再上大档--10^9 起朴素版就要超时了。")
    code_box(s, 0.6, 1.5, 7.2, 2.5, [
        "import time",
        "t0 = time.perf_counter()",
        "... 要计时的代码 ...",
        "dt = time.perf_counter() - t0",
        "print(dt, \"秒\")",
    ], size=16)
    tf = text_box(s, 0.6, 4.2, 7.2, 1.6)
    for t in ("规矩 1：用 perf_counter，不用 time.time()", "规矩 2：重复 3 次，取最小值", "规矩 3：限时 30 秒，超过如实记「超时」"):
        para(tf, t, 16, False, INK, first=(t.startswith("规矩 1")), space_after=6)
    badge(s, 8.2, 1.7, 4.5, 1.4, "超时也是数据\n不是失败", RGBColor(0xFD, 0xF5, 0xF4), WARN)
    tf2 = text_box(s, 8.2, 3.4, 4.5, 2.6)
    para(tf2, "档位（全质数，素性已用脚本验证）：", 16, True, BLUE, first=True, space_after=4)
    para(tf2, "1000003", 16, False, INK, font=MONO, space_after=4)
    para(tf2, "1000000007", 16, False, INK, font=MONO, space_after=4)
    para(tf2, "999999999989", 16, False, INK, font=MONO, space_after=0)

    # ---- 10 实验一实测 ----
    s = content_slide(prs, "实验一实测（教师机参考值，以现场为准）", "数据如实来自 2026-11-10 本机实测。"
         "重点带学生读 10^12 行：朴素超时、优化 0.077 秒--同一任务，一亿倍的操作次数差距。"
         "提醒：机房机器不同，报告里写自己实测的数。", kicker="数据页")
    table(s, 0.6, 1.5, 12.1, [
        ["档位", "朴素试除", "优化试除", "6k±1 试除"],
        ["1000003", "0.0947 秒", "0.0001 秒", "<0.0001 秒"],
        ["1000000007", "超时（>30 秒）", "0.0017 秒", "0.0012 秒"],
        ["999999999989", "超时（>30 秒）", "0.0774 秒", "0.0367 秒"],
    ], [3.1, 3.2, 3.0, 2.8], size=17, row_h=0.62)
    tf = text_box(s, 0.6, 4.4, 12.1, 1.8)
    para(tf, "读数：10^6 档差约 900 倍；10^9 起朴素版出局；10^12 档优化版 0.08 秒完成。", 18, True, BLUE, first=True, space_after=6)
    para(tf, "超时行如实记录--评分表要的就是「客观记录程序耗时」。", 16, False, WARN, space_after=0)

    # ---- 11 练习页任务 ----
    s = content_slide(prs, "练习页任务（T1 / T2）", "T1 优化试除与 T2 6k±1 同输入同输出（1000000007 → yes），"
         "学生亲手体会「同任务双算法」。课堂写 T1，T2 课后；都写对再去跑实验脚本计时。批处理与埃氏筛在下一讲。")
    table(s, 0.6, 1.5, 12.1, [
        ["任务", "做什么", "输入", "预期输出"],
        ["T1 优化试除（必做）", "√n、跳偶判质数（实验一优化版本体）", "1000000007", "yes"],
        ["T2 6k±1 试除（必做）", "同一任务、更少候选", "1000000007", "yes"],
    ], [3.0, 5.4, 2.0, 1.7], size=16, row_h=0.62)
    tf = text_box(s, 0.6, 4.0, 12.1, 1.6)
    para(tf, "课堂节奏：跟打三版 → 课末写 T1 → 课后写 T2 + 实验一记录表。", 18, True, BLUE, first=True, space_after=6)
    para(tf, "预告：分解「一批数」怎么更快？下一讲埃氏筛，先造工具再干活。", 16, False, MUT, space_after=0)

    # ---- 12 40 分钟安排 ----
    s = content_slide(prs, "40 分钟怎么用", "三版详讲是本讲主菜：每版 7–8 分钟，先图解后代码、一次只改一处。"
         "实验一 6 分钟：重点跑 10^6 与 10^12 两档 + 10^9 朴素超时演示。结论句工坊移到第 04 讲，本讲作业先写两句。")
    table(s, 0.6, 1.6, 12.1, [
        ["时间", "环节", "做什么"],
        ["0–4", "提出问题", "评分表六要点；「快」怎么变成证据"],
        ["4–12", "第 1 版朴素试除", "分步搭 + 现场跑 1000003；算一笔「慢」账"],
        ["12–20", "第 2 版优化试除", "√N 图解 + 跳偶图解；两处改动 before / after"],
        ["20–27", "第 3 版 6k±1", "数轴图解 + 双位置检查 + i += 6"],
        ["27–33", "实验一三档实测", "计时三规矩；填记录表实验一部分；超时如实记"],
        ["33–40", "学生写 T1 + 收口", "练习页核对；作业布置（T2 课后）"],
    ], [1.6, 3.0, 7.5], size=16, row_h=0.6)

    # ---- 13 小结与作业 ----
    s = content_slide(prs, "小结与作业", "带走三句齐读。作业 2 让学生课后跑实验一--"
         "每个人手里的数据都是自己测的，第 04 讲写结论句才有底气。")
    tf = text_box(s, 0.6, 1.4, 6.0, 4.6)
    para(tf, "带走三句", 20, True, BLUE, first=True, space_after=8)
    for t in ("三版一条链：查到 √N → 跳过偶数 → 只走 6k±1", "perf_counter，3 次取最小，超时如实记", "结论三要素：条件 + 数据 + 原因"):
        para(tf, t, 17, False, INK, space_after=10)
    tf2 = text_box(s, 7.0, 1.4, 5.7, 4.6)
    para(tf2, "作业", 20, True, BLUE, first=True, space_after=8)
    for t in ("1. 练习页 T1、T2 核对通过", "2. 跑实验一三档并填记录表实验一部分（写一句三要素结论）", "3. 预习思考：分解 2~100000 全部整数，逐个试除要多久？（下一讲埃氏筛）"):
        para(tf2, t, 16, False, INK, space_after=10)
    badge(s, 7.0, 5.6, 5.7, 0.5, "数据真实 > 数据漂亮", CODE_BG, BLUE)

    prs.save(out_path)


# ============================================================
# 第 04 讲课件：埃氏筛与批处理加速（12 页）
# ============================================================

def build_ppt04(out_path):
    prs = Presentation()
    prs.slide_width = Emu(12192000)  # 标准 16:9 宽（13.333 英寸写法取整有偏差）
    prs.slide_height = Inches(7.5)

    # ---- 1 封面 ----
    s = prs.slides.add_slide(prs.slide_layouts[6])
    slide_bg(s, BLUE)
    tf = text_box(s, 1.0, 2.2, 11.3, 2.2)
    para(tf, "第 04 讲 · 埃氏筛与批处理加速", 40, True, RGBColor(0xFF, 0xFF, 0xFF), first=True, space_after=10)
    para(tf, "先造工具再干活--批处理分解快 2~3.5 倍，输出完全一致才算数", 20, False,
         RGBColor(0xCA, 0xDC, 0xFC))
    tf2 = text_box(s, 1.0, 5.9, 11.3, 0.5)
    para(tf2, "配套：练习.html（T1 批处理分解 · T2 筛素数个数）· 代码/ 实验二脚本 · 数据/ 实验记录表（实验二部分）", 14, False,
         RGBColor(0xCA, 0xDC, 0xFC), first=True, space_after=0)
    s.notes_slide.notes_text_frame.text = (
        "开场：上一讲把单个数的快慢比完了，这一讲解决「一批数」。两件事：先造工具（埃氏筛），再加速（只除素数）。"
        "这是评分表 20 分的下半场：探究要成体系、结论要可信。记录表实验一部分上周已填，本讲填实验二部分。"
    )

    # ---- 2 引入：一批数怎么办 ----
    s = content_slide(prs, "引入：一批数怎么办", "任务投影：分解 2 ~ 100000 每个整数的质因数，一行一个。"
         "算一笔账：逐个试除，每个数平均除几十上百次，乘十万个数是千万级除法。"
         "问学生：每个数都在反复除 2、3、5……能不能先把这些「好候选」一次性准备好？")
    code_box(s, 0.6, 1.5, 7.4, 2.4, [
        "任务：输出 2 ~ 100000 每个数的分解式",
        "（每数一行，共 99999 行）",
        "",
        "逐个试除：10 万个数 × 每个数上百次除法",
    ], size=16)
    tf = text_box(s, 0.6, 4.3, 12.1, 1.6)
    para(tf, "观察：不管分解哪个数，试除的候选都是 2, 3, 5, 7, 11……这一串「质数」是重复劳动。", 17, False, INK, first=True, space_after=6)
    para(tf, "能不能先造一张素数表，分解时只除表里的数？", 18, True, BLUE, space_after=0)
    badge(s, 8.2, 1.7, 4.5, 1.4, "先造工具\n再干活", CODE_BG, BLUE)

    # ---- 3 手筛 30 以内 ----
    s = content_slide(prs, "手筛 30 以内（黑板跟着划）", "全班一起划：写 2~30，划掉 2 的倍数，再划掉 3、5 的倍数，"
         "剩下的就是素数（2,3,5,7,11,13,17,19,23,29）。为什么划到 5 就停了？因为 √30≈5.5--和上一讲因子成对是同一个道理。"
         "这 10 个数就是程序要造出来的素数表。")
    tf = text_box(s, 0.6, 1.35, 12.1, 1.0)
    para(tf, "三轮划掉", 18, True, BLUE, first=True, space_after=6)
    para(tf, "第 1 轮划掉 2 的倍数 → 第 2 轮划掉 3 的倍数 → 第 3 轮划掉 5 的倍数", 16, False, INK, space_after=0)
    code_box(s, 0.6, 2.5, 12.1, 2.7, [
        "写：  2  3  4  5  6  7  8  9  10  11  12  13 … 30",
        "划：  4, 6, 8, 10, 12, 14, 16, …, 30     （2 的倍数）",
        "再划：9, 15, 21, 27                      （3 的倍数里没划过的）",
        "再划：25                                 （5 的倍数里没划过的）",
        "剩：  2, 3, 5, 7, 11, 13, 17, 19, 23, 29",
    ], size=15)
    badge(s, 0.6, 5.5, 12.1, 0.55, "先造工具再干活：一张素数表，分解十万个数都只用它", CODE_BG, BLUE)

    # ---- 4 埃氏筛代码分步搭 ----
    s = content_slide(prs, "埃氏筛代码：五步搭出来", "五步对照练习页 T2 starter 的第 1–5 步注释，一一对应。"
         "两个易错点：从 p × p 开始划（更小的倍数早被更小的素数划过）；p = p + 1 在外层缩进（不在 if 里面，否则 p 永远不动）。"
         "筛完 flags[v] 还是 True 的 v 就是质数。")
    code_box(s, 0.6, 1.4, 7.4, 4.6, [
        "flags = [True] * (n + 1)   # 建表：True = 还没被划掉",
        "flags[0] = False",
        "flags[1] = False           # 0 和 1 不是质数",
        "p = 2",
        "while p * p <= n:          # 第 1 步：外层，只筛到 √n",
        "    if flags[p]:           # 第 2 步：p 没被划掉才划",
        "        multiple = p * p   # 第 3 步：从 p×p 划到 n",
        "        while multiple <= n:",
        "            flags[multiple] = False",
        "            multiple = multiple + p",
        "    p = p + 1              # 第 4 步：下一个候选",
        "# 第 5 步：数 2~n 里剩多少 True，就是质数个数",
    ], size=15)
    tf = text_box(s, 8.2, 1.5, 4.5, 4.4)
    para(tf, "两个为什么", 17, True, BLUE, first=True, space_after=8)
    para(tf, "为什么从 p × p 开始？", 16, True, INK, space_after=4)
    para(tf, "p × 2、p × 3 这些更小的倍数，早被 2、3 等更小的素数划过了", 15, False, MUT, space_after=8)
    para(tf, "为什么只筛到 √n？", 16, True, INK, space_after=4)
    para(tf, "和因子成对同理：大素数的倍数必含小于 √n 的素因子", 15, False, MUT, space_after=0)

    # ---- 5 筛完怎么用：方案 A / 方案 B ----
    s = content_slide(prs, "素数表怎么用：先写对，再加速", "方案 A 就是第 02 讲的分解放进循环（练习页 T1，先写对）；"
         "方案 B 只换候选来源--从「2, 3, 4, 5, … 全都试」换成「只除素数表」。30 以内候选从 29 个降到 10 个。"
         "强调流程：先写对 A 并跑通，再换 B 加速，最后比输出。")
    tf = text_box(s, 0.6, 1.3, 5.9, 0.5)
    para(tf, "方案 A · 逐个试除（先写对）", 16, True, MUT, first=True, space_after=0)
    code_box(s, 0.6, 1.8, 5.9, 2.6, [
        "while k < m:",
        "    n = int(input())",
        "    ……第 02 讲短除法分解……",
        "    i = 2",
        "    while i * i <= mm:   # 候选全试",
        "    print(……)",
        "    k = k + 1",
    ], size=14)
    tf = text_box(s, 6.8, 1.3, 5.9, 0.5)
    para(tf, "方案 B · 筛后只除素数（加速版）", 16, True, OKG, first=True, space_after=0)
    code_box(s, 6.8, 1.8, 5.9, 2.6, [
        "primes = 筛出的素数表",
        "while k < m:",
        "    n = int(input())",
        "    ……分解循环……",
        "    for p in primes:     # 只除素数",
        "        if p * p > mm: break",
        "    ……",
    ], size=14, bg=RGBColor(0xF2, 0xFB, 0xF6))
    tf2 = text_box(s, 0.6, 4.8, 12.1, 1.6)
    para(tf2, "30 以内：候选 29 个 → 10 个素数；规模越大省得越多--批处理时优势最大。", 17, False, INK, first=True, space_after=6)
    para(tf2, "实验二脚本（代码/实验二_筛法对比.py）两方案都写好了，课堂上直接跑。", 16, False, MUT, space_after=0)

    # ---- 6 任务 T1：批处理分解 ----
    s = content_slide(prs, "任务 T1 · 批处理分解（先写对）", "T1 参考解 = 第 02 讲 T1 放进 while k < m 循环。"
         "巡视盯三处：读入顺序（先读个数 m，再循环读 n）、质数边界（剩下的 mm > 1 也要 append）、每数一行立刻输出。")
    table(s, 0.6, 1.5, 12.1, [
        ["项目", "内容"],
        ["输入", "第一行个数 m；后面 m 行每行一个整数"],
        ["输出", "每行一个分解式：n = 因子 × 因子 × ……（格式同第 02 讲）"],
        ["样例", "输入 3 / 12 / 97 / 100 → 三行分解式"],
    ], [2.0, 10.1], size=17, row_h=0.62)
    tf = text_box(s, 0.6, 4.4, 12.1, 1.6)
    para(tf, "常见错：忘了质数边界（97 输出成空）、几行攒到最后一起 print、读入顺序乱。", 17, False, WARN, first=True, space_after=0)

    # ---- 7 输出一致性护栏 ----
    s = content_slide(prs, "护栏：两方案输出必须逐行一致", "实验二的采信标准：方案 A 与方案 B 的输出逐行比对完全一致，"
         "提速数据才可信。不一致 = 有一个方案写错了，先修算法再谈提速。"
         "把「输出完全一致」写进记录表--这就是评分表「结论可信、数据真实」的直接证据。", kicker="得分点")
    code_box(s, 0.6, 1.5, 5.9, 2.6, [
        "× 输出不一致就报提速倍数",
        "",
        "× 「方案 B 是书上的，肯定对」",
        "",
        "× 只比总行数，不逐行比对",
    ], size=16, color=WARN)
    code_box(s, 6.8, 1.5, 5.9, 2.6, [
        "√ 脚本自动逐行比对",
        "",
        "√ 完全一致（99999 行）才计时",
        "",
        "√ 「输出一致」写进结论句",
    ], size=16, color=OKG, bg=RGBColor(0xF2, 0xFB, 0xF6))
    tf = text_box(s, 0.6, 4.6, 12.1, 1.2)
    para(tf, "提速不牺牲正确性--这句话有证据，评委才认。", 19, True, BLUE, first=True, space_after=0)

    # ---- 8 实验二实测 ----
    s = content_slide(prs, "实验二实测（教师机参考值，以现场为准）", "N 默认 100000，约 1 秒完成；机房快可改 1000000 看大档。"
         "提速口径统一说「约 2~3.5 倍」：100000 档约 2.3 倍、1000000 档约 3.4 倍，量级随批大小上升。"
         "数据如实来自本机实测，报告里写自己测的数。", kicker="数据页")
    table(s, 0.6, 1.5, 12.1, [
        ["N", "方案 A 逐个试除", "方案 B 筛后只除素数", "提速", "输出比对"],
        ["100000", "0.605 秒", "0.259 秒", "约 2.3 倍", "99999 行完全一致"],
        ["1000000", "15.7 秒", "4.6 秒", "约 3.4 倍", "999999 行完全一致"],
    ], [1.9, 2.6, 3.0, 1.7, 2.9], size=16, row_h=0.62)
    tf = text_box(s, 0.6, 3.9, 12.1, 2.2)
    para(tf, "埃氏筛为什么值得？", 18, True, BLUE, first=True, space_after=8)
    para(tf, "一次建表（快），处处复用（分解 10 万个数只除素数）；合数被筛掉，除法次数少一半以上。", 17, False, INK, space_after=6)
    para(tf, "提速不牺牲正确性--输出完全一致就是证据。", 17, False, OKG, space_after=0)

    # ---- 9 结论句工坊 ----
    s = content_slide(prs, "结论句工坊：两个实验各写一句", "三要素模板：条件 + 数据 + 原因。学生按模板把实验一、实验二各写一句，"
         "同桌互查三要素是否齐全。写得好的结论句直接搬进报告第 4、5 页--数据和原理在报告里是硬通货。", kicker="得分点")
    code_box(s, 0.6, 1.5, 12.1, 1.6, [
        "模板：在 ___（条件）上，___ 版耗时 ___ 秒，___ 版耗时 ___ 秒，快约 ___ 倍；",
        "      原因是操作次数从约 ___ 降到约 ___（或：只除素数、候选少一半以上）。",
    ], size=15)
    code_box(s, 0.6, 3.3, 5.9, 2.6, [
        "√ 实验一示例：在 10^12 档位，",
        "  优化试除 0.077 秒出结果，朴素",
        "  试除超 30 秒未出结果；原因是操",
        "  作次数从约 5×10^11 降到约 10^6。",
    ], size=14, color=OKG, bg=RGBColor(0xF2, 0xFB, 0xF6))
    code_box(s, 6.8, 3.3, 5.9, 2.6, [
        "√ 实验二示例：在分解 2~100000",
        "  的批处理中，方案 B 0.259 秒、方",
        "  案 A 0.605 秒，快约 2.3 倍；原因",
        "  是只除素数，且输出完全一致。",
    ], size=14, color=OKG, bg=RGBColor(0xF2, 0xFB, 0xF6))

    # ---- 10 练习页任务 ----
    s = content_slide(prs, "练习页任务（T1 / T2）", "T1 批处理分解是「先写对」的本体，必做；T2 筛素数个数是埃氏筛本体，必做。"
        "两个都核对通过后，实验二的加速才轮得到你。")
    table(s, 0.6, 1.5, 12.1, [
        ["任务", "做什么", "输入", "预期输出"],
        ["T1 批处理分解（必做）", "m 个数逐个输出分解式（第 02 讲模板）", "3 / 12 / 97 / 100", "三行分解式"],
        ["T2 筛素数个数（必做）", "埃氏筛五步，输出 n 以内质数个数", "30", "10"],
    ], [3.4, 4.8, 2.2, 1.7], size=16, row_h=0.62)
    tf = text_box(s, 0.6, 3.9, 12.1, 1.6)
    para(tf, "课堂节奏：手筛 → 五步跟搭 → 课内写 T1 → 实验二 → 课内/课后写 T2。", 18, True, BLUE, first=True, space_after=6)
    para(tf, "下一讲：把三讲的成果讲给评委听--报告框架与全真模拟。", 16, False, MUT, space_after=0)

    # ---- 11 40 分钟安排 ----
    s = content_slide(prs, "40 分钟怎么用", "记录表实验一部分上周已填，本讲填实验二部分。"
         "结论句工坊 7 分钟包含同桌互查--这 20 分的一半在结论句上。T2 课内来不及就课后，实验脚本必须全班当场跑一遍。")
    table(s, 0.6, 1.6, 12.1, [
        ["时间", "环节", "做什么"],
        ["0–4", "引入", "批处理任务 + 一笔账；「先造工具」"],
        ["4–12", "手筛 30 + 五步搭", "黑板跟划；代码五步对照练习页 T2"],
        ["12–20", "先写对：T1 批处理", "第 02 讲模板放进循环；巡视三处"],
        ["20–27", "再加速：方案 B", "只除素数；A / B 对比"],
        ["27–33", "实验二实测", "全班跑脚本；输出逐行一致才采信；填记录表"],
        ["33–40", "结论句工坊 + T2", "两个实验各写一句三要素；T2 核对；作业"],
    ], [1.6, 3.0, 7.5], size=16, row_h=0.6)

    # ---- 12 小结与作业 ----
    s = content_slide(prs, "小结与作业", "带走三句齐读。作业 2 的实验数据下节课直接进报告--"
        "第 05 讲教怎么把三讲的成果讲给评委听。")
    tf = text_box(s, 0.6, 1.4, 6.0, 4.6)
    para(tf, "带走三句", 20, True, BLUE, first=True, space_after=8)
    for t in ("先造工具再干活：素数表一次建、处处用", "两方案输出一致，提速才可信", "先写对，再加速"):
        para(tf, t, 17, False, INK, space_after=10)
    tf2 = text_box(s, 7.0, 1.4, 5.7, 4.6)
    para(tf2, "作业", 20, True, BLUE, first=True, space_after=8)
    for t in ("1. 练习页 T1、T2 核对通过", "2. 跑实验二并填记录表实验二部分（写一句三要素结论）", "3. 预习：翻一遍第 05 讲数据/ 里的六页框架与陈述骨架"):
        para(tf2, t, 16, False, INK, space_after=10)
    badge(s, 7.0, 5.6, 5.7, 0.5, "下一讲：把会做的变成会讲的", CODE_BG, BLUE)

    prs.save(out_path)


# ============================================================
# 第 05 讲课件：报告与全真模拟（11 页）
# ============================================================

def build_ppt05(out_path):
    prs = Presentation()
    prs.slide_width = Emu(12192000)  # 标准 16:9 宽（13.333 英寸写法取整有偏差）
    prs.slide_height = Inches(7.5)

    # ---- 1 封面 ----
    s = prs.slides.add_slide(prs.slide_layouts[6])
    slide_bg(s, BLUE)
    tf = text_box(s, 1.0, 2.2, 11.3, 2.2)
    para(tf, "第 05 讲 · 报告与全真模拟", 40, True, RGBColor(0xFF, 0xFF, 0xFF), first=True, space_after=10)
    para(tf, "项目理解 10 + 问题描述 10 + 报告 20 + 分享 5 -- 四项 45 分，比算法本身还多", 20, False,
         RGBColor(0xCA, 0xDC, 0xFC))
    tf2 = text_box(s, 1.0, 5.9, 11.3, 0.5)
    para(tf2, "配套：数据/ 六页框架 · 流程图规范 · 陈述骨架 · 全真模拟卷 · 自评清单", 14, False,
         RGBColor(0xCA, 0xDC, 0xFC), first=True, space_after=0)
    s.notes_slide.notes_text_frame.text = (
        "开场算账：项目理解 10 + 问题描述 10 + 报告 20 + 分享 5 = 45 分，"
        "算法相关只有 35 分。今天这讲是「把会做的变成会讲的」。"
    )

    # ---- 2 分值算账 ----
    s = content_slide(prs, "把报告当第二道编程题", "投影评分表七项，把 45 分圈出来。"
         "学生们容易把 95% 精力放在写码、5% 留给报告--比例反了。"
         "报告的六要素评分表原文里写得明明白白，逐条照做就是得分。")
    table(s, 0.6, 1.5, 12.1, [
        ["评分项", "分值", "哪讲练的"],
        ["项目理解 + 问题描述", "10 + 10", "第 05 讲（六页框架 + 流程图）"],
        ["数字分解与处理", "15", "第 02 讲"],
        ["算法设计与实现", "20", "第 02 + 03 讲"],
        ["算法效率探究与优化", "20", "第 03 + 04 讲"],
        ["项目分析报告 + 现场分享", "20 + 5", "第 05 讲（六页框架 + 陈述演练）"],
    ], [4.5, 2.6, 5.0], size=16, row_h=0.6)
    badge(s, 0.6, 6.0, 6.0, 0.5, "报告相关 45 分 vs 算法 35 分", RGBColor(0xFD, 0xF5, 0xF4), WARN)

    # ---- 3 六页框架 ----
    s = content_slide(prs, "PPT 六页框架（评分 20 分原文六要素）", "逐页念「放什么/忌什么」。"
         "强调评分原文：设计思路、算法原理、运行结果、效率对比、优化策略和创新点--六页正好一一对应，"
         "评委按条找分，框架就是给评委的寻宝图。")
    table(s, 0.6, 1.4, 12.1, [
        ["页", "放什么", "忌"],
        ["1 问题理解", "题目一句话 + 输入/输出/范围/边界四要素", "整段抄题"],
        ["2 算法原理", "因子成对原理 + 流程图 1 张", "贴大段代码"],
        ["3 实验设计", "档位表 + 为什么选质数 + 计时方法", "只写「测了几次」"],
        ["4 数据与对比", "实测表 + 对比图 + 提速倍数大字", "表格不解读"],
        ["5 优化与原理", "O(N)→O(√N) + 三条数学原理", "只说「优化了」"],
        ["6 创新与反思", "自己的做法 + 试除法的真实边界", "吹「完美解决」"],
    ], [2.2, 6.6, 3.3], size=15, row_h=0.56)
    tf = text_box(s, 0.6, 6.0, 12.1, 0.8)
    para(tf, "每页三检查：有图表吗？有加粗结论吗？数字是自己实测的吗？", 17, True, BLUE, first=True, space_after=0)

    # ---- 4 流程图规范 ----
    s = content_slide(prs, "流程图四符号（问题描述 10 分）", "示例图是「优化试除判质数」。课堂实训：学生草稿纸照画，"
         "同桌互查四个要点--是/否标注、平行四边形、回跳箭头、图码一致。图码一致是「算法设计与实现」的加分点。", kicker="课堂实训 8 分钟")
    table(s, 0.6, 1.5, 4.9, [
        ["符号", "形状", "用于"],
        ["起止框", "圆角矩形", "开始 / 结束"],
        ["输入输出框", "平行四边形", "输入 n / 输出 yes"],
        ["判断框", "菱形", "n % i == 0 ?（标是 / 否）"],
        ["处理框", "矩形", "m = m // i"],
    ], [1.4, 1.8, 1.7], size=14, row_h=0.6)
    code_box(s, 5.8, 1.5, 6.9, 4.3, [
        "(开始) → [输入 n]",
        "  ↓",
        "<n==2?> 是→ [输出 yes] → (结束)",
        "  ↓否",
        "<偶数且n>2?> 是→ [输出 no] → (结束)",
        "  ↓否        [i = 3]",
        "  ↓          ↙循环↖",
        "<i×i<=n?> 否→ [输出 yes] → (结束)",
        "  ↓是",
        "<n%i==0?> 是→ [输出 no] → (结束)",
        "  ↓否   [i = i + 2] → 回循环",
    ], size=15)
    tf = text_box(s, 0.6, 6.0, 12.1, 0.8)
    para(tf, "互查四要点：是 / 否标了吗？▱ 用了吗？回跳箭头在吗？图码一致吗？", 17, True, BLUE, first=True, space_after=0)

    # ---- 5 陈述时间轴 ----
    s = content_slide(prs, "5 分钟陈述时间轴（分享 5 分）", "两人都要讲--现场评委可能任指一人答问。"
         "超时自断示范一次：讲到 4:30 直接跳收尾，评委反而给时间控制分。")
    table(s, 0.6, 1.5, 12.1, [
        ["时间", "段落", "一句话模板"],
        ["0:00–0:30", "开场", "我们的任务是____，用____思路，主算法是____"],
        ["0:30–2:00", "算法讲解", "选试除法是因为____；关键一步是____"],
        ["2:00–3:30", "数据展示", "同机同数字下，优化版 __ 秒，朴素版 __，快约 __ 倍"],
        ["3:30–4:30", "优化原理", "操作次数 O(N) 降到 O(√N)，数学依据是____"],
        ["4:30–5:00", "收尾", "创新点____；____ 以上会吃力，下一步想突破"],
    ], [2.0, 1.8, 8.3], size=16, row_h=0.6)
    tf = text_box(s, 0.6, 5.0, 12.1, 1.4)
    for t in ("三纪律：每页一句话主线 ｜ 核心倍数最多强调两遍 ｜ 4:30 自断跳收尾",):
        para(tf, t, 18, True, WARN, first=True, space_after=0)

    # ---- 6 评委问答预案 ----
    s = content_slide(prs, "评委问答 6 预案", "角色扮演 2 分钟：教师扮评委抽 2 题问。"
         "答题公式：先答结论 → 再给依据（数字/原理）→ 有边界就诚实说边界。")
    table(s, 0.6, 1.4, 12.1, [
        ["评委问", "答题要点"],
        ["为什么埃氏筛更快？", "建一次表处处复用；只除素数；输出一致，提速不牺牲正确性"],
        ["测试数字怎么选的？", "全质数 + 三档量级跳跃 + 脚本验证素性"],
        ["O(√N) 什么意思？", "耗时随 N 开平方增长；N 大 1 万倍，操作次数只大 100 倍"],
        ["还能再优化吗？", "诚实：已有优化的原理与量级；更高阶方法超出中学范围，想继续学"],
        ["边界情况怎么处理？", "质数剩 m 本身 / n=2 / 偶数快速通道 / 重复因子反复除"],
        ["两人怎么分工？", "如实：一人主码一人记录，都参与验证"],
    ], [3.2, 8.9], size=15, row_h=0.6)

    # ---- 7 全真模拟卷 ----
    s = content_slide(prs, "全真模拟 · 120 分钟怎么分", "模拟卷三任务对准官方三环节。开场 10 分钟不写代码--"
         "先写问题理解和流程图。收尾 10 分钟自评 + 预演陈述。强调：记录表必须提交，超时如实记。", kicker="课后作业")
    table(s, 0.6, 1.5, 12.1, [
        ["时间段", "做什么", "产出"],
        ["0–10", "读题 + 问题理解 + 流程图", "草稿：六要素 + 1 张图"],
        ["10–45", "任务一：数字分解与处理", "任务一.py（格式逐字符照抄）"],
        ["45–80", "任务二：算法效率探究", "双算法 + 记录表.md"],
        ["80–110", "任务三：报告 PPT 六页", "报告.pptx（数字用实测）"],
        ["110–120", "自评清单核对 + 预演陈述", "「否」项清单"],
    ], [1.8, 5.0, 5.3], size=16, row_h=0.6)

    # ---- 8 数据真实铁律 ----
    s = content_slide(prs, "铁律：数据真实 > 数据漂亮", "这页是价值观页，讲 1 分钟但要严肃："
         "编一个数字被评委看出，整份报告作废；如实写超时、如实写边界，评委反而给「结论可信」分。"
         "这也是为什么全部参考耗时都是「教师机实测、以现场为准」。", kicker="底线")
    code_box(s, 0.6, 1.6, 5.9, 2.6, [
        "× 「优化后快了 10000 倍！」",
        "  （没有数据支撑）",
        "",
        "× 报告数字和记录表对不上",
        "  （事后补写的痕迹）",
    ], size=16, color=WARN)
    code_box(s, 6.8, 1.6, 5.9, 2.6, [
        "√ 朴素版超时如实记「>30 秒」",
        "",
        "√ 提速写「约 2.3 倍」并附",
        "  两方案输出完全一致的证据",
    ], size=16, color=OKG, bg=RGBColor(0xF2, 0xFB, 0xF6))
    tf = text_box(s, 0.6, 4.6, 12.1, 1.2)
    para(tf, "报告里的每一个数，都必须能在记录表里找到。", 19, True, BLUE, first=True, space_after=0)

    # ---- 9 练习页任务 ----
    s = content_slide(prs, "练习页任务与作业", "T1 综合自检串起第 02 讲分解 + 因数个数：360 的分解式与 24 个因数。"
         "作业三件事：T1 通过、120 分钟模拟、正式版 PPT。下节课陈述 + 教师扮评委。")
    table(s, 0.6, 1.5, 12.1, [
        ["任务", "做什么", "输入", "预期输出"],
        ["T1 综合自检", "分解式一行 + 因数个数一行", "360", "360 = 2 × 2 × 2 × 3 × 3 × 5 与 24"],
    ], [2.4, 4.6, 1.6, 3.5], size=16, row_h=0.66)
    tf = text_box(s, 0.6, 3.4, 12.1, 2.6)
    para(tf, "作业", 18, True, BLUE, first=True, space_after=8)
    for t in ("1. T1 综合自检核对通过", "2. 完成 120 分钟全真模拟（打印模拟卷），自评清单逐项打勾", "3. 两人把模拟 PPT 做成正式版，下节课 5 分钟陈述 + 评委抽问"):
        para(tf, t, 17, False, INK, space_after=8)

    # ---- 10 40 分钟安排 ----
    s = content_slide(prs, "40 分钟怎么用", "陈述演练要留足 12 分钟。流程图互查环节重点抓「图码一致」。"
         "模拟卷发放环节把三任务时间分配讲清，别让学生回家才想起来没打印。")
    table(s, 0.6, 1.6, 12.1, [
        ["时间", "环节", "做什么"],
        ["0–5", "分值算账", "45 分 vs 35 分；「报告是第二道编程题」"],
        ["5–13", "六页框架", "逐页放什么/忌什么；每页三检查"],
        ["13–21", "流程图实训", "照示例画优化试除；同桌互查四要点"],
        ["21–33", "陈述演练", "两人一组 5 分钟计时；超时自断；抽组演示"],
        ["33–40", "模拟卷发放", "三任务 + 时间分配 + 自评清单用法"],
    ], [1.6, 2.4, 8.1], size=16, row_h=0.6)

    # ---- 11 小结 ----
    s = content_slide(prs, "小结：把会做的变成会讲的", "收官页。五讲串一条线：01 语法地基 → 02 分解写对 → "
         "03 三版比快慢 → 04 筛法批处理 → 05 讲清价值。提醒材料清单都在 数据/，比赛前一天全部重走一遍。")
    tf = text_box(s, 0.6, 1.4, 6.6, 4.6)
    para(tf, "五讲一条线", 20, True, BLUE, first=True, space_after=8)
    for t in ("01 语法地基（Python 六大句型）", "02 分解写对（格式规范）", "03 三版试除（控制变量）", "04 筛法批处理（先造工具）", "05 讲清价值（六页框架 + 陈述）"):
        para(tf, t, 17, False, INK, space_after=8)
    tf2 = text_box(s, 7.6, 1.4, 5.1, 4.6)
    para(tf2, "带进考场的三句话", 20, True, BLUE, first=True, space_after=8)
    for t in ("先写问题理解再动手", "每个数都是实测的", "超时和边界都如实写"):
        para(tf2, t, 17, False, INK, space_after=10)
    badge(s, 7.6, 5.4, 5.1, 0.6, "六页框架 + 记录表 + 自评清单，全在 数据/", CODE_BG, BLUE)

    prs.save(out_path)


# ============================================================
# 入口
# ============================================================

BUILDERS = {"01": build_ppt01, "02": build_ppt02, "03": build_ppt03, "04": build_ppt04, "05": build_ppt05}
DIRNAMES = {
    "01": "第01讲_Python基础速通",
    "02": "第02讲_因数分解实战",
    "03": "第03讲_双算法效率对比",
    "04": "第04讲_埃氏筛与批处理加速",
    "05": "第05讲_报告与全真模拟",
}


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    targets = list(BUILDERS) if which == "all" else [which]
    for nn in targets:
        out = COURSE_ROOT / DIRNAMES[nn] / "课件.pptx"
        BUILDERS[nn](out)
        print(f"生成 {out.relative_to(COURSE_ROOT.parent)}（{len(out.read_bytes())} 字节）")
    return 0


if __name__ == "__main__":
    sys.exit(main())

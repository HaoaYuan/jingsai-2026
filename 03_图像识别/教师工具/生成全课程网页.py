#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成全课程网页.py -- 将《图像识别》全部 16 讲 + 六天冲刺 + 题库 + 拓展汇总为单文件离线 HTML。

输出：Python基础/图像识别全课程.html
特性：
- 零外部请求、ES2017 兼容 JS、localStorage 独立键名 py_all_course_v1
- 补齐第 03 讲、第 04 讲交互客观题与程序任务
- 仅提取学生可见内容（教案中的目标/板书/常见错误、demo*.py、task*.py），绝不纳入 answer*.py 或教案参考答案
"""

import json
import pathlib
import re
import subprocess
import sys
from html import escape as html_escape

TRACK_ROOT = pathlib.Path(__file__).resolve().parent.parent  # 03_图像识别/
ROOT = TRACK_ROOT / "系统课程16讲"
REPO = TRACK_ROOT.parent                                     # 仓库根
OUT_HTML = TRACK_ROOT / "图像识别全课程.html"

LESSON_DIRS = [
    ("01", "第01讲_你好Python", "第 1 周 · 初识 IDLE 与 print"),
    ("02", "第02讲_图形变成数据", "第 1 周 · 变量、字符串与索引"),
    ("03", "第03讲_程序会算术", "第 1 周 · // 整除与 % 取余"),
    ("04", "第04讲_小数之谜", "第 2 周 · 浮点数误差与对策"),
    ("05", "第05讲_控制结构入门", "第 2 周 · 分支/循环/逻辑运算认脸"),
    ("06", "第06讲_让程序判断", "第 2 周 · if/elif/else 与规则分类"),
    ("07", "第07讲_逐个检查像素", "第 3 周 · for 循环与计数"),
    ("07s", "第07讲补充_边数边判", "第 3 周 · 循环记录与对称判别"),
    ("08", "第08讲_从一行到整幅图", "第 3 周 · 二维列表与嵌套循环"),
    ("09", "第09讲_读取比赛文件", "第 3 周 · open/strip 读取 100×100"),
    ("10", "第10讲_把步骤变成函数", "第 4 周 · def/参数/return"),
    ("11", "第11讲_寻找形状特征", "第 4 周 · 外接框/填充率/行宽"),
    ("12", "第12讲_建立识别规则", "第 4 周 · 规则组合与 36 变体测试"),
    ("13", "第13讲_整合与调试", "第 5 周 · 完整流程与模板输出"),
    ("14", "第14讲_独立编写与答辩", "第 5 周 · 脱稿编写与答辩流程图"),
    ("15", "第15讲_模拟赛与复盘", "第 5 周 · 40 分钟模拟与评分复盘"),
]

# 第 03 讲与第 04 讲无独立练习.html，从其教案.md + 课件.pptx 原题与代码/task*.py 补全
EXTRA_LESSONS = {
    "03": {
        "questions": [
            {
                "id": 1, "tag": "运算符",
                "stem": "Python 的乘法和除法，用的是哪一组符号？",
                "options": ["× ÷", "* /", "** //", "＋ －"],
                "answer": "B",
                "explain": "乘是 *，除是 /；÷ 和 × 不是 Python 符号，中文输入法下容易打错。"
            },
            {
                "id": 2, "tag": "除法规则",
                "stem": "<code>print(7 / 2)</code> 的输出是什么？",
                "options": ["3", "3.5", "3 余 1", "4"],
                "answer": "B",
                "explain": "/ 的结果一律带小数，7 / 2 = 3.5（即使 10 / 2 也会得到 5.0）。"
            },
            {
                "id": 3, "tag": "整除 //",
                "stem": "<code>print(17 // 5)</code> 的输出是什么？",
                "options": ["3.4", "3", "2", "4"],
                "answer": "B",
                "explain": "// 只留整数商：5 × 3 = 15 摆满 3 行，砍掉余数 2，所以是 3。"
            },
            {
                "id": 4, "tag": "取余 %",
                "stem": "<code>print(17 % 5)</code> 的输出是什么？",
                "options": ["3", "2", "3.4", "5"],
                "answer": "B",
                "explain": "% 只留余数：17 - 15 = 2，所以是 2。"
            },
            {
                "id": 5, "tag": "奇偶判断",
                "stem": "想知道一个整数 <code>n</code> 是奇数还是偶数，用哪个式子？",
                "options": ["n / 2", "n // 2", "n % 2", "n * 2"],
                "answer": "C",
                "explain": "n % 2 余 0 是偶数、余 1 是奇数；其余三个式子得不到「余几」。"
            },
            {
                "id": 6, "tag": "行列换算",
                "stem": "一行 10 个像素，索引 27 的像素在第几行（行号从 0 开始数）？",
                "options": ["2", "3", "27", "7"],
                "answer": "A",
                "explain": "27 // 10 = 2，索引从 0 数，所以是第 2 行（第 7 列：27 % 10 = 7）。"
            },
        ],
        "tasks": [
            {
                "id": "t1", "level": "基础", "title": "任务 1 · 分像素", "file": "01_分像素.py",
                "brief": "23 个像素每行摆 6 个，计算能摆满几行、还剩几个。",
                "requirements": ["用 // 算出摆满几行存进 rows；", "用 % 算出剩下几个存进 left；", "最后用 print(rows, left) 输出。"],
                "expected": "3 5",
                "hints": ["商是 //，余数是 %。", "rows = 23 // 6，left = 23 % 6。", "最后一行写 print(rows, left)。"],
                "starter": "# 任务 1：分像素\n# 23 个像素，每行摆 6 个\n# 把「摆满几行」存进 rows，「剩下几个」存进 left\n# 再用 print(rows, left) 一起输出，预期：3 5\n",
            },
            {
                "id": "t2", "level": "基础", "title": "任务 2 · 找位置", "file": "02_找位置.py",
                "brief": "一行摆 10 个像素，索引 27 在第几行、第几列（都从 0 数）？",
                "requirements": ["第一行输出第几行；", "第二行输出第几列。"],
                "expected": "2\n7",
                "hints": ["摆满几行就是行号（整除 10）。", "剩下几个就是列号（对 10 取余）。", "print(n // 10) 和 print(n % 10)。"],
                "starter": "# 任务 2：找位置\n# 一行摆 10 个像素，索引 27 在第几行、第几列？（都从 0 数）\nn = 27\n# 补两行 print(n □ 10)：一行算第几行，一行算第几列\n",
            },
            {
                "id": "t3", "level": "选做", "title": "任务 3 · 奇偶观察（选做）", "file": "03_奇偶观察.py",
                "brief": "运行观察 0、1、7、8、100 对 2 取余的结果，总结奇偶规律。",
                "requirements": ["按 F5 运行查看 5 行输出；", "总结余 0 与余 1 分别对应什么数。"],
                "expected": "0\n1\n1\n0\n0",
                "hints": ["直接运行代码查看输出。", "偶数除以 2 余 0，奇数除以 2 余 1。", "以后判断偶数都用 n % 2 == 0。"],
                "starter": "print(0 % 2)\nprint(1 % 2)\nprint(7 % 2)\nprint(8 % 2)\nprint(100 % 2)\n",
            },
        ],
    },
    "04": {
        "questions": [
            {
                "id": 1, "tag": "浮点误差",
                "stem": "<code>print(0.1 + 0.2)</code> 的实际输出是什么？",
                "options": ["0.3", "0.30000000000000004", "0.31", "报错"],
                "answer": "B",
                "explain": "0.1 和 0.2 在二进制中无限循环，只能存近似值，相加后误差露馅输出 0.30000000000000004。"
            },
            {
                "id": 2, "tag": "误差原理",
                "stem": "<code>0.1 + 0.2</code> 不等于 <code>0.3</code>，根本原因是什么？",
                "options": ["Python 有 bug", "0.1 在二进制里写不完，只能存最接近的数", "电脑坏了", "数字太大"],
                "answer": "B",
                "explain": "二进制小数位是 0.5、0.25、0.125… 凑不出精确的 0.1，只能存最接近的近似数；全世界的语言都一样。"
            },
            {
                "id": 3, "tag": "精确存储",
                "stem": "下面哪个数，计算机用二进制能精确存储？",
                "options": ["0.5", "0.1", "0.2", "0.3"],
                "answer": "A",
                "explain": "0.5 恰好是二进制小数第一位「一半」（1/2），能精确表示；0.1、0.2、0.3 都写不完。"
            },
            {
                "id": 4, "tag": "二分之一系",
                "stem": "<code>print(0.5 + 0.25)</code> 的输出是什么？",
                "options": ["0.75", "0.7", "带一串长尾巴", "报错"],
                "answer": "A",
                "explain": "0.5 和 0.25 都能精确表示，相加得干净精确的 0.75。"
            },
            {
                "id": 5, "tag": "比较对策",
                "stem": "判断浮点数 <code>a</code> 和 <code>0.3</code>「足够接近」的正确写法是？",
                "options": ["a == 0.3", "abs(a - 0.3) < 0.0001", "round(a)", "a > 0.3"],
                "answer": "B",
                "explain": "浮点数不能直接用 == 比相等，要判断差值的绝对值 abs(a - b) 是否小于很小的阈值。"
            },
            {
                "id": 6, "tag": "显示对策",
                "stem": "<code>print(round(0.1 + 0.2, 2))</code> 的输出是什么？",
                "options": ["0.3", "0.30000000000000004", "0.30", "报错"],
                "answer": "A",
                "explain": "round(..., 2) 四舍五入到 2 位小数用于美化显示，输出 0.3（不补尾零）。"
            },
        ],
        "tasks": [
            {
                "id": "t1", "level": "基础", "title": "任务 1 · 见一见误差", "file": "01_见一见误差.py",
                "brief": "分别打印 0.1 + 0.2、0.1 + 0.7、0.5 + 0.25，对比哪两个带尾巴、哪个精确。",
                "requirements": ["写三行 print 依次输出 0.1 + 0.2、0.1 + 0.7、0.5 + 0.25；", "不要修改或脑补输出。"],
                "expected": "0.30000000000000004\n0.7999999999999999\n0.75",
                "hints": ["直接写三条 print(...) 语句。", "前两个会带一长串小数尾巴，最后一个是干净的 0.75。", "print(0.1 + 0.2) / print(0.1 + 0.7) / print(0.5 + 0.25)"],
                "starter": "# 任务 1：见一见误差\n# 补全三行 print 并运行，观察输出\n",
            },
            {
                "id": "t2", "level": "基础", "title": "任务 2 · 改对比较", "file": "02_改对比较.py",
                "brief": "把永远不成立的 a == 0.3 改成差值比较，让程序输出「差不多，算相等」。",
                "requirements": ["使用 abs(a - 0.3) < 0.0001 替代 ==；", "成功输出「差不多，算相等」。"],
                "expected": "差不多，算相等",
                "hints": ["浮点数不能用 == 直接判相等。", "判断两个数差值的绝对值是否小于 0.0001。", "if abs(a - 0.3) < 0.0001:"],
                "starter": "a = 0.1 + 0.2\nif a == 0.3:\n    print(\"差不多，算相等\")\n",
            },
            {
                "id": "t3", "level": "选做", "title": "任务 3 · 别迷信 round（选做）", "file": "03_别迷信round.py",
                "brief": "运行 print(round(2.675, 2))，观察它是不是 2.68。",
                "requirements": ["按 F5 运行，看清实际输出 2.67。"],
                "expected": "2.67",
                "hints": ["2.675 存进二进制时也略微偏小。", "所以四舍五入后反而变成 2.67。", "直接运行即可看到结果。"],
                "starter": "print(round(2.675, 2))\n",
            },
        ],
    },
}


def extract_safe_plan_sections(plan_path):
    """只从教案.md提取学生可看部分（教学目标、重点与难点、板书设计、常见错误与纠正），绝不提取参考答案。"""
    if not plan_path.exists():
        return {}
    txt = plan_path.read_text(encoding="utf-8")
    sections = {}
    parts = re.split(r"(?m)^##\s+", txt)
    for part in parts[1:]:
        lines = part.splitlines()
        heading = lines[0].strip()
        body = "\n".join(lines[1:]).strip()
        if heading in ("教学目标", "重点与难点", "板书设计", "常见错误与纠正"):
            sections[heading] = body
    return sections


def parse_js_vars_via_node(html_text):
    """用 node 提取 练习.html 里的 QUESTIONS 和 TASKS（兼容第01讲非标准JSON对象字面量）。"""
    mq = re.search(r"var\s+QUESTIONS\s*=\s*(\[.*?\]);", html_text, re.S)
    mt = re.search(r"var\s+TASKS\s*=\s*(\[.*?\]);", html_text, re.S)
    q_raw = mq.group(1) if mq else "[]"
    t_raw = mt.group(1) if mt else "[]"
    try:
        return json.loads(q_raw), json.loads(t_raw)
    except Exception:
        js = f"const QUESTIONS = {q_raw};\nconst TASKS = {t_raw};\nconsole.log(JSON.stringify({{q: QUESTIONS, t: TASKS}}));"
        res = subprocess.run(["node", "-e", js], check=True, capture_output=True, text=True, encoding="utf-8")
        obj = json.loads(res.stdout)
        return obj["q"], obj["t"]


def load_lesson(lid, dirname, subtitle):
    d = ROOT / dirname
    title_part = dirname.split("_", 1)[1] if "_" in dirname else dirname
    num_label = "第 07 讲补充" if lid == "07s" else f"第 {lid} 讲"

    # 1) 教案安全摘要
    plan_secs = extract_safe_plan_sections(d / "教案.md")

    # 2) demo 代码（仅 demo*.py，严禁读 answer*）
    demos = []
    if (d / "代码").exists():
        for p in sorted((d / "代码").glob("demo*.py")):
            demos.append({"name": p.name, "code": p.read_text(encoding="utf-8")})

    # 3) 数据文件预览（<= 12KB 原文展示，超大文件如 100x100 只展示前 8 行 + 尺寸）
    data_files = []
    if (d / "数据").exists():
        for p in sorted((d / "数据").glob("*.txt")):
            raw = p.read_text(encoding="utf-8", errors="replace")
            rows = raw.splitlines()
            preview = raw if len(raw) <= 1200 else "\n".join(rows[:6]) + f"\n...（共 {len(rows)} 行，完整文件位于 {dirname}/数据/{p.name}）"
            data_files.append({"name": p.name, "rows": len(rows), "cols": len(rows[0]) if rows else 0, "preview": preview})

    # 4) 客观题与任务
    if lid in EXTRA_LESSONS:
        qs = EXTRA_LESSONS[lid]["questions"]
        ts = EXTRA_LESSONS[lid]["tasks"]
    else:
        prac_html = (d / "练习.html").read_text(encoding="utf-8")
        qs, ts = parse_js_vars_via_node(prac_html)

    # 归一化任务字段
    norm_tasks = []
    for t in ts:
        norm_tasks.append({
            "id": t.get("id", "t1"),
            "level": t.get("level", "基础"),
            "title": t.get("title", ""),
            "file": t.get("file", ""),
            "brief": t.get("brief", ""),
            "requirements": t.get("requirements", []),
            "expected": t.get("expected", ""),
            "expectedNote": t.get("expectedNote", ""),
            "hints": t.get("hints", []),
            "starter": t.get("starter", ""),
        })

    # 课件相对路径（相对于 03_图像识别/图像识别全课程.html）
    slide_href = ""
    slide_label = ""
    if (d / "课件.html").exists():
        slide_href = f"系统课程16讲/{dirname}/课件.html"
        slide_label = "打开独立 HTML 课件"
    elif (d / "课件.pptx").exists():
        slide_href = f"系统课程16讲/{dirname}/课件.pptx"
        slide_label = "下载/打开 PPTX 课件"

    return {
        "id": lid,
        "numLabel": num_label,
        "title": title_part,
        "subtitle": subtitle,
        "dirname": dirname,
        "slideHref": slide_href,
        "slideLabel": slide_label,
        "plan": plan_secs,
        "demos": demos,
        "dataFiles": data_files,
        "questions": qs,
        "tasks": norm_tasks,
    }


def load_sprint_extras():
    """提取 03_图像识别/练习与模拟/ 下的 30 题扩散库、拓展四形状题库+任务、27 行必背核心代码。"""
    prac = TRACK_ROOT / "练习与模拟"
    # 1) 30 题客观题库
    qbank_html = (prac / "客观题练习.html").read_text(encoding="utf-8")
    mq = re.search(r"var\s+QS\s*=\s*(\[.*?\]);", qbank_html, re.S).group(1)
    js = f"const QS = {mq};\nconsole.log(JSON.stringify(QS));"
    qs30 = json.loads(subprocess.run(["node", "-e", js], check=True, capture_output=True, text=True, encoding="utf-8").stdout)

    # 2) 拓展特训 10 题 + 2 任务
    ext_html = (prac / "拓展练习_多形与空心.html").read_text(encoding="utf-8")
    me_q = re.search(r"var\s+MCQS\s*=\s*(\[.*?\]);", ext_html, re.S).group(1)
    me_t = re.search(r"var\s+TASKS\s*=\s*(\[.*?\]);", ext_html, re.S).group(1)
    js2 = f"const MCQS = {me_q};\nconst TASKS = {me_t};\nconsole.log(JSON.stringify({{q: MCQS, t: TASKS}}));"
    ext_obj = json.loads(subprocess.run(["node", "-e", js2], check=True, capture_output=True, text=True, encoding="utf-8").stdout)

    # 3) 27 行必背核心程序
    core_code = (prac / "冲刺练习" / "完整程序_初中组.py").read_text(encoding="utf-8")

    return {"qs30": qs30, "extQ": ext_obj["q"], "extT": ext_obj["t"], "coreCode": core_code}


HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>图像识别 · 全套课程与冲刺一体化平台（16讲 + 冲刺 + 题库 + 拓展）</title>
<style>
  :root {
    --brand:#0b5fff; --brand2:#2fa4ff; --ink:#1c2b3a; --mut:#64748b;
    --line:#e2e8f0; --bg:#f1f5f9; --ok:#137333; --okbg:#e6f4ea;
    --bad:#c5221f; --badbg:#fce8e6; --warn:#8a5a00; --warnbg:#fff8ec;
  }
  * { box-sizing:border-box; }
  body { margin:0; font-family:"Microsoft YaHei","PingFang SC",system-ui,sans-serif; background:var(--bg); color:var(--ink); line-height:1.6; font-size:15.5px; }

  /* 布局：左侧导航 + 右侧内容 */
  .app { display:flex; min-height:100vh; }
  .sidebar { width:290px; flex:0 0 290px; background:#fff; border-right:1px solid var(--line); display:flex; flex-direction:column; position:sticky; top:0; height:100vh; overflow-y:auto; }
  .brand-box { background:linear-gradient(135deg,#0b5fff 0%,#2fa4ff 100%); color:#fff; padding:18px 18px 14px; }
  .brand-box h1 { margin:0 0 4px; font-size:18px; }
  .brand-box p { margin:0; font-size:12.5px; opacity:.9; }
  .progress-pill { margin-top:10px; background:rgba(255,255,255,.18); border-radius:8px; padding:7px 10px; font-size:12.5px; }

  .nav-group { padding:10px 12px 4px; font-size:12px; font-weight:700; color:var(--mut); letter-spacing:1px; }
  .nav-item { display:flex; align-items:center; justify-content:space-between; padding:8px 14px; margin:2px 8px; border-radius:8px; cursor:pointer; font-size:13.5px; color:var(--ink); border:1px solid transparent; }
  .nav-item:hover { background:#f1f6ff; }
  .nav-item.active { background:#eaf2ff; border-color:#bfd6ff; color:var(--brand); font-weight:700; }
  .nav-left { display:flex; align-items:center; min-width:0; }
  .nav-no { display:inline-block; min-width:34px; text-align:center; font-size:11.5px; font-weight:700; padding:1px 5px; border-radius:6px; background:#e8eef6; color:#334155; margin-right:8px; }
  .nav-item.active .nav-no { background:var(--brand); color:#fff; }
  .nav-item.sprint .nav-no { background:#f3e8ff; color:#6b21a8; }
  .nav-item.sprint.active .nav-no { background:#7c3aed; color:#fff; }
  .nav-title { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .nav-dot { font-size:11.5px; color:var(--ok); margin-left:6px; flex:0 0 auto; }

  .side-foot { margin-top:auto; padding:12px; border-top:1px solid var(--line); display:flex; flex-direction:column; gap:6px; }
  .side-foot button { width:100%; padding:7px 10px; font-size:12.5px; border-radius:7px; border:1px solid var(--line); background:#fff; cursor:pointer; font-family:inherit; color:var(--ink); }
  .side-foot button:hover { border-color:var(--brand); color:var(--brand); }

  .main { flex:1; min-width:0; padding:20px 28px 60px; max-width:980px; }
  .banner { display:none; background:var(--warnbg); border:1px solid #ffe0b0; color:var(--warn); border-radius:10px; padding:10px 14px; margin-bottom:14px; font-size:14px; }

  .lesson-head { background:#fff; border:1px solid var(--line); border-radius:14px; padding:20px 24px; margin-bottom:16px; box-shadow:0 4px 14px rgba(15,35,70,.04); display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:12px; }
  .lesson-head .kicker { font-size:12.5px; color:var(--brand); font-weight:700; margin:0 0 4px; }
  .lesson-head h2 { margin:0 0 4px; font-size:23px; color:#0f2b5c; }
  .lesson-head .sub { margin:0; font-size:14px; color:var(--mut); }
  .head-actions { display:flex; gap:8px; flex-wrap:wrap; }

  .tabs { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:16px; }
  .tab-btn { padding:8px 16px; border-radius:9px; border:1px solid var(--line); background:#fff; cursor:pointer; font-family:inherit; font-size:14px; color:var(--ink); font-weight:600; }
  .tab-btn:hover { border-color:var(--brand); color:var(--brand); }
  .tab-btn.active { background:var(--brand); border-color:var(--brand); color:#fff; }

  .card { background:#fff; border:1px solid var(--line); border-radius:12px; padding:18px 20px; margin-bottom:16px; box-shadow:0 2px 10px rgba(15,35,70,.03); }
  .card h3 { margin:0 0 10px; font-size:17px; color:#0f2b5c; border-bottom:1px solid #eef2f7; padding-bottom:6px; }

  pre.code { background:#1e2433; color:#d8e6f3; padding:12px 14px; border-radius:9px; overflow-x:auto; font-family:Consolas,monospace; font-size:13.5px; line-height:1.55; margin:8px 0; white-space:pre-wrap; }
  pre.board { background:#f8fafc; border:1px solid var(--line); padding:10px 14px; border-radius:8px; font-family:Consolas,monospace; font-size:13.5px; white-space:pre-wrap; margin:8px 0; }
  code { font-family:Consolas,monospace; background:#f1f5f9; padding:1px 5px; border-radius:4px; font-size:13.5px; }

  .q-card { border:1px solid var(--line); border-radius:10px; padding:12px 14px; margin:10px 0; }
  .q-card.correct { border-color:var(--ok); background:#f3fbf6; }
  .q-card.wrong { border-color:var(--bad); background:#fdf4f4; }
  .q-meta { font-size:12px; color:var(--mut); margin-bottom:4px; }
  .q-stem { font-size:15px; font-weight:500; margin-bottom:8px; }
  .q-stem pre.mini { background:#f1f5f9; padding:8px 10px; border-radius:6px; font-family:Consolas,monospace; font-size:13.5px; margin:6px 0; white-space:pre-wrap; }
  label.opt { display:block; padding:5px 10px; border-radius:7px; cursor:pointer; font-size:14.5px; }
  label.opt:hover { background:#f1f6ff; }
  input.blank { width:100%; padding:7px 10px; font-family:Consolas,monospace; font-size:14.5px; border:1px solid #cbd5e1; border-radius:7px; }
  .why { display:none; margin-top:8px; padding:8px 12px; border-radius:8px; background:var(--warnbg); border:1px solid #ffe0b0; color:#7c4d00; font-size:13.5px; }
  .why.show { display:block; }

  .task-box { border:1px solid #dbe5f3; border-radius:10px; padding:14px 16px; margin-bottom:14px; background:#fcfdff; }
  .task-head { display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; flex-wrap:wrap; gap:6px; }
  .task-head h4 { margin:0; font-size:16px; color:#0f2b5c; }
  .badge { font-size:12px; padding:2px 9px; border-radius:999px; background:#eef4ff; color:var(--brand); }
  .badge.done { background:var(--okbg); color:var(--ok); font-weight:700; }
  .req-list { margin:6px 0 10px 20px; padding:0; font-size:14px; }
  textarea.editor { width:100%; min-height:135px; font-family:Consolas,monospace; font-size:13.5px; padding:10px 12px; border:1px solid #cbd5e1; border-radius:8px; resize:vertical; line-height:1.5; }
  textarea.paste { width:100%; min-height:76px; font-family:Consolas,monospace; font-size:13.5px; padding:8px 10px; border:1px solid #cbd5e1; border-radius:8px; resize:vertical; margin-top:8px; }

  .btn { display:inline-block; padding:7px 14px; border-radius:8px; border:1px solid var(--brand); background:var(--brand); color:#fff; font-size:13.5px; cursor:pointer; font-family:inherit; text-decoration:none; }
  .btn:hover { background:#004be5; }
  .btn.ghost { background:#fff; color:var(--brand); }
  .btn.ghost:hover { background:#eef5ff; }
  .btn.gray { background:#fff; color:#334155; border-color:#cbd5e1; }
  .btn.gray:hover { background:#f8fafc; }
  .row { display:flex; flex-wrap:wrap; gap:8px; margin-top:8px; align-items:center; }

  .hint-box { margin-top:8px; padding:8px 12px; border-radius:8px; background:var(--warnbg); border:1px solid #ffe0b0; color:var(--warn); font-size:13.5px; white-space:pre-wrap; }
  .msg { display:none; margin-top:8px; padding:8px 12px; border-radius:8px; font-size:13.5px; white-space:pre-wrap; }
  .msg.show { display:block; }
  .msg.ok { background:var(--okbg); color:var(--ok); border:1px solid #a8dab5; }
  .msg.bad { background:var(--badbg); color:var(--bad); border:1px solid #f5b7b1; }
  .msg.info { background:#eef4ff; color:#14417e; border:1px solid #c9dcff; }

  .plan-md { font-size:14px; line-height:1.65; }
  .plan-md ul, .plan-md ol { margin:6px 0 10px 20px; padding:0; }
  table.err-tbl { width:100%; border-collapse:collapse; font-size:13.5px; margin-top:6px; }
  table.err-tbl th, table.err-tbl td { border:1px solid var(--line); padding:6px 10px; text-align:left; }
  table.err-tbl th { background:#f8fafc; }

  .mobile-bar { display:none; background:#fff; border-bottom:1px solid var(--line); padding:10px 14px; align-items:center; justify-content:space-between; }
  @media (max-width:860px) {
    .app { flex-direction:column; }
    .sidebar { width:100%; height:auto; position:static; display:none; }
    .sidebar.open { display:flex; }
    .mobile-bar { display:flex; }
    .main { padding:16px 14px 40px; }
  }
</style>
</head>
<body>

<div class="mobile-bar">
  <b>图像识别 · 全套课程平台</b>
  <button class="btn ghost" id="btnToggleNav">☰ 课程目录</button>
</div>

<div class="app">
  <aside class="sidebar" id="sidebar">
    <div class="brand-box">
      <div style="font-size:12px;opacity:.9;margin-bottom:4px;"><a href="index.html" style="color:#fff;text-decoration:none;">← 图像识别主页</a> · <a href="../index.html" style="color:#fff;text-decoration:none;">总入口</a></div>
      <h1>03 图像识别 · 全课程合集</h1>
      <p>16 讲系统课 + 六天冲刺 + 题库 + 拓展</p>
      <div class="progress-pill" id="globalProgress">加载进度中…</div>
    </div>
    <div id="navList"></div>
    <div class="side-foot">
      <button id="btnExportAll">导出全部学习记录 (.txt)</button>
      <button id="btnResetAll">清空本机全部进度</button>
    </div>
  </aside>

  <main class="main">
    <div class="banner" id="storeBanner">浏览器禁用了本地存储，本页功能仍可用，但刷新后作答与草稿会丢失。</div>
    <div id="contentHost"></div>
  </main>
</div>

<script id="COURSE_DATA" type="application/json">__DATA__</script>
<script>
(function () {
  'use strict';
  var DATA = JSON.parse(document.getElementById('COURSE_DATA').textContent);
  var LS_KEY = 'py_all_course_v1';
  var storeOK = true;

  var state = { activeId: '01', tab: 'learn', obj: {}, objScore: {}, drafts: {}, hints: {}, tasksDone: {}, q30: {}, extObj: {}, extDone: {}, extHints: {}, extDrafts: {} };
  function loadState() {
    try {
      var raw = localStorage.getItem(LS_KEY);
      if (raw) {
        var s = JSON.parse(raw);
        if (s && typeof s === 'object') {
          for (var k in state) { if (k in s && s[k] !== null && s[k] !== undefined) state[k] = s[k]; }
        }
      }
    } catch (e) { storeOK = false; }
  }
  function saveState() {
    try { localStorage.setItem(LS_KEY, JSON.stringify(state)); }
    catch (e) { storeOK = false; $('storeBanner').style.display = 'block'; }
    updateSidebarStats();
  }

  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  function fmtInline(s) { return esc(s).replace(/`([^`]+)`/g, '<code>$1</code>'); }
  function normalizeOut(t) {
    var lines = String(t).replace(/\r\n/g, '\n').replace(/\r/g, '\n').split('\n');
    for (var i = 0; i < lines.length; i++) lines[i] = lines[i].replace(/^[\s\u3000]+/, '').replace(/[\s\u3000]+$/, '');
    while (lines.length && lines[lines.length - 1] === '') lines.pop();
    return lines.join('\n');
  }
  function normBlank(s) {
    s = String(s).replace(/^[\s\u3000]+/, '').replace(/[\s\u3000]+$/, '');
    if (s.length >= 2 && s.charAt(0) === s.charAt(s.length - 1) && (s.charAt(0) === '"' || s.charAt(0) === "'")) s = s.substring(1, s.length - 1);
    return s.replace(/[\s\u3000]+/g, '');
  }
  function copyText(text, btn) {
    var ta = document.createElement('textarea');
    ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); if (btn) { var old = btn.textContent; btn.textContent = '已复制 ✓'; setTimeout(function () { btn.textContent = old; }, 1200); } } catch (e) {}
    document.body.removeChild(ta);
  }

  function renderPlanSection(title, md) {
    if (!md) return '';
    if (title === '板书设计') {
      var clean = md.replace(/```[a-z]*\n?/g, '').replace(/```/g, '').trim();
      return '<div class="card"><h3>' + esc(title) + '</h3><pre class="board">' + esc(clean) + '</pre></div>';
    }
    if (title === '常见错误与纠正') {
      var lines = md.split('\n');
      var rows = [];
      for (var i = 0; i < lines.length; i++) {
        var ln = lines[i].trim();
        if (ln.indexOf('|') === 0 && ln.indexOf('---') === -1) {
          var cells = ln.split('|').slice(1, -1);
          rows.push(cells);
        }
      }
      if (rows.length > 1) {
        var tbl = '<table class="err-tbl"><thead><tr>';
        for (var c = 0; c < rows[0].length; c++) tbl += '<th>' + fmtInline(rows[0][c].trim()) + '</th>';
        tbl += '</tr></thead><tbody>';
        for (var r = 1; r < rows.length; r++) {
          tbl += '<tr>';
          for (var c2 = 0; c2 < rows[r].length; c2++) tbl += '<td>' + fmtInline(rows[r][c2].trim()) + '</td>';
          tbl += '</tr>';
        }
        tbl += '</tbody></table>';
        return '<div class="card"><h3>' + esc(title) + '</h3>' + tbl + '</div>';
      }
    }
    // 列表/段落转换
    var out = [], inUl = false;
    var rawLines = md.split('\n');
    for (var j = 0; j < rawLines.length; j++) {
      var l = rawLines[j].trim();
      if (!l) { if (inUl) { out.push('</ul>'); inUl = false; } continue; }
      if (/^[-*]\s+/.test(l) || /^\d+\.\s+/.test(l)) {
        if (!inUl) { out.push('<ul>'); inUl = true; }
        out.push('<li>' + fmtInline(l.replace(/^([-*]|\d+\.)\s+/, '').replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>')) + '</li>');
      } else {
        if (inUl) { out.push('</ul>'); inUl = false; }
        out.push('<p>' + fmtInline(l.replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>')) + '</p>');
      }
    }
    if (inUl) out.push('</ul>');
    return '<div class="card"><h3>' + esc(title) + '</h3><div class="plan-md">' + out.join('') + '</div></div>';
  }

  function isLessonDone(les) {
    var oScore = state.objScore[les.id];
    var objOk = (typeof oScore === 'number' && oScore === les.questions.length);
    var tDone = 0;
    for (var i = 0; i < les.tasks.length; i++) {
      var tid = les.id + '_' + les.tasks[i].id;
      if (state.tasksDone[tid]) tDone++;
    }
    return { objOk: objOk, tDone: tDone, tTotal: les.tasks.length };
  }

  function buildSidebar() {
    var host = $('navList');
    var html = '<div class="nav-group">系统课程（15 讲 + 1 补充）</div>';
    for (var i = 0; i < DATA.lessons.length; i++) {
      var l = DATA.lessons[i];
      var cls = 'nav-item' + (state.activeId === l.id ? ' active' : '');
      html += '<div class="' + cls + '" data-id="' + l.id + '"><span class="nav-left"><span class="nav-no">' + esc(l.id) + '</span><span class="nav-title">' + esc(l.title) + '</span></span><span class="nav-dot" id="dot-' + l.id + '"></span></div>';
    }
    html += '<div class="nav-group">考前冲刺与拓展专题</div>';
    var sprints = [
      { id: 'SP_CORE', no: '背', title: '27 行必背核心与口诀' },
      { id: 'SP_Q30', no: '题', title: '30 道扩散客观题库' },
      { id: 'SP_EXT', no: '拓', title: '拓展四形状与空心特训' },
      { id: 'SP_MOCK', no: '模', title: '全真模拟试卷 & 路线图' }
    ];
    for (var j = 0; j < sprints.length; j++) {
      var sp = sprints[j];
      var scls = 'nav-item sprint' + (state.activeId === sp.id ? ' active' : '');
      html += '<div class="' + scls + '" data-id="' + sp.id + '"><span class="nav-left"><span class="nav-no">' + sp.no + '</span><span class="nav-title">' + esc(sp.title) + '</span></span><span class="nav-dot" id="dot-' + sp.id + '"></span></div>';
    }
    host.innerHTML = html;

    var items = host.querySelectorAll('.nav-item');
    for (var k = 0; k < items.length; k++) {
      items[k].addEventListener('click', function () {
        state.activeId = this.getAttribute('data-id');
        state.tab = 'learn';
        saveState();
        buildSidebar();
        renderActive();
        $('sidebar').classList.remove('open');
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    }
    updateSidebarStats();
  }

  function updateSidebarStats() {
    var lesFull = 0, totalObjRight = 0, totalObjAll = 0, totalTaskDone = 0, totalTaskAll = 0;
    for (var i = 0; i < DATA.lessons.length; i++) {
      var l = DATA.lessons[i];
      var st = isLessonDone(l);
      totalObjAll += l.questions.length;
      if (typeof state.objScore[l.id] === 'number') totalObjRight += state.objScore[l.id];
      totalTaskAll += st.tTotal;
      totalTaskDone += st.tDone;
      var dot = $('dot-' + l.id);
      if (dot) {
        if (st.objOk && st.tDone === st.tTotal) { dot.textContent = '✓'; lesFull++; }
        else if (st.objOk || st.tDone > 0) dot.textContent = '•';
        else dot.textContent = '';
      }
    }
    var q30Ok = 0;
    for (var j = 0; j < DATA.sprint.qs30.length; j++) {
      var q = DATA.sprint.qs30[j];
      if (typeof state.q30[q.n] === 'number' && 'ABCD'.charAt(state.q30[q.n]) === q.ans) q30Ok++;
    }
    var gp = $('globalProgress');
    if (gp) gp.textContent = '16讲过关 ' + lesFull + '/16 · 课内客观 ' + totalObjRight + '/' + totalObjAll + ' · 冲刺30题 ' + q30Ok + '/30';
  }

  function findLesson(id) {
    for (var i = 0; i < DATA.lessons.length; i++) {
      if (DATA.lessons[i].id === id) return DATA.lessons[i];
    }
    return null;
  }

  function renderActive() {
    var id = state.activeId;
    if (id === 'SP_CORE') return renderSprintCore();
    if (id === 'SP_Q30') return renderSprintQ30();
    if (id === 'SP_EXT') return renderSprintExt();
    if (id === 'SP_MOCK') return renderSprintMocks();
    var les = findLesson(id) || DATA.lessons[0];
    renderLesson(les);
  }

  function renderLesson(les) {
    var host = $('contentHost');
    var html = '<div class="lesson-head"><div><p class="kicker">' + esc(les.numLabel) + ' · ' + esc(les.subtitle) + '</p><h2>' + esc(les.title) + '</h2><p class="sub">客观题 ' + les.questions.length + ' 道 · 程序任务 ' + les.tasks.length + ' 道 · 演示代码 ' + les.demos.length + ' 份</p></div>';
    if (les.slideHref) {
      html += '<div class="head-actions"><a class="btn ghost" href="' + esc(les.slideHref) + '" target="_blank">' + esc(les.slideLabel) + ' &rarr;</a></div>';
    }
    html += '</div>';

    html += '<div class="tabs">';
    var tabs = [
      { k: 'learn', name: '1. 本讲要点与演示代码' },
      { k: 'quiz', name: '2. 客观题自测 (' + les.questions.length + ')' },
      { k: 'tasks', name: '3. 程序任务 (' + les.tasks.length + ')' }
    ];
    for (var ti = 0; ti < tabs.length; ti++) {
      html += '<button class="tab-btn' + (state.tab === tabs[ti].k ? ' active' : '') + '" data-tab="' + tabs[ti].k + '">' + tabs[ti].name + '</button>';
    }
    html += '</div><div id="tabBody"></div>';
    host.innerHTML = html;

    var tBtns = host.querySelectorAll('.tab-btn');
    for (var b = 0; b < tBtns.length; b++) {
      tBtns[b].addEventListener('click', function () {
        state.tab = this.getAttribute('data-tab');
        saveState();
        renderLesson(les);
      });
    }

    if (state.tab === 'learn') renderTabLearn(les);
    else if (state.tab === 'quiz') renderTabQuiz(les);
    else renderTabTasks(les);
  }

  function renderTabLearn(les) {
    var body = $('tabBody');
    var html = '';
    var order = ['教学目标', '重点与难点', '板书设计', '常见错误与纠正'];
    for (var i = 0; i < order.length; i++) {
      html += renderPlanSection(order[i], les.plan[order[i]]);
    }
    if (les.demos.length) {
      html += '<div class="card"><h3>课堂演示代码（学生可运行对照）</h3>';
      for (var d = 0; d < les.demos.length; d++) {
        var dm = les.demos[d];
        html += '<div style="margin-bottom:14px;"><div style="display:flex;justify-content:space-between;align-items:center;"><b>' + esc(dm.name) + '</b><button class="btn gray copy-demo" data-idx="' + d + '">复制代码</button></div><pre class="code">' + esc(dm.code) + '</pre></div>';
      }
      html += '</div>';
    }
    if (les.dataFiles.length) {
      html += '<div class="card"><h3>本讲配套数据（位于 <code>' + esc(les.dirname) + '/数据/</code>）</h3>';
      for (var f = 0; f < les.dataFiles.length; f++) {
        var df = les.dataFiles[f];
        html += '<div style="margin-bottom:10px;"><b>' + esc(df.name) + '</b>（' + df.rows + ' 行 × ' + df.cols + ' 列）<pre class="board">' + esc(df.preview) + '</pre></div>';
      }
      html += '</div>';
    }
    if (!html) html = '<div class="card"><p>本讲重点为综合实践，请直接切换到「客观题自测」与「程序任务」开始练题。</p></div>';
    body.innerHTML = html;
    var cBtns = body.querySelectorAll('.copy-demo');
    for (var k = 0; k < cBtns.length; k++) {
      cBtns[k].addEventListener('click', function () {
        copyText(les.demos[Number(this.getAttribute('data-idx'))].code, this);
      });
    }
  }

  function renderTabQuiz(les) {
    var body = $('tabBody');
    var qs = les.questions;
    var saved = state.obj[les.id] || {};
    var html = '<div class="card"><h3>客观题自测（共 ' + qs.length + ' 题）</h3>';
    for (var i = 0; i < qs.length; i++) {
      var q = qs[i];
      var isBlank = (q.type === 'blank');
      html += '<div class="q-card" id="qcard-' + i + '"><div class="q-meta">第 ' + (i + 1) + ' 题 · ' + esc(q.tag || '') + (isBlank ? ' · 填空' : ' · 单选') + '</div>';
      html += '<div class="q-stem">' + q.stem + '</div>';
      if (isBlank) {
        var val = (typeof saved['q' + i] === 'string') ? saved['q' + i] : '';
        html += '<input type="text" class="blank" id="qblank-' + i + '" placeholder="' + esc(q.placeholder || '输入答案') + '" value="' + esc(val) + '">';
      } else {
        for (var oi = 0; oi < q.options.length; oi++) {
          var letter = 'ABCD'.charAt(oi);
          var chk = (saved['q' + i] === letter) ? ' checked' : '';
          html += '<label class="opt"><input type="radio" name="lq-' + i + '" value="' + letter + '"' + chk + '> ' + letter + '. ' + q.options[oi] + '</label>';
        }
      }
      html += '<div class="why" id="qwhy-' + i + '"></div></div>';
    }
    html += '<div class="row"><button class="btn" id="btnSubmitQuiz">提交批改</button><button class="btn ghost" id="btnRedoQuiz">清空重做</button><span id="quizScoreMsg" style="font-size:14px;color:var(--mut);"></span></div></div>';
    body.innerHTML = html;

    function grade(doSave) {
      var okCnt = 0, ansMap = {};
      for (var i = 0; i < qs.length; i++) {
        var q = qs[i], card = $('qcard-' + i), why = $('qwhy-' + i), ok = false;
        if (q.type === 'blank') {
          var v = $('qblank-' + i).value;
          ansMap['q' + i] = v;
          var acc = q.accept || [q.answer];
          for (var a = 0; a < acc.length; a++) { if (normBlank(v) === normBlank(acc[a])) ok = true; }
        } else {
          var picked = body.querySelector('input[name="lq-' + i + '"]:checked');
          var pv = picked ? picked.value : '';
          ansMap['q' + i] = pv;
          ok = (pv === q.answer);
        }
        if (ok) okCnt++;
        card.className = 'q-card ' + (ok ? 'correct' : 'wrong');
        why.className = 'why show';
        why.innerHTML = '<b>' + (ok ? '✓ 正确' : '✗ 错误，正确答案：' + esc(q.answer)) + '</b><br>' + q.explain;
      }
      $('quizScoreMsg').textContent = '得分：' + okCnt + ' / ' + qs.length;
      if (doSave) {
        state.obj[les.id] = ansMap;
        state.objScore[les.id] = okCnt;
        saveState();
      }
    }

    if (typeof state.objScore[les.id] === 'number') grade(false);
    $('btnSubmitQuiz').addEventListener('click', function () { grade(true); });
    $('btnRedoQuiz').addEventListener('click', function () {
      delete state.obj[les.id]; delete state.objScore[les.id]; saveState(); renderTabQuiz(les);
    });
  }

  function checkPythonFormat(code) {
    var issues = [];
    if (!code.trim()) return ['代码框是空的，请先写或粘贴你的代码'];
    if (/[“”‘’（）]/.test(code)) issues.push('发现中文引号或中文括号，Python 只认英文半角符号');
    if (/&&|\|\|/.test(code)) issues.push('Python 逻辑运算用 and / or，不用 && / ||');
    var lines = code.replace(/\r\n/g, '\n').split('\n'), hasT = false, hasS = false;
    for (var i = 0; i < lines.length; i++) {
      if (/^\t+/.test(lines[i])) hasT = true;
      if (/^ {2,}/.test(lines[i])) hasS = true;
      var cp = lines[i].split('#')[0].replace(/[\s\u3000]+$/, '');
      if (cp.indexOf('"') === -1 && cp.indexOf("'") === -1 && /^(if|elif|else|for|while|def)\b/.test(cp) && cp.charAt(cp.length - 1) !== ':') {
        issues.push('第 ' + (i + 1) + ' 行行末缺英文冒号 :');
      }
    }
    if (hasT && hasS) issues.push('缩进混用了 Tab 与空格，请统一用 4 个空格');
    var op = (code.match(/\(/g) || []).length, cl = (code.match(/\)/g) || []).length;
    if (op !== cl) issues.push('圆括号不配对：( 有 ' + op + ' 个，) 有 ' + cl + ' 个');
    return issues;
  }

  function renderTabTasks(les) {
    var body = $('tabBody');
    var html = '';
    for (var i = 0; i < les.tasks.length; i++) {
      var t = les.tasks[i];
      var tid = les.id + '_' + t.id;
      var done = !!state.tasksDone[tid];
      html += '<div class="task-box"><div class="task-head"><h4>' + esc(t.title) + '（' + esc(t.level) + ' · ' + esc(t.file) + '）</h4><span class="badge' + (done ? ' done' : '') + '" id="tbdg-' + i + '">' + (done ? '已核对 ✓' : '待完成') + '</span></div>';
      html += '<p style="margin:4px 0;">' + fmtInline(t.brief) + '</p>';
      if (t.requirements && t.requirements.length) {
        html += '<ul class="req-list">';
        for (var r = 0; r < t.requirements.length; r++) html += '<li>' + fmtInline(t.requirements[r]) + '</li>';
        html += '</ul>';
      }
      if (t.expected) {
        html += '<div style="font-size:13px;color:var(--mut);">预期输出：</div><pre class="board">' + esc(t.expected) + '</pre>';
      } else if (t.expectedNote) {
        html += '<div style="font-size:13px;color:var(--mut);">检查要求：' + esc(t.expectedNote) + '</div>';
      }
      var draftVal = (typeof state.drafts[tid] === 'string' && state.drafts[tid] !== '') ? state.drafts[tid] : (t.starter || '');
      html += '<textarea class="editor" id="tedit-' + i + '">' + esc(draftVal) + '</textarea>';
      html += '<div class="row"><button class="btn gray t-fmt" data-i="' + i + '">格式检查（不判分）</button><button class="btn gray t-exp" data-i="' + i + '">导出 .py</button><button class="btn ghost t-hint" data-i="' + i + '" id="thbtn-' + i + '">提示</button></div>';
      html += '<div id="thints-' + i + '"></div>';
      html += '<textarea class="paste" id="tpaste-' + i + '" placeholder="在 IDLE 按 F5 运行后，把输出的全部文字粘贴到这里核对…"></textarea>';
      html += '<div class="row"><button class="btn t-chk" data-i="' + i + '">' + (t.expected ? '核对输出' : '标记为已运行完成') + '</button></div>';
      html += '<div class="msg" id="tmsg-' + i + '"></div></div>';
    }
    body.innerHTML = html;

    function paintHints(idx) {
      var t = les.tasks[idx], tid = les.id + '_' + t.id;
      var u = state.hints[tid] || 0;
      $('thbtn-' + idx).textContent = '提示（已用 ' + u + '/' + t.hints.length + '）';
      var host = $('thints-' + idx); host.innerHTML = '';
      for (var k = 0; k < u && k < t.hints.length; k++) {
        var d = document.createElement('div'); d.className = 'hint-box';
        d.textContent = '提示 ' + (k + 1) + '/' + t.hints.length + '：' + t.hints[k];
        host.appendChild(d);
      }
    }

    for (var j = 0; j < les.tasks.length; j++) {
      (function (idx) {
        var t = les.tasks[idx], tid = les.id + '_' + t.id;
        paintHints(idx);
        $('tedit-' + idx).addEventListener('input', function () { state.drafts[tid] = this.value; saveState(); });
      })(j);
    }

    var fmtBtns = body.querySelectorAll('.t-fmt');
    for (var a = 0; a < fmtBtns.length; a++) fmtBtns[a].addEventListener('click', function () {
      var idx = Number(this.getAttribute('data-i'));
      var iss = checkPythonFormat($('tedit-' + idx).value);
      var msg = $('tmsg-' + idx);
      msg.className = 'msg show ' + (iss.length ? 'bad' : 'info');
      msg.textContent = iss.length ? '格式检查发现问题：\n· ' + iss.join('\n· ') : '格式检查通过（只查基础语法格式，去 IDLE 运行验证逻辑吧）！';
    });

    var expBtns = body.querySelectorAll('.t-exp');
    for (var b = 0; b < expBtns.length; b++) expBtns[b].addEventListener('click', function () {
      var idx = Number(this.getAttribute('data-i')), t = les.tasks[idx];
      var blob = new Blob([$('tedit-' + idx).value], { type: 'text/plain;charset=utf-8' });
      var link = document.createElement('a');
      link.href = URL.createObjectURL(blob); link.download = t.file || (les.id + '_' + t.id + '.py');
      document.body.appendChild(link); link.click(); document.body.removeChild(link);
    });

    var hBtns = body.querySelectorAll('.t-hint');
    for (var c = 0; c < hBtns.length; c++) hBtns[c].addEventListener('click', function () {
      var idx = Number(this.getAttribute('data-i')), t = les.tasks[idx], tid = les.id + '_' + t.id;
      var u = state.hints[tid] || 0;
      if (u < t.hints.length) { state.hints[tid] = u + 1; saveState(); paintHints(idx); }
    });

    var cBtns = body.querySelectorAll('.t-chk');
    for (var d = 0; d < cBtns.length; d++) cBtns[d].addEventListener('click', function () {
      var idx = Number(this.getAttribute('data-i')), t = les.tasks[idx], tid = les.id + '_' + t.id;
      var pasted = $('tpaste-' + idx).value, msg = $('tmsg-' + idx), bdg = $('tbdg-' + idx);
      if (pasted.indexOf('Traceback') !== -1) {
        msg.className = 'msg show bad'; msg.textContent = '你粘贴的是 Python 报错（Traceback）：回 IDLE 看红色报错最后一行，对照「常见错误」修改后再跑。';
        return;
      }
      if (!t.expected) {
        state.tasksDone[tid] = true; bdg.className = 'badge done'; bdg.textContent = '已核对 ✓'; saveState();
        msg.className = 'msg show ok'; msg.textContent = '已标记完成！';
        return;
      }
      if (!pasted.trim()) {
        msg.className = 'msg show info'; msg.textContent = '请先在 IDLE 中运行，把输出粘贴到框里再点核对。';
        return;
      }
      if (normalizeOut(pasted) === normalizeOut(t.expected)) {
        state.tasksDone[tid] = true; bdg.className = 'badge done'; bdg.textContent = '已核对 ✓'; saveState();
        msg.className = 'msg show ok'; msg.textContent = '输出完全一致，本任务通过！';
      } else {
        msg.className = 'msg show bad'; msg.textContent = '输出还不一致，逐行对照上面预期输出的空格、冒号和顺序；需要帮助点「提示」。';
      }
    });
  }

  /* ---- 冲刺模块 ---- */
  function renderSprintCore() {
    var host = $('contentHost');
    var html = '<div class="lesson-head"><div><p class="kicker">考前冲刺 · 必背代码模板</p><h2>27 行必背核心程序与四段口诀</h2><p class="sub">12 分钟脱稿默写并在真题三件套（圆形 / 等腰三角形 / 正五边形）实测通过</p></div></div>';
    html += '<div class="card"><h3>完整程序（27 行循环版）<button class="btn gray" id="copyCoreBtn" style="float:right;padding:3px 10px;">复制全部</button></h3><pre class="code">' + esc(DATA.sprint.coreCode) + '</pre></div>';
    html += '<div class="card"><h3>四段背诵口诀与规则顺序</h3><div class="plan-md"><ul>' +
      '<li><b>第 1 段 load（8 行）</b>：开文件、逐行读；去空白（<code>strip()</code>）、跳空行（<code>if line:</code>）；装进列表再返回。</li>' +
      '<li><b>第 2 段 row_widths（9 行）</b>：先找有 1 的行，首行数到尾行（<code>rows[-1] + 1</code> 别忘 +1），<code>count("1")</code> 数宽度。</li>' +
      '<li><b>第 3 段 classify（8 行）</b>：<b>顶宽够 10 是五边；宽度变小是圆；都不满足三角形。</b>（顺序绝对不能换，否则五边形会被圆形规则吃掉！）</li>' +
      '<li><b>第 4 段 主程序（3 行）</b>：1 到 3 拼名字；<code>图形1.txt  识别为: 圆形</code>（文件名后<b>两个空格</b>、<b>英文冒号</b>、一个空格）。</li>' +
      '</ul></div></div>';
    html += '<div class="card"><h3>手绘标准流程图样张（草稿纸必考）</h3><pre class="board">(开始) -> [输入: data/图形N.txt] -> [处理: strip去换行存入二维网格] -> [处理: 找上下边界算行宽 widths]\n  -> <widths[0] >= 10?> --是--> [输出: 正五边形]\n  -> 否 -> <行宽存在变小?> --是--> [输出: 圆形]\n  -> 否 -> [输出: 等腰三角形]\n  -> <3个文件处理完毕?> --否(回输入) / 是--> (结束)</pre></div>';
    host.innerHTML = html;
    $('copyCoreBtn').addEventListener('click', function () { copyText(DATA.sprint.coreCode, this); });
  }

  function renderSprintQ30() {
    var host = $('contentHost');
    var qs = DATA.sprint.qs30;
    var okCnt = 0, ansCnt = 0;
    for (var i = 0; i < qs.length; i++) {
      var p = state.q30[qs[i].n];
      if (typeof p === 'number') { ansCnt++; if ('ABCD'.charAt(p) === qs[i].ans) okCnt++; }
    }
    var html = '<div class="lesson-head"><div><p class="kicker">考前冲刺 · 独立客观题库</p><h2>30 道扩散新编单选题（与往年原卷零重复）</h2><p class="sub">当前已答 ' + ansCnt + '/30 · 正确 ' + okCnt + ' 题 · 点选项即时判分</p></div><div class="head-actions"><button class="btn ghost" id="q30WrongBtn">只重练错题</button><button class="btn gray" id="q30ResetBtn">全部重做</button></div></div>';
    for (var j = 0; j < qs.length; j++) {
      var q = qs[j], picked = state.q30[q.n], answered = (typeof picked === 'number');
      var good = answered && ('ABCD'.charAt(picked) === q.ans);
      html += '<div class="q-card' + (answered ? (good ? ' correct' : ' wrong') : '') + '"><div class="q-meta">第 ' + q.n + ' 题 · ' + esc(q.tag) + '</div>';
      html += '<div class="q-stem">' + fmtInline(q.stem) + (q.code ? '<pre class="mini">' + esc(q.code) + '</pre>' : '') + '</div>';
      for (var oi = 0; oi < q.opts.length; oi++) {
        var letter = 'ABCD'.charAt(oi), chk = (picked === oi) ? ' checked' : '';
        html += '<label class="opt"><input type="radio" name="q30-' + q.n + '" value="' + oi + '"' + chk + '> ' + letter + '. ' + fmtInline(q.opts[oi]) + '</label>';
      }
      html += '<div class="why' + (answered ? ' show' : '') + '">' + (answered ? ('<b>' + (good ? '✓ 正确' : '✗ 错，应选 ' + q.ans) + '</b> · ' + fmtInline(q.exp)) : '') + '</div></div>';
    }
    host.innerHTML = html;

    var radios = host.querySelectorAll('input[type="radio"]');
    for (var r = 0; r < radios.length; r++) {
      radios[r].addEventListener('change', function () {
        var qn = Number(this.name.split('-')[1]);
        state.q30[qn] = Number(this.value);
        saveState();
        renderSprintQ30();
      });
    }
    $('q30WrongBtn').addEventListener('click', function () {
      for (var k = 0; k < qs.length; k++) {
        var p2 = state.q30[qs[k].n];
        if (typeof p2 === 'number' && 'ABCD'.charAt(p2) !== qs[k].ans) delete state.q30[qs[k].n];
      }
      saveState(); renderSprintQ30();
    });
    $('q30ResetBtn').addEventListener('click', function () {
      if (confirm('清空 30 题练习记录？')) { state.q30 = {}; saveState(); renderSprintQ30(); }
    });
  }

  function renderSprintExt() {
    var host = $('contentHost');
    var qs = DATA.sprint.extQ, ts = DATA.sprint.extT;
    var html = '<div class="lesson-head"><div><p class="kicker">冲刺拓展 · 突破三件套</p><h2>多形状与空心轮廓特训（data_ext 四分类）</h2><p class="sub">覆盖正六边形、等腰梯形、空心正方形、实心正方形及图库距离匹配（数据位于 <code>练习与模拟/冲刺练习/data_ext/</code>）</p></div><div class="head-actions"><a class="btn ghost" href="练习与模拟/拓展练习_多形与空心.html" target="_blank">打开独立全屏拓展页 &rarr;</a></div></div>';
    html += '<div class="card"><h3>一、拓展客观题（10 题）</h3>';
    for (var i = 0; i < qs.length; i++) {
      var q = qs[i], picked = state.extObj[q.n], answered = (typeof picked === 'number'), good = answered && picked === q.ans;
      html += '<div class="q-card' + (answered ? (good ? ' correct' : ' wrong') : '') + '"><div class="q-meta">第 ' + q.n + ' 题</div><div class="q-stem">' + q.stem + '</div>';
      for (var oi = 0; oi < q.opts.length; oi++) {
        html += '<label class="opt"><input type="radio" name="eq-' + q.n + '" value="' + oi + '"' + (picked === oi ? ' checked' : '') + '> ' + 'ABCD'.charAt(oi) + '. ' + esc(q.opts[oi]) + '</label>';
      }
      html += '<div class="why' + (answered ? ' show' : '') + '">' + (answered ? ('<b>' + (good ? '✓ 正确' : '✗ 错，应选 ' + 'ABCD'.charAt(q.ans)) + '</b> · ' + esc(q.exp)) : '') + '</div></div>';
    }
    html += '</div><div class="card"><h3>二、拓展编程实操（2 题）</h3>';
    for (var j = 0; j < ts.length; j++) {
      var t = ts[j], done = !!state.extDone[t.id];
      html += '<div class="task-box"><div class="task-head"><h4>' + esc(t.id + ' · ' + t.title) + '</h4><span class="badge' + (done ? ' done' : '') + '">' + (done ? '已通过 ✓' : '待核对') + '</span></div>';
      html += '<p>' + fmtInline(t.desc).replace(/\n/g, '<br>') + '</p>';
      html += '<textarea class="editor ext-ed" data-id="' + t.id + '">' + esc(state.extDrafts[t.id] || t.starter) + '</textarea>';
      html += '<textarea class="paste" id="epaste-' + t.id + '" placeholder="粘贴 IDLE 运行输出核对…"></textarea>';
      html += '<div class="row"><button class="btn ext-chk" data-i="' + j + '">核对输出</button></div><div class="msg" id="emsg-' + t.id + '"></div></div>';
    }
    html += '</div>';
    host.innerHTML = html;

    var rs = host.querySelectorAll('input[type="radio"]');
    for (var r = 0; r < rs.length; r++) rs[r].addEventListener('change', function () {
      state.extObj[Number(this.name.split('-')[1])] = Number(this.value); saveState(); renderSprintExt();
    });
    var eds = host.querySelectorAll('.ext-ed');
    for (var e = 0; e < eds.length; e++) eds[e].addEventListener('input', function () {
      state.extDrafts[this.getAttribute('data-id')] = this.value; saveState();
    });
    var chks = host.querySelectorAll('.ext-chk');
    for (var c = 0; c < chks.length; c++) chks[c].addEventListener('click', function () {
      var t = ts[Number(this.getAttribute('data-i'))], p = $('epaste-' + t.id).value, m = $('emsg-' + t.id);
      if (p.indexOf('Traceback') !== -1) { m.className = 'msg show bad'; m.textContent = '发现 Traceback 报错，请检查路径 data_ext/ 与语法。'; return; }
      if (normalizeOut(p) === normalizeOut(t.expect)) { state.extDone[t.id] = true; saveState(); renderSprintExt(); }
      else { m.className = 'msg show bad'; m.textContent = '输出还不一致，核对空格、保留两位小数及分类规则。'; }
    });
  }

  function renderSprintMocks() {
    var host = $('contentHost');
    host.innerHTML = '<div class="lesson-head"><div><p class="kicker">考前实战 · 全真模拟考试</p><h2>全真模拟试卷 &amp; 六天冲刺工作台</h2><p class="sub">建议在掌握第 01–15 讲或背熟 27 行程序后，限时闭卷演练</p></div></div>' +
      '<div class="card"><h3>两套全真模拟试卷（限时独立考试模式）</h3><p>模拟卷带独立倒计时、自动交卷评分与打印样式，点击将在新标签页打开：</p>' +
      '<div class="row"><a class="btn" href="练习与模拟/全真模拟试卷2.html" target="_blank">模拟卷二（60 分钟 · 全新 15 题 + 新点阵实测）&rarr;</a>' +
      '<a class="btn ghost" href="练习与模拟/全真模拟试卷.html" target="_blank">模拟卷一（40 分钟 · 10 题 + 代码自查）&rarr;</a></div></div>' +
      '<div class="card"><h3>配套文档与工作台直达</h3><div class="row">' +
      '<a class="btn gray" href="index.html">图像识别备赛主页</a>' +
      '<a class="btn gray" href="冲刺讲义与速记/六天冲刺课程.html" target="_blank">六天冲刺教学计划</a>' +
      '<a class="btn gray" href="冲刺讲义与速记/考前速记与答辩攻防.md" target="_blank">考前速记与答辩攻防</a>' +
      '<a class="btn gray" href="冲刺讲义与速记/图像识别备赛教程.md" target="_blank">21 章备赛完整教程</a>' +
      '</div></div>';
  }

  $('btnToggleNav').addEventListener('click', function () { $('sidebar').classList.toggle('open'); });
  $('btnExportAll').addEventListener('click', function () {
    var lines = ['图像识别全课程学习记录', '导出时间：' + new Date().toLocaleString()];
    for (var i = 0; i < DATA.lessons.length; i++) {
      var l = DATA.lessons[i], st = isLessonDone(l), sc = state.objScore[l.id];
      lines.push(l.numLabel + ' ' + l.title + ' | 客观题: ' + (typeof sc === 'number' ? sc + '/' + l.questions.length : '未提交') + ' | 任务: ' + st.tDone + '/' + st.tTotal);
    }
    var blob = new Blob([lines.join('\r\n')], { type: 'text/plain;charset=utf-8' });
    var a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = '图像识别全课程学习记录.txt';
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
  });
  $('btnResetAll').addEventListener('click', function () {
    if (!confirm('确定清空本机保存的全部 16 讲及冲刺题库作答、草稿和进度？')) return;
    try { localStorage.removeItem(LS_KEY); } catch (e) {}
    location.reload();
  });

  loadState();
  if (!storeOK) $('storeBanner').style.display = 'block';
  buildSidebar();
  renderActive();
})();
</script>
</body>
</html>
'''


def main():
    lessons = [load_lesson(lid, dname, sub) for lid, dname, sub in LESSON_DIRS]
    sprint = load_sprint_extras()
    payload = {"lessons": lessons, "sprint": sprint}
    data_json = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    html = HTML_TEMPLATE.replace("__DATA__", data_json)
    with open(OUT_HTML, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(html)
    total_q = sum(len(l["questions"]) for l in lessons) + len(sprint["qs30"]) + len(sprint["extQ"])
    total_t = sum(len(l["tasks"]) for l in lessons) + len(sprint["extT"])
    print(f"生成 {OUT_HTML.relative_to(REPO)} ({len(html.encode('utf-8'))} B)")
    print(f"内嵌统计: 课程 {len(lessons)} 讲, 客观题 {total_q} 道, 编程任务 {total_t} 道")
    return 0


if __name__ == "__main__":
    sys.exit(main())

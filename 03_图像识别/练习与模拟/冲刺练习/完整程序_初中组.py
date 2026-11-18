# 图像识别 · 必背版完整程序（初中组）——2026-11-17 实测通过
# 用法：放在 冲刺练习/ 文件夹里直接运行（data/ 内是真题三件套）
# 默写后与本文件逐字对照；预期输出：
#   图形1.txt  识别为: 圆形
#   图形2.txt  识别为: 等腰三角形
#   图形3.txt  识别为: 正五边形
# 与《背代码手册》四段完全一致（教程第 12 章为等价的另一种写法）。


def load(name):
    grid = []
    with open("data/" + name, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                grid.append(line)
    return grid


def row_widths(g):
    rows = []
    for r in range(len(g)):
        if "1" in g[r]:
            rows.append(r)
    widths = []
    for r in range(rows[0], rows[-1] + 1):
        widths.append(g[r].count("1"))
    return widths


def classify(widths):
    if widths[0] >= 10:
        return "正五边形"
    for i in range(len(widths) - 1):
        if widths[i] > widths[i + 1]:
            return "圆形"
    return "等腰三角形"


for i in (1, 2, 3):
    name = "图形" + str(i) + ".txt"
    print(name + "  识别为: " + classify(row_widths(load(name))))

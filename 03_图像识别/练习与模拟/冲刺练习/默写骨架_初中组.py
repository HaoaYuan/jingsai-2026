# 默写骨架 —— 配合《背代码手册》第 5、6 天限时默写使用
# 用法：把每个 TODO 处补全（删掉 TODO 注释和 pass），保存运行，
#       三行输出与《背代码手册》模板逐字一致才算过。
# 顺序：先默 load → row_widths → classify → 主程序，一段一段补。


def load(name):
    # TODO ① 准备空列表 grid
    # TODO ② with open("data/" + name, encoding="utf-8") as f: 逐行读
    # TODO ③ 每行 strip()，空行跳过，其余 append 进 grid
    # TODO ④ return grid
    pass


def row_widths(g):
    # TODO ① rows = []：找出所有有 "1" 的行号，存进 rows
    # TODO ② widths = []：从 rows[0] 到 rows[-1]（含），每行 count("1") 存进 widths
    # TODO ③ return widths
    pass


def classify(widths):
    # TODO ① 首行宽 >= 10 → return "正五边形"
    # TODO ② 行宽一旦变小 → return "圆形"
    # TODO ③ 否则 return "等腰三角形"
    pass


# TODO 主程序：i 取 1、2、3；name = "图形" + str(i) + ".txt"
# TODO 按模板打印：print(name + "  识别为: " + classify(row_widths(load(name))))

# demo1_六大句型.py -- 六大句型演示（课堂跟做用）
# 按 F5 运行，对照输出一节一节看

# ── 句型 1：输出 print(东西) ─────────────────
print("你好，Python")
print(2 + 3)            # 不带引号才会计算；带引号是原样显示

# ── 句型 2：变量 名字 = 值 ───────────────────
n = 7                   # 把 7 存进名字 n
print(n)

# ── 句型 3：输入 n = int(input()) ───────────
# input() 会在黑窗口等你敲字；练习和比赛里这样读入一个整数：
# n = int(input("请输入一个整数："))

# ── 句型 4：判断 if 条件: ... else: ... ──────
n = 8
if n % 2 == 0:          # 行末要有英文冒号
    print("偶数")        # 缩进 4 格
else:
    print("奇数")

# ── 句型 5：循环累加 for + total = total + i ─
total = 0
for i in range(1, 5):   # i 依次是 1, 2, 3, 4
    total = total + i
print(total)            # 1+2+3+4 = 10
# 以后还会把结果收集进「列表」，第 02 讲学。

# ── 句型 6：函数 def 名字(参数): ... return ... ─
def add(a, b):
    return a + b

print(add(3, 4))        # 7

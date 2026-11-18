# task2 成分提取与统计骨架：偶因数个数 / 奇因数之和 / 最大质因数
# 练习页 T2 同题；参考答案在教师包 answer2_成分提取.py

n = int(input())
even_count = 0
odd_sum = 0
# 第 1 部分：枚举 1 到 n 找全部因数，分两类统计
# 第 1 步：给 i 起始值 1，写循环 while i <= n:
# 第 2 步：循环里判断是不是因数：if n % i == 0:
# 第 3 步：因数里分偶奇：if i % 2 == 0: even_count 加 1；else: odd_sum 加 i
# 第 4 步：循环末尾 i = i + 1
# 第 2 部分：短除法找最大质因数（最后除掉的因子就是最大的）
m = n
max_prime = 0
i = 2
# 第 5 步：写双循环：外层 while i * i <= m:，内层 while m % i == 0:
#             内层两行：max_prime = i 和 m = m // i
# 第 6 步：循环结束后 if m > 1: max_prime = m
# 第 7 步：打印三行：even_count、odd_sum、max_prime
# 自查：输入 180 输出 12、78、5

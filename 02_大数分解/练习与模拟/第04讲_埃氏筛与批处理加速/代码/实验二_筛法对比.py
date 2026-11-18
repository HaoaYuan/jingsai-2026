# 实验二：分解一大批数 -- 逐个试除 vs 先埃氏筛再只除素数（教师演示版）
# 同一个任务：输出 2 ~ N 每个数的质因数分解式（两方案输出必须完全一致）
# 计时：time.perf_counter()；N 默认 100000，机房较慢可缩到 50000（教案 §流程）
# 学生版：先跑方案 A 记时，再跑方案 B 记时，填实验记录表

import time

N = 100000


def factor_line(m, parts):
    """把因子列表拼成 "m = a × b × ..."（格式与第 02 讲 T1 一致）"""
    s = ""
    for k in range(len(parts)):
        if k > 0:
            s = s + " × "
        s = s + str(parts[k])
    return str(m) + " = " + s


# ---------- 方案 A：逐个试除 ----------
# 思路一句话：每个数独立做短除法分解，互相不帮忙--简单直接，重复劳动多
def run_trial_all(n_max):
    """方案 A：逐个试除--每个数独立从 2 试到 √m，不建素数表"""
    lines = []
    for n in range(2, n_max + 1):
        m = n
        parts = []
        i = 2
        while i * i <= m:  # 只查到 √m（因子成对）
            while m % i == 0:
                parts.append(i)
                m = m // i
            i = i + 1
        if m > 1:
            parts.append(m)
        lines.append(factor_line(n, parts))
    return lines


# ---------- 埃氏筛：先造工具 ----------
# 思路一句话：把 2~√N 里每个素数的倍数都划掉，剩下的就是素数表
def build_primes(limit):
    """埃氏筛：返回 [2, 3, 5, ..., <=limit] 的素数表"""
    flags = [True] * (limit + 1)
    flags[0] = False
    if limit >= 1:
        flags[1] = False
    p = 2
    while p * p <= limit:  # 划到 √limit 就够了
        if flags[p]:  # p 没被划掉 → p 是素数
            multiple = p * p
            while multiple <= limit:
                flags[multiple] = False  # 划掉 p 的倍数
                multiple = multiple + p
        p = p + 1
    primes = []
    for v in range(2, limit + 1):
        if flags[v]:  # 没被划掉的都是素数
            primes.append(v)
    return primes


# ---------- 方案 B：筛后只除素数 ----------
# 思路一句话：先造好素数表，分解时只除表里的素数--合数候选全部跳过
def run_sieve_first(n_max):
    """方案 B：先埃氏筛出 √N 内素数表，分解时只除素数"""
    primes = build_primes(int(n_max ** 0.5))
    lines = []
    for n in range(2, n_max + 1):
        m = n
        parts = []
        for p in primes:
            if p * p > m:  # 表里的因子查完了：剩下的 m 要么是 1 要么是素数
                break
            while m % p == 0:
                parts.append(p)
                m = m // p
        if m > 1:
            parts.append(m)
        lines.append(factor_line(n, parts))
    return lines


print(f"任务：分解 2 ~ {N} 全部整数的质因数（每数一行），两方案输出必须完全一致")
t0 = time.perf_counter()
lines_a = run_trial_all(N)
ta = time.perf_counter() - t0
print(f"方案 A 逐个试除      ：{ta:.3f} 秒")

t0 = time.perf_counter()
lines_b = run_sieve_first(N)
tb = time.perf_counter() - t0
print(f"方案 B 埃氏筛后只除素数：{tb:.3f} 秒")

if lines_a == lines_b:
    print(f"输出一致性：完全一致（{len(lines_a)} 行）✔")
else:
    for k in range(len(lines_a)):
        if lines_a[k] != lines_b[k]:
            print(f"第 {k + 1} 行不一致：A={lines_a[k]!r}  B={lines_b[k]!r}")
            break
    print("输出不一致 -- 检查算法后再上课！")
    raise SystemExit(1)

print(f"提速：约 {ta / tb:.1f} 倍")
print("样例（第 1、10、100 行）：")
print(" ", lines_a[0])
print(" ", lines_a[9])
print(" ", lines_a[99])

# 实验一：分解单个大数 -- 三版试除同任务对比（教师演示版）
# 同一个任务：判断 n 是否质数（质数要把候选除满，最能拉开差距）
# 三版算法：朴素试除 / 优化试除（√n、跳偶）/ 6k±1 试除
# 计时：time.perf_counter()，重复 3 次取最小；单版限时 30 秒，超过如实记录「超时」
# 课堂用法：学生把其中一版的循环抄进 IDLE，自己给一个数计时，填实验记录表

import time

LIMIT = 30.0  # 单版限时（秒）
TARGETS = [1000003, 1000000007, 999999999989]


# ---------- 第 1 版：朴素试除 ----------
# 思路一句话：从 2 到 n-1 挨个试，能整除就不是质数--最老实，也最慢
def naive(n, limit):
    """朴素试除：从 2 试到 n - 1"""
    start = time.perf_counter()
    i = 2
    while i < n:  # 挨个试到 n-1，不做任何优化
        if n % i == 0:
            return False
        i = i + 1  # 下一个候选
        if i % 100000 == 0 and time.perf_counter() - start > limit:
            return None  # 超时
    return True


# ---------- 第 2 版：优化试除（√n、跳偶） ----------
# 思路一句话：因子成对、小的那个总在 √n 以内，查到 √n 就查完了；先除 2，再只试奇数 3,5,7…
def sqrt_skip(n, limit):
    """优化试除：只试到 √n，先除 2 再只试奇数"""
    start = time.perf_counter()
    if n % 2 == 0:  # 先除 2：偶数里只有 2 是质数
        return n == 2
    i = 3
    checks = 0
    while i * i <= n:  # 只查到 √n（因子成对）
        if n % i == 0:
            return False
        i = i + 2  # 跳偶：n 是奇数，不可能有偶数因子
        checks = checks + 1  # i 恒为奇数，撞不到 100000 的倍数，限时检查要用迭代计数
        if checks % 100000 == 0 and time.perf_counter() - start > limit:
            return None  # 超时
    return True


# ---------- 第 3 版：6k±1 试除 ----------
# 思路一句话：3 的倍数（9,15,21…）早被 3 除过，候选只剩 6k−1 和 6k+1 两种位置
def wheel_6k(n, limit):
    """6k±1 试除：除 2、3 之后只试 6k±1 位置的数"""
    start = time.perf_counter()
    if n % 2 == 0:  # 特判 2
        return n == 2
    if n % 3 == 0:  # 特判 3
        return n == 3
    i = 5
    checks = 0
    while i * i <= n:  # 只查到 √n（因子成对）
        if n % i == 0 or n % (i + 2) == 0:  # 一轮查 6k−1、6k+1 两个位置
            return False
        i = i + 6  # 跳到下一对 6k±1
        checks = checks + 1  # i 恒为奇数，撞不到 300000 的倍数，限时检查要用迭代计数
        if checks % 100000 == 0 and time.perf_counter() - start > limit:
            return None  # 超时
    return True


VERSIONS = [
    ("朴素试除", naive),
    ("优化试除", sqrt_skip),
    ("6k±1试除", wheel_6k),
]


print(f"单版限时 {LIMIT:g} 秒；每版共跑 3 次取最小耗时")
print(f"{'档位':<16}{'版本':<12}{'最快耗时':>12}   结论")
for n in TARGETS:
    for name, func in VERSIONS:
        t0 = time.perf_counter()
        r = func(n, LIMIT)
        dt = time.perf_counter() - t0
        # 再补两次取最小
        for _ in range(2):
            t0 = time.perf_counter()
            r2 = func(n, LIMIT)
            dt2 = time.perf_counter() - t0
            if r2 is not None and dt2 < dt:
                dt = dt2
            if r2 is not None:
                r = r2
        if r is None:
            print(f"{n:<16}{name:<12}{'>30 秒未出结果':>14}   超时（如实记录）")
        else:
            verdict = "是质数" if r else "是合数"
            print(f"{n:<16}{name:<12}{dt:>10.4f} 秒   {verdict}")
    print()

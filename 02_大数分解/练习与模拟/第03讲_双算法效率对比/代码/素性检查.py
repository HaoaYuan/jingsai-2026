# 素性检查.py -- 第 03 讲实验档位数字的素性验证（教师包）
# 用试除法判素：先跑本脚本确认三个实验档位都是质数，实验结果才可信
# 断言：1000003 / 1000000007 / 999999999989 均为质数；反例若干为合数

def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i = i + 1
    return True


TARGETS = [1000003, 1000000007, 999999999989]
COMPOSITES = [1, 4, 1000001, 1000000005, 999999999987]

failed = 0
for n in TARGETS:
    r = is_prime(n)
    print(f"{n}  {'是质数' if r else '是合数！！'}")
    if not r:
        failed = failed + 1
for n in COMPOSITES:
    r = is_prime(n)
    print(f"{n}  {'是质数！！（断言失败）' if r else '是合数（正常）'}")
    if r:
        failed = failed + 1

if failed:
    print(f"断言失败 {failed} 项 -- 更换实验档位数字后再上课！")
    raise SystemExit(1)
print("素性断言全部通过：三个档位均为质数，可直接用于效率实验。")

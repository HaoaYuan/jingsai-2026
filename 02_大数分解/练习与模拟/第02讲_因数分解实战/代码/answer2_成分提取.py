# answer2 成分提取与统计参考答案（教师包专属）
# 与 课程/工具/生成练习页.py REF[("02","T2")] 同源；输入样例 180 → 12 / 78 / 5
n = int(input())
even_count = 0
odd_sum = 0
i = 1
while i <= n:
    if n % i == 0:
        if i % 2 == 0:
            even_count = even_count + 1
        else:
            odd_sum = odd_sum + i
    i = i + 1
m = n
max_prime = 0
i = 2
while i * i <= m:
    while m % i == 0:
        max_prime = i
        m = m // i
    i = i + 1
if m > 1:
    max_prime = m
print(even_count)
print(odd_sum)
print(max_prime)

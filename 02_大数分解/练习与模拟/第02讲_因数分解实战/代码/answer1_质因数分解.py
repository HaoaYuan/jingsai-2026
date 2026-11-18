# answer1 质因数分解参考答案（教师包专属）
# 与 课程/工具/生成练习页.py REF[("02","T1")] 同源；输入样例 180
n = int(input())
m = n
parts = []
i = 2
while i * i <= m:
    while m % i == 0:
        parts.append(i)
        m = m // i
    i = i + 1
if m > 1:
    parts.append(m)
out = ""
for k in range(len(parts)):
    if k > 0:
        out = out + " × "
    out = out + str(parts[k])
print(str(n) + " = " + out)

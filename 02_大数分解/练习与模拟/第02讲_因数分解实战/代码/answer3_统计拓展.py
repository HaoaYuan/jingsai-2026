# answer3 因数个数与总和参考答案（教师包专属，选做题）
# 与 课程/工具/生成练习页.py REF[("02","T3")] 同源（基础版）；输入样例 180 → 18 / 546
# √n 拓展讲法（每找到一对因子 d 与 n // d 同时累加）见练习页 T3 提示 3
n = int(input())
count = 0
total = 0
for i in range(1, n + 1):
    if n % i == 0:
        count = count + 1
        total = total + i
print(count)
print(total)

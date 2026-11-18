# demo1 全因数有序输出：对准评分表「输出完整、格式规范」
# 运行后输入一个整数，例如：30
n = int(input("输入一个整数："))
factors = []
i = 1
while i <= n:
    if n % i == 0:
        factors.append(i)
    i = i + 1
print("因数共", len(factors), "个：")
# 逗号分隔一行输出（有序、不漏不重）
out = ""
for k in range(len(factors)):
    if k > 0:
        out = out + "、"
    out = out + str(factors[k])
print(out)

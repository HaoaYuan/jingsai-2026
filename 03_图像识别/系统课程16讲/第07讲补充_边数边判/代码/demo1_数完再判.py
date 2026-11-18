# 第 07 讲补充 示例 1：数完再判 -- 特征 + 规则 = 判断
# 循环负责数数，循环外的 if 负责下结论
row = "00111100001111000011110001100"
ones = 0
zeros = 0

for ch in row:
    if ch == "1":
        ones += 1
    else:
        zeros += 1

print("1 的个数:", ones)
print("0 的个数:", zeros)

if ones > zeros:
    print("这一行 1 比较多")
elif ones < zeros:
    print("这一行 0 比较多")
else:
    print("一样多")

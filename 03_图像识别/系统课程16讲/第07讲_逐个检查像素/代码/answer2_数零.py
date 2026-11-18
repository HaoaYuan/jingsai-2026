# 任务 2 参考答案
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

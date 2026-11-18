# 任务 1 参考答案
row = "00111100001111000011110001100"
count = 0

for ch in row:
    if ch == "1":
        count += 1

print("1 的个数:", count)

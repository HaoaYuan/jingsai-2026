# 任务 2 参考答案：最后一个 1
row = "00111100001111000011110001100"
last = 0

for i in range(len(row)):
    if row[i] == "1":
        last = i

print("最后一个 1 在位置:", last)

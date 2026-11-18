# 任务 3 参考答案
row = "00111100001111000011110001100"

for i in range(len(row)):
    if row[i] == "1":
        print("第一个 1 在位置:", i)
        break

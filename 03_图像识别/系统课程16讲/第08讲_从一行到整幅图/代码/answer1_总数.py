# 任务 1 参考答案
grid = ["00100", "01110", "11111", "01110", "00100"]
total = 0

for row in grid:
    for ch in row:
        if ch == "1":
            total += 1

print("总像素:", total)

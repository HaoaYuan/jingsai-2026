# 任务 2 参考答案
grid = ["00100", "01110", "11111", "01110", "00100"]

for i in range(len(grid)):
    count = 0
    for ch in grid[i]:
        if ch == "1":
            count += 1
    print("第", i, "行:", count)

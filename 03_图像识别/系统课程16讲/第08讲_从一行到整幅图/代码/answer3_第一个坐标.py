# 任务 3 参考答案
grid = ["00100", "01110", "11111", "01110", "00100"]

for i in range(len(grid)):
    for j in range(len(grid[i])):
        if grid[i][j] == "1":
            print("第一个 1 在:", (i, j))
            break
    else:
        continue
    break

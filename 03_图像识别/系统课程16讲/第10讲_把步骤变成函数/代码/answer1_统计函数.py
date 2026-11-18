# 任务 1 参考答案
def count_ones(grid):
    total = 0
    for row in grid:
        for ch in row:
            if ch == "1":
                total += 1
    return total

grid = ["00100", "01110", "11111", "01110", "00100"]
print(count_ones(grid))

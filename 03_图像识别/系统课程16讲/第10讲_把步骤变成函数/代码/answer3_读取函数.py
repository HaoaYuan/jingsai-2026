# 任务 3 参考答案
def read_grid(path):
    grid = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                grid.append(line)
    return grid

grid = read_grid("数据/小图形.txt")
total = 0
for row in grid:
    for ch in row:
        if ch == "1":
            total += 1
print(len(grid), len(grid[0]))
print("1 的总数:", total)

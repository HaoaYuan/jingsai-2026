# 任务 1 参考答案
grid = []
with open("数据/小图形.txt", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            grid.append(line)

total = 0
for row in grid:
    for ch in row:
        if ch == "1":
            total += 1

print("行数:", len(grid))
print("列数:", len(grid[0]))
print("1 的总数:", total)

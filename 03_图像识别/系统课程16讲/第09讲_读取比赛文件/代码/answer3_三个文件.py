# 任务 3 参考答案
names = ["图形1.txt", "图形2.txt", "图形3.txt"]

for name in names:
    grid = []
    with open("数据/" + name, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                grid.append(line)

    total = 0
    for row in grid:
        for ch in row:
            if ch == "1":
                total += 1

    print(name, len(grid), len(grid[0]), total)

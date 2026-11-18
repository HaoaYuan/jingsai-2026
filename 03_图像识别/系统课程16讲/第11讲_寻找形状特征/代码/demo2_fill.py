# 第 11 讲 示例 2：填充率
def read_grid(path):
    grid = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                grid.append(line)
    return grid


def count_ones(grid):
    total = 0
    for row in grid:
        for ch in row:
            if ch == "1":
                total += 1
    return total


def bbox(grid):
    top = len(grid)
    bottom = -1
    left = len(grid[0])
    right = -1
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] == "1":
                if i < top:
                    top = i
                if i > bottom:
                    bottom = i
                if j < left:
                    left = j
                if j > right:
                    right = j
    return top, bottom, left, right


def fill_ratio(grid):
    top, bottom, left, right = bbox(grid)
    height = bottom - top + 1
    width = right - left + 1
    return count_ones(grid) / (height * width)

for name in ["图形1.txt", "图形2.txt", "图形3.txt"]:
    grid = read_grid("数据/" + name)
    print(name, round(fill_ratio(grid), 3))

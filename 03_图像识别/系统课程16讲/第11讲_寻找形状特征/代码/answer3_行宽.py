# 任务 3 参考答案
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


def row_widths(grid):
    top, bottom, left, right = bbox(grid)
    widths = []
    for i in range(top, bottom + 1):
        count = 0
        for ch in grid[i]:
            if ch == "1":
                count += 1
        widths.append(count)
    return widths

def is_increasing(widths):
    for i in range(len(widths) - 1):
        if widths[i] > widths[i+1]:
            return False
    return True

for name in ["图形1.txt", "图形2.txt", "图形3.txt"]:
    grid = read_grid("数据/" + name)
    widths = row_widths(grid)
    print(name.replace(".txt", "") + ":", widths[0], widths[len(widths)//2], widths[-1], is_increasing(widths))

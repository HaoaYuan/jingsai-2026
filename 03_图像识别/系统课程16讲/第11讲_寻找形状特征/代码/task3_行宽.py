# 任务 3（选做）：行宽序列
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
    # 补全：按行统计 1 的个数
    return [0]

def is_increasing(widths):
    # 补全：判断是否一直不下降
    return False

for name in ["图形1.txt", "图形2.txt", "图形3.txt"]:
    grid = read_grid("数据/" + name)
    widths = row_widths(grid)
    print(name.replace(".txt", "") + ":", widths[0], widths[len(widths)//2], widths[-1], is_increasing(widths))

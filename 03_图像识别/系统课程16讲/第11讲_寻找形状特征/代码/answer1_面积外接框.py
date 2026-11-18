# 任务 1 参考答案
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


grid = read_grid("数据/图形1.txt")
print("面积:", count_ones(grid))
print("外接框:", bbox(grid))

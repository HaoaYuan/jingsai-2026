# 任务 1：面积与外接框
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
    # 补全：返回 (top, bottom, left, right)
    return 0, 0, 0, 0


grid = read_grid("数据/图形1.txt")
print("面积:", count_ones(grid))
print("外接框:", bbox(grid))

# 第 10 讲 示例 2：返回两个值
def grid_size(grid):
    return len(grid), len(grid[0])

grid = ["00100", "01110", "11111", "01110", "00100"]
rows, cols = grid_size(grid)
print(rows, cols)

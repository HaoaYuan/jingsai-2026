# 第 09 讲 示例 1：读取文件
grid = []

with open("数据/小图形.txt", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            grid.append(line)

print("行数:", len(grid))
print("第一行:", grid[0])
print("列数:", len(grid[0]))

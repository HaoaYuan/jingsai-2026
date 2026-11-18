# 第 12 讲 教师参考：在 36 个样例上测试规则
# 3 个原图 + 每个图形 6 个平移 + 5 个缩放 = 36 个
from pathlib import Path

BASE = Path("数据")


def load(name):
    return [line.strip() for line in (BASE / name).read_text(encoding="ascii").splitlines() if line.strip()]


def crop(grid):
    pts = [(r, c) for r, row in enumerate(grid) for c, ch in enumerate(row) if ch == "1"]
    rs = [p[0] for p in pts]
    cs = [p[1] for p in pts]
    top, bottom, left, right = min(rs), max(rs), min(cs), max(cs)
    return [row[left:right+1] for row in grid[top:bottom+1]]


def scale_nn(grid, factor):
    h, w = len(grid), len(grid[0])
    nh, nw = max(1, round(h * factor)), max(1, round(w * factor))
    out = []
    for i in range(nh):
        sr = min(h - 1, int(i / factor))
        out.append("".join(grid[sr][min(w - 1, int(j / factor))] for j in range(nw)))
    return out


def place(grid, dy=0, dx=0, size=100):
    h, w = len(grid), len(grid[0])
    top = (size - h) // 2 + dy
    left = (size - w) // 2 + dx
    canvas = [["0"] * size for _ in range(size)]
    for i, row in enumerate(grid):
        for j, ch in enumerate(row):
            if ch == "1":
                y, x = top + i, left + j
                if 0 <= y < size and 0 <= x < size:
                    canvas[y][x] = "1"
    return ["".join(r) for r in canvas]


def features(grid):
    pts = [(r, c) for r, row in enumerate(grid) for c, ch in enumerate(row) if ch == "1"]
    rs = [p[0] for p in pts]
    cs = [p[1] for p in pts]
    top, bottom, left, right = min(rs), max(rs), min(cs), max(cs)
    widths = [sum(1 for ch in grid[i] if ch == "1") for i in range(top, bottom + 1)]
    return widths[0], widths


def classify(top_width, widths):
    if top_width >= 10:
        return "正五边形"
    for i in range(len(widths) - 1):
        if widths[i] > widths[i+1]:
            return "圆形"
    return "等腰三角形"


labels = {"图形1.txt": "圆形", "图形2.txt": "等腰三角形", "图形3.txt": "正五边形"}
ok = 0
total = 0
for name, label in labels.items():
    shape = crop(load(name))
    tests = [place(shape)]
    for dy, dx in [(-10, 0), (10, 0), (0, -10), (0, 10), (-10, -10), (10, 10)]:
        tests.append(place(shape, dy, dx))
    for factor in [0.7, 0.8, 0.9, 1.1, 1.2]:
        tests.append(place(scale_nn(shape, factor)))
    for grid in tests:
        top_width, widths = features(grid)
        pred = classify(top_width, widths)
        total += 1
        if pred == label:
            ok += 1
        else:
            print("FAIL", name, pred, label, top_width, widths[:3])
print("accuracy:", ok, "/", total)

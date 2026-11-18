# 第 06 讲 示例 2：同时看两个特征
edges = 5
closed = True

if not closed:
    print("不是封闭图形")
elif edges == 3:
    print("三角形")
elif edges == 5:
    print("正五边形")
else:
    print("未知")

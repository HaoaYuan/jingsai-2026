# 第 06 讲 示例 1：根据边数判断形状
# edges 是变量：改它的值，程序走的那条路就跟着变
# 试一试：把 3 改成 5、再改成 4，各运行一次
edges = 3

if edges == 3:
    print("三角形")
elif edges == 5:
    print("正五边形")
elif edges == 0:
    print("圆形")
else:
    print("未知")

# 第 05 讲 示例 1：看身高决定票种（分支）
# height 是变量：改它的值，程序走的那条路就跟着变
# 试一试：把 135 改成 110、再改成 160，各运行一次
height = 135  # 单位：厘米

if height < 120:
    print("免票")
elif height < 150:
    print("半票")
else:
    print("全票")

# 第 05 讲 示例 3：把条件连起来（and / or / not）
# Python 用单词，不写 && || !
height = 135  # 单位：厘米
age = 11
rain = False
wind = True
has_card = False

if height >= 140 and age >= 12:
    print("可以坐过山车")
else:
    print("不能坐过山车")

if rain or wind:
    print("改到室内上课")
else:
    print("照常户外")

if not has_card:
    print("没带学生证，不能借书")

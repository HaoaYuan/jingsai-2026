# 第 07 讲 示例 2：看着计数器长大
# print 在循环里，能看到 count 每一步的变化
row = "00111100001111000011110001100"
count = 0

for ch in row:
    if ch == "1":
        count += 1
    print(count)

# 试一试：把 print(count) 移到循环外面（不缩进），会看到什么？

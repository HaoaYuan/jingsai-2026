# 任务 3 参考答案（选做）：对称吗
row = "00111100001111000011110001100"
diff = 0

for i in range(len(row)):
    if row[i] != row[len(row) - 1 - i]:
        diff += 1

if diff == 0:
    print("这一行左右对称")
else:
    print("这一行不对称")

# 试一试：把 row 换成 数据/对称一行.txt 里的内容 00111100001111011110000111100，再跑一次

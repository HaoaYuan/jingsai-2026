# 任务 3 参考答案
a = 3
b = 3
c = 5

if a == b and b == c:
    print("等边三角形")
elif a == b or b == c or a == c:
    print("等腰三角形")
else:
    print("普通三角形")

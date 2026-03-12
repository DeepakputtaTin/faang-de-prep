import shlex

s = "ERROR user=123 action=login msg=timeout"

a = s.split()
b = a[2].split('=')[1]
print(a,b)

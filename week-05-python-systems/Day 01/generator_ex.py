def fiesys(f):
    with open(f, 'r') as file:
        for line in file:
            if line.strip() != "":
                yield line.strip()
f = 'abc.csv'
fiesys(f)
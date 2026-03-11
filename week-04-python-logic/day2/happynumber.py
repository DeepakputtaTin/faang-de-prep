def happynumber(n):
    #sum = 0
    seen = set()
    while n != 1:
        print(n)
        if n in seen:
            print(False)
            break
        seen.add(n)
        n = sum(int(d)**2 for d in str(n))
    print( True)
num = int(input())
happynumber(num)
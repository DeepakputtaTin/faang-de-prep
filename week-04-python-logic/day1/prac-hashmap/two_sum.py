def two_sum(nums, target):
    seen ={}
    for i, n in enumerate(nums):
        print(i,n)
        complement = target -n
        if complement in seen:
            print( [seen[complement],i])
        seen[n] = i

if __name__ == '__main__':
    nums = [2,7,11,15]
    target = 9
    two_sum(nums, target)
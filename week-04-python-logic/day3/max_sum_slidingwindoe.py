def max_sum(nums, k):
    window_sum = sum(nums[:k])
    print(window_sum)
    best = window_sum

    for i in range(k, len(nums)):
        window_sum += nums[i]
        window_sum -= nums[i-k]
        print(f'current sum {window_sum}')
        best = max(best, window_sum)
    print(best)
nums =[1,4,2,9,7,3]
k =3
max_sum(nums, k)
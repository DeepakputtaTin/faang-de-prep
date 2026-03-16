def subsum_bf(nums, k):
    res = 0
    for i in range(len(nums)):
        cs = 0
        for j in range(i, len(nums)):
            #print(nums[j])
            cs += nums[j]
            print(cs)
            if cs == k:
                res+=1
    print(res)

def subsum_prefix(nums,k):
    res = cursum = 0
    prefixSums = {0:1}
    for num in nums:
        cursum+= num
        diff = cursum - k

        res += prefixSums.get(diff, 0)
        prefixSums[cursum] = 1+prefixSums.get(cursum,0)
    return res
nums = [1,2,3]
k = 3
#subsum_bf(nums, k)
print(subsum_prefix(nums, k))
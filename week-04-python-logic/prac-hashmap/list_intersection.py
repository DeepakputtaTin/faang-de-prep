def intersection(nums1, nums2):
    n1 = set(nums1)
    n2 = set(nums2)
    l=[]
    for i in n2:
        if i in n1:
            l.append(i)
    print(l)

    print(list(set(nums1) & set(nums2) ))
nums1 = [4,9,5]
nums2 = [9,4,9,8,4]
intersection(nums1, nums2)
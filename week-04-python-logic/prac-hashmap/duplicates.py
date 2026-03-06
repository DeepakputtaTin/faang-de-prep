def find_dupli(nums1):
    s1 = set(nums1)
    if len(s1) != len(nums1):
        print(True)
    else:
        print(False)

nums1 = [1,2,2,3]
find_dupli(nums1)
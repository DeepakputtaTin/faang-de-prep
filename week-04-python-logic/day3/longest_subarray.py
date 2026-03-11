def longestSubarray(s):
    left = 0
    seen ={}
    result = 0

    for right in range(len(s)):
        seen[s[right]] = seen.get(s[right],0)+1

        while seen[s[right]] > 1:
            print(s[left])
            print(seen[s[left]])
            seen[s[left]]  -= 1
            left+=1
        result = max(result, right-left +1)
    print(result)



s = input()
longestSubarray(s)
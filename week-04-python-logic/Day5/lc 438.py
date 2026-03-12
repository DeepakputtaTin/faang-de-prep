
from collections import Counter

class Solution(object):
    def findAnagrams(self, s, p):
        """
        :type s: str
        :type p: str
        :rtype: List[int]
        """
        result = []
        p_count = Counter(p)
        window_count = Counter(s[:len(p)])
        #print(window_count)
        if window_count == p_count:
            result.append(0)
        for i in range(1, len(s)-len(p)+1):
            window_count[s[i+len(p) - 1]] += 1
            window_count[s[i-1]] -= 1
            if window_count[s[i-1]] == 0:
                del window_count[s[i-1]]
            if window_count == p_count:
                result.append(i)
            #print(window_count)
        return(result)
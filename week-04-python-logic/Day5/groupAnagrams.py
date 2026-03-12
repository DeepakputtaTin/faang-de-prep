from collections import defaultdict


def groupAnagrams(stlist):
    groups = defaultdict(list)
    for i in stlist:
        #print(i)

        a = ''.join(sorted(i))
        #print(a)
        groups[a].append(i)
        print(groups)

stlist = ["eat", "tea", "tan", "ate", "nat", "bat"]
groupAnagrams(stlist)
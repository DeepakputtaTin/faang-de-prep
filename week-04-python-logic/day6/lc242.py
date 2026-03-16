from collections import Counter


def anagram(s,t):
    print(Counter(s) == Counter(t))
def anagram_sorted(s,t):
    print(sorted(s) == sorted(t))
s= 'anagram'
t = 'nagaram'
anagram_sorted(s,t)
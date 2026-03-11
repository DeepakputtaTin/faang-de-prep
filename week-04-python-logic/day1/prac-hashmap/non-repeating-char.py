from collections import Counter


def non_repeat(st):
    count = Counter(st)
    for i,char in enumerate(st):
       if count[char] == 1:
           print( i)
    print( -1)


if __name__ == '__main__':
    st = 'leetcode'
    non_repeat(st)
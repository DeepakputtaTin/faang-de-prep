from collections import  Counter

words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
freq = Counter(words)
print(freq.most_common(2))
print(freq)
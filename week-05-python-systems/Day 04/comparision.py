from sys import getsizeof


def compare_memory():
    my_list = [x for x in range(100000)]
    my_gen = ( x for x in range(100000))
    tem_list = [1,2,3,4,5,6,7,8,9,10]
    tem_tup = (1,2,3,4,5,6,7,8,9,10)
    print(f'List (100k): {getsizeof(my_list)}')
    print(f'Generator: {getsizeof(my_gen)}')
    print(f'List[1...10]: {getsizeof(tem_list)}')
    print(f'tuple(1..10) {getsizeof(tem_tup)}')

compare_memory()

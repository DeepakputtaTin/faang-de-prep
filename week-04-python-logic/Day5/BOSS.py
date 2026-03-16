import heapq
from collections import defaultdict

def analyze_logs(logs):
    log = defaultdict(int)
    heap =[]

    for i in logs:
        a = i.split()
        #print(a)
        b = a[2].split('=')[1]
        c = a[3].split('=')[1]
        elog = a[0] + ' ' +b + ' ' + c
        log[elog] +=  1
        print(log)
    for temp, count in log.items():

        heapq.heappush(heap, (count, temp))
        print(heap)
        if len(heap) > 3:
            heapq.heappop(heap)
            print(heap)
    return sorted([(t, c) for c, t in heap], key = lambda x: -x[1])
logs = [
        "ERROR user=123 action=login msg=timeout",
        "WARN  user=456 action=checkout msg=retry",
        "ERROR user=789 action=login msg=timeout",
        "INFO  user=123 action=logout msg=success",
        "ERROR user=456 action=login msg=timeout"
]

print(analyze_logs(logs))
    # → [("ERROR login timeout", 3), ("WARN checkout retry", 1), ("INFO logout success", 1)]
import collections
from collections import Counter
from itertools import count


class log_manager:
    def __init__(self):
        self.logsd = collections.defaultdict(list)
    def add_to_dict(self, key, value):
        self.logsd[key].append(value)

    def get_counts(self):
        for key, message in self.logsd.items():
            print(f'{key}: {len(message)}')

    def most_frequent(self):
        return max(self.logsd, key = lambda k: len(self.logsd[k]))

    def get_errors(self):
        print(self.logsd.get("ERROR"))
if __name__ == '__main__':
    logging = log_manager()
    logs = [
        "ERROR: database connection failed",
        "INFO: user logged in",
        "ERROR: timeout exceeded",
        "WARNING: disk space low",
        "INFO: request completed",
        "ERROR: null pointer exception",
        "INFO: cache refreshed"
    ]
    for i in logs:
        parts = i.split(':')
        logging.add_to_dict(parts[0],parts[1])
    print(logging.logsd)
    logging.get_counts()
    print(logging.most_frequent())
    logging.get_errors()




from collections import defaultdict, deque

class RateLimiter:
    def __init__(self, max_requests, window_size):
        self.max_requests = max_requests
        self.window_size = window_size
        self.windows = defaultdict(deque)

    def is_allowed(self, user_id, timestamp):
        while self.windows[user_id] and \
              timestamp - self.windows[user_id][0] >= self.window_size:
            self.windows[user_id].popleft()
        if len(self.windows[user_id]) < self.max_requests:
            self.windows[user_id].append(timestamp) 
            return True

        return False


requests = [
    {"user_id": "u1", "timestamp": 1},
    {"user_id": "u1", "timestamp": 4},
    {"user_id": "u1", "timestamp": 8},
    {"user_id": "u1", "timestamp": 9},   # BLOCKED
    {"user_id": "u2", "timestamp": 5},
    {"user_id": "u1", "timestamp": 12},  # ALLOWED
]

limiter = RateLimiter(max_requests=3, window_size=10)
for req in requests:
    result = limiter.is_allowed(req["user_id"], req["timestamp"])
    print(f"u={req['user_id']} t={req['timestamp']} → {result}")
requests = [
    {"user_id": "u1", "timestamp": 1},
    {"user_id": "u1", "timestamp": 4},
    {"user_id": "u1", "timestamp": 8},
    {"user_id": "u1", "timestamp": 9},   # BLOCKED
    {"user_id": "u2", "timestamp": 5},
    {"user_id": "u1", "timestamp": 12},  # ALLOWED
]

limiter = RateLimiter(max_requests=3, window_size=10)
for req in requests:
    result = limiter.is_allowed(req["user_id"], req["timestamp"])
    print(f"u={req['user_id']} t={req['timestamp']} → {result}")

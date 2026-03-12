import heapq


class RobotMonitor:
    def __init__(self, k: int):
        self.k = k
        self.heap = []
        self.latest = {}

    # initialize
    def add_reading(self, robot_id: str, temperature: float):
        self.latest[robot_id] = temperature
        #print(self.latest)
        heapq.heappush(self.heap, (temperature, robot_id))
        if len(self.heap) > self.k:
            heapq.heappop(self.heap)
        #print(self.heap)
    # add new reading, maintain top K

    def get_top_k(self) -> list:
        result = []
        for temp, rid in self.heap:
            if temp == self.latest[rid]:
                result.append((temp, rid))

        return sorted(result, reverse=True)




# return K most overheating robots
# format: [(temperature, robot_id), ...]

monitor = RobotMonitor(k=2)
monitor.add_reading("R1", 95.0)
monitor.add_reading("R2", 87.0)
monitor.add_reading("R3", 99.0)
monitor.add_reading("R4", 78.0)
monitor.add_reading("R5", 102.0)
monitor.add_reading("R1", 110.0)
print(monitor.get_top_k())
# → [(102.0, "R5"), (99.0, "R3")]
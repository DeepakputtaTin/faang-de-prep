import heapq

class RewardsSystem:
    def __init__(self):
        self.customers = {}  # phone → {name, points}

    def add_customer(self, phone, name, points):
        # your code
        self.customers[phone] = {"name": name, "points": points}
        #print(self.customers.values())

    def get_customer(self, phone):
        # your code
        return (self.customers[phone])
    def add_points(self, phone, points):
        # your code
        self.customers[phone]["points"] += points
        return (self.customers[phone])

    def top_customers(self, k):
        customer = heapq.nlargest(k, self.customers.items(), key = lambda x: x[1]['points'])
        print( [(data["name"], data["points"]) for phone, data in customer])
        # your code — hint: use heap!


if __name__ == '__main__':
    rewards = RewardsSystem()
    rewards.add_customer("913-278-3519", "Deepak", 250)
    rewards.add_customer("314-944-5566", "John", 180)
    rewards.add_customer("555-123-4567", "Jane", 320)

    rewards.get_customer("913-278-3519")
    # → {"name": "Deepak", "points": 250}

    rewards.add_points("913-278-3519", 100)

    rewards.get_customer("913-278-3519")
    # → {"name": "Deepak", "points": 350}

    rewards.top_customers(2)
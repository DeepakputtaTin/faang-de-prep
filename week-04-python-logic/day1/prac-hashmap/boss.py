from collections import defaultdict

class leaderboard:
    def __init__(self):
        self.scores = {}

    def add_score(self, player, score):
        self.scores[player] = self.scores.get(player, 0) + score

    def top(self, k):
        return sorted(
            self.scores.values(),
            reverse = True
        )[:k]
if __name__ == '__main__':
    board = leaderboard()
    board.add_score('Alice', 300)
    board.add_score('Bob', 300)
    board.add_score('Alice', 200)
    print(board.top(1))

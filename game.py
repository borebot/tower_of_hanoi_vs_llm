import json

class HanoiGame:
    def __init__(self, num_stones=3, max_moves=200):
        self.num_stones = num_stones
        self.max_moves = max_moves
        self.reset()

    def reset(self):
        self.cairns = {'A': list(range(self.num_stones, 0, -1)), 'B': [], 'C': []}
        self.moves = 0

    def move_stone(self, from_cairn, to_cairn):
        if self.is_valid_move(from_cairn, to_cairn):
            stone = self.cairns[from_cairn].pop()
            self.cairns[to_cairn].append(stone)
            self.moves += 1
            return True
        return False

    def is_valid_move(self, from_cairn, to_cairn):
        if from_cairn not in self.cairns or to_cairn not in self.cairns:
            return False
        if not self.cairns[from_cairn]:
            return False
        if not self.cairns[to_cairn]:
            return True
        return self.cairns[from_cairn][-1] < self.cairns[to_cairn][-1]

    def check_win(self):
        return len(self.cairns['C']) == self.num_stones

    def is_out_of_moves(self):
        return self.moves >= self.max_moves

    def get_state(self, is_active=False, is_paused=False):
        return {
            "cairns": self.cairns,
            "moves": self.moves,
            "is_win": self.check_win(),
            "is_active": is_active,
            "is_paused": is_paused
        }

    def to_json(self, is_active=False, is_paused=False):
        return json.dumps(self.get_state(is_active, is_paused))

    def to_llm_json(self):
        # A lean version of the state for the LLM
        llm_state = {
            "cairns": self.cairns,
            "moves": self.moves
        }
        return json.dumps(llm_state)

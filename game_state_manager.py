from problems import problems
import random

class GameStateManager:
    def __init__(self):
        self.states = {}
        self.sid_to_username = {}

    def start_game(self, room, players):
        self.states[room] = {
            'players': players,
            'scores': {p: 0 for p in players},
            'questions': random.sample(problems, 5),
            'current_index': 0
        }

    def get_current_question(self, room):
        return self.states[room]['questions'][self.states[room]['current_index']]['question']

    def evaluate_code(self, room, code):
        expected = self.states[room]['questions'][self.states[room]['current_index']]['answer']
        try:
            local_env = {}
            exec(code, {}, local_env)
            if 'jawaban' in local_env and str(local_env['jawaban']) == str(expected):
                return {'correct': True}
        except Exception:
            pass
        return {'correct': False}

    def increment_score(self, room, username):
        self.states[room]['scores'][username] += 1

    def next_question(self, room):
        self.states[room]['current_index'] += 1
        return self.states[room]['current_index'] < len(self.states[room]['questions'])

    def get_winner(self, room):
        scores = self.states[room]['scores']
        max_score = max(scores.values())
        winners = [k for k, v in scores.items() if v == max_score]
        return winners[0] if len(winners) == 1 else "Seri"

    def get_scores(self, room):
        return self.states[room]['scores']
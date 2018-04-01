import random
import pickle
from base import BaseAgent
from actions import ACTIONS


class QLearningAgent(BaseAgent):

    def __init__(self, use_epsilon=True, epsilon=1, alpha=0.5, gamma=0.9, total_games=1000):

        self.q_table = self.load_policy()
        if not self.q_table:
            self.epsilon = epsilon
        else:
            self.epsilon = epsilon / 2.0
        self.use_epsilon = use_epsilon
        self.gamma = gamma
        self.alpha = alpha

        self.initial_epsilon = self.epsilon
        self.game_number = 1
        self.total_games = total_games

        self.total_exploration = 0

    def _get_state(self, player_hand, house_up_card):

        return (player_hand.score(), house_up_card, player_hand.is_soft(), player_hand.can_split())

    def _get_max_q_actions(self, state, player_hand):

        if state not in self.q_table:
            return player_hand.get_valid_actions()

        max_q = max(self.q_table[state].values())
        return [action for action, value in self.q_table[state].items() if value == max_q]

    def _get_max_q(self, state):

        if state not in self.q_table:
            return 0

        return max(self.q_table[state].values())

    def _get_q(self, state, action):

        if not state in self.q_table:
            self.q_table[state] = dict([(action, 0) for action in ACTIONS.all_actions])

        return self.q_table[state][action]

    def get_action(self, player_hand, house_up_card):

        state = self._get_state(player_hand, house_up_card)

        rand = random.random()
        if self.use_epsilon and rand < self.epsilon:
            action = random.choice(player_hand.get_valid_actions())
            self.total_exploration += 1
        else:
            actions = self._get_max_q_actions(state, player_hand)
            #validate this is a valid action for the current hand
            actions = [action for action in actions if action in player_hand.get_valid_actions()]
            if not actions:
                actions = player_hand.get_valid_actions()

            action = random.choice(actions)

        return action

    def learn(self, player_hand, player_new_hand, house_up_card, reward, action):

        state = self._get_state(player_hand, house_up_card)
        new_state = self._get_state(player_new_hand, house_up_card)

        new_q = (1 - self.alpha) * self._get_q(state, action) + self.alpha * (reward + self.gamma * self._get_max_q(new_state))
        self.q_table[state][action] = new_q

    def end_cycle(self):

        self.epsilon = self.initial_epsilon - self.game_number / float(self.total_games)
        self.game_number += 1

    def learned_policy(self):

        return self.q_table.items()

    def load_policy(self):

        try:
            with open("policy.pickle", "r") as f:
                return pickle.loads(f.read())
        except:
            return {}

    def save_policy(self):

        with open("policy.pickle", "w") as f:
            f.write(pickle.dumps(self.q_table))


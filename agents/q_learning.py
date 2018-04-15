import random
import pickle
import json
from base import BaseAgent
from basic_strategy import BasicStrategyAgent
from actions import ACTIONS


class QLearningAgent(BaseAgent):

    def __init__(self, use_epsilon=True, epsilon=1, fixed_epsilon=None, alpha=0.5, gamma=0.9, total_games=1000):

        self.q_table = self.load_policy()
        #if not self.q_table:
            #"self.epsilon = epsilon
        #else:
            #self.epsilon = epsilon / 2.0

        self.fixed_epsilon = fixed_epsilon
        if fixed_epsilon is not None:
            self.epsilon = fixed_epsilon
        else:
            self.epsilon = epsilon

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
            #action = BasicStrategyAgent().get_action(player_hand, house_up_card)
            #action = GameProbability().choice(player_hand.get_valid_actions(), player_hand)
            self.total_exploration += 1
        else:
            actions = self._get_max_q_actions(state, player_hand)
            #validate this is a valid action for the current hand
            actions = [action for action in actions if action in player_hand.get_valid_actions()]
            if not actions:
                actions = player_hand.get_valid_actions()
                self.total_exploration += 1

            action = random.choice(actions)

        return action

    def learn(self, player_hand, player_new_hand, house_up_card, reward, action, description=""):

        state = self._get_state(player_hand, house_up_card)
        new_state = self._get_state(player_new_hand, house_up_card)

        state_q = self._get_q(state, action)
        max_q = self._get_max_q(new_state)

        new_q = state_q + self.alpha * (reward + self.gamma * max_q - state_q)
        #new_q = (1 - self.alpha) * state_q + self.alpha * (reward + self.gamma * max_q)
        self.q_table[state][action] = new_q

        with open("log.txt", "a") as f:
            f.write("From {} to {} with action {}. Reward: {}. Old Q: {}, New Q: {}. {}\n".format(state, new_state, action, reward, state_q, new_q, description))
            f.write("{} + {} * ({} + {} * {} - {}))\n".format(state_q, self.alpha, reward, self.gamma, max_q, state_q))
            #formula = "(1 - {}) * {} + {} * ({} + {} * {})".format(self.alpha, state_q, self.alpha, reward, self.gamma, max_q)
            #f.write("{}\n".format(formula))

        #time.sleep(5)

    def end_cycle(self):

        if self.fixed_epsilon is None:
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

    def save_policy(self, money_results):

        with open("policy.pickle", "w") as f:
            f.write(pickle.dumps(self.q_table))

        try:
            with open("results.json", "r") as f:
                results = json.loads(f.read())
        except:
            results = {"QLearningAgent": []}

        last_results = [r["money"] for r in results["QLearningAgent"]]
        if last_results and money_results > max(last_results):
            with open("best_policy.pickle", "w") as f:
                data = self.q_table.copy()
                data["money_results"] = money_results
                f.write(pickle.dumps(data))


class GameProbability(object):

    def calculate_probablity_of_busted(self, hand):

        score = hand.score()
        score_to_21 = 21 - score
        if score_to_21 >= 10:
            return 0

        cards_of_10_value = 4 * 4 #10, jack, queen, king
        cards_of_same_value = 4

        prob = score_to_21 * cards_of_same_value / 52.0
        return 1 - prob

    def choice(self, actions, hand):

        from numpy.random import choice

        prob_busted =  self.calculate_probablity_of_busted(hand)
        prob_hit = 1 - prob_busted
        prob_normal = 1 / float(len(actions))

        actions = sorted(actions)
        distribution = []

        choice(actions, 1, p=distribution)

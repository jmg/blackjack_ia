from base import BaseAgent
from actions import ACTIONS
import pickle
import operator


class CustomPolicyAgent(BaseAgent):

    def __init__(self):

        with open("best_policy.pickle", "r") as f:
            self.policy = pickle.loads(f.read())

    def _get_state(self, player_hand, house_up_card):

        return (player_hand.score(), house_up_card, player_hand.is_soft(), player_hand.can_split())

    def get_action(self, player_hand, house_up_card):

        state = self._get_state(player_hand, house_up_card)
        actions = self.policy[state]
        return sorted(actions.items(), key=operator.itemgetter(1), reverse=True)[0][0]


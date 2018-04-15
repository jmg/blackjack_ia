from base import BaseAgent
from actions import ACTIONS


class SimpleAgent(BaseAgent):

    def __init__(self, score_to_stay=21):

        self.score_to_stay = score_to_stay

    def get_action(self, player_hand, house_up_card):

        if player_hand.score() < self.score_to_stay:
            return ACTIONS.hit

        if player_hand.can_split():
            return ACTIONS.split

        return ACTIONS.stand


class BaseAgent(object):

    def get_action(self, player_hand, house_up_card):
        pass

    def learn(self, player_hand, player_new_hand, house_up_card, reward, action):
        pass

    def end_cycle(self):
        pass

    def learned_policy(self):
        return []

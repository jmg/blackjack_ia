import json

class BaseAgent(object):

    def get_action(self, player_hand, house_up_card):
        pass

    def learn(self, player_hand, player_new_hand, house_up_card, reward, action, decription):
        pass

    def end_cycle(self):
        pass

    def learned_policy(self):
        return []

    def save_results(self, data):

        try:
            with open("results.json", "r") as f:
                file_data = json.loads(f.read())
        except:
            file_data = {}

        if self.__class__.__name__ not in file_data:
            file_data[self.__class__.__name__] = [data]
        else:
            file_data[self.__class__.__name__].append(data)

        with open("results.json", "w") as f:
            f.write(json.dumps(file_data))

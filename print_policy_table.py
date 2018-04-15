import pickle
from blackjack import BasicStrategyAgent
import operator

try:
    with open("policy.pickle", "r") as f:
        data = pickle.loads(f.read())
except:
    print "Can't open policy file"
    exit()


states = sorted(data.items())
score = states[0][0][0]
next_score = states[0][0][0]
i = 0

actions_table = {}
soft_actions_table = {}

while True:

    no_ace_str = ""
    ace_str = ""

    while score == next_score:

        score = states[i][0][0]

        house_up_card = states[i][0][1]
        is_soft = states[i][0][2]
        can_split = states[i][0][3]

        try:
            max_action = sorted([(key, value) for key, value in states[i][1].items() if value != 0], key=operator.itemgetter(1), reverse=True)[0][0]
        except:
            max_action = "-"
        else:
            if max_action == "hit":
                max_action = "H"
            else:
                max_action = "S"

        if is_soft:
            if house_up_card not in soft_actions_table:
                soft_actions_table[house_up_card] = {}

            soft_actions_table[house_up_card][score] = max_action
        else:
            if house_up_card not in actions_table:
                actions_table[house_up_card] = {}

            actions_table[house_up_card][score] = max_action

        i += 1
        try:
            next_score = states[i][0][0]
        except:
            break

    try:
        score = states[i][0][0]
    except:
        break

print "HARD hands"
for house_up_card, score_actions in actions_table.items():
    print house_up_card, score_actions

print "SOFT hands"
for house_up_card, score_actions in soft_actions_table.items():
    print house_up_card, score_actions
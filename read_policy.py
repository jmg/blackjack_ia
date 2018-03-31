import pickle
from blackjack import BasicStrategyAgent

try:
    with open("policy.pickle", "r") as f:
        data = pickle.loads(f.read())
except:
    print "Can't open policy file"
    exit()

for state, actions in sorted(data.items()):

    basic_strategy_policy = BasicStrategyAgent().basic_strategy_policy

    max_q = max([value for value in actions.values() if value != 0])

    try:
        basic_strategy_action = basic_strategy_policy[state]
    except:
        basic_strategy_action = "stand"

    print state, "->", [action for action, q in actions.items() if q == max_q], basic_strategy_action
    #print state, "->", [(action, q) for action, q in actions.items()]
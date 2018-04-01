import pickle
from blackjack import BasicStrategyAgent

try:
    with open("policy.pickle", "r") as f:
        data = pickle.loads(f.read())
except:
    print "Can't open policy file"
    exit()

total_diff = 0
for state, actions in sorted(data.items()):

    basic_strategy_policy = BasicStrategyAgent().basic_strategy_policy

    max_q_actions = [value for value in actions.values() if value != 0]
    if not max_q_actions:
        total_diff += 1
        continue

    max_q = max(max_q_actions)

    try:
        basic_strategy_action = basic_strategy_policy[state]
    except:
        basic_strategy_action = "stand"

    actions = [action for action, q in actions.items() if q == max_q]
    if actions[0] != basic_strategy_action:
        total_diff += 1
        print "{} -> {} ({}), {}".format(state, actions, round(max_q, 2), basic_strategy_action)
    #print state, "->", [(action, q) for action, q in actions.items()]

print "Total different: {}/{}".format(total_diff, len(data.items()))
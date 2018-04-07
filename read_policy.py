import pickle
from blackjack import BasicStrategyAgent
import operator

try:
    with open("policy.pickle", "r") as f:
        data = pickle.loads(f.read())
except:
    print "Can't open policy file"
    exit()

money_results = data.pop("money_results", None)
total_diff = 0
differences = {}
for state, actions in sorted(data.items()):

    basic_strategy_policy = BasicStrategyAgent().basic_strategy_policy

    max_q_actions = [value for value in actions.values() if value != 0]
    if not max_q_actions:
        total_diff += 1
        print "Not found {}".format(state)
        continue

    max_q = max(max_q_actions)

    try:
        basic_strategy_action = basic_strategy_policy[state]
    except:
        basic_strategy_action = "stand"

    #actions = [action for action, q in actions.items() if q == max_q]
    actions_q = sorted([(key, value) for key, value in actions.items() if value != 0], key=operator.itemgetter(1), reverse=True)

    if actions_q[0][0] != basic_strategy_action:
        total_diff += 1

        if basic_strategy_action not in differences:
            differences[basic_strategy_action] = [(state, actions_q)]
        else:
            differences[basic_strategy_action].append((state, actions_q))

    #print state, "->", [(action, q) for action, q in actions.items()]

for action, state_actions_q_list in differences.items():

    print "Should use '{}' but:".format(action)
    for state, actions_q in state_actions_q_list:
        print "{} -> {}".format(state, actions_q)

print "Total different: {}/{}".format(total_diff, len(data.items()))
if money_results:
    print "Money results with this policy: {}".format(money_results)
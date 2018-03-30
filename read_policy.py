import pickle

with open("policy.pickle", "r") as f:
    data = pickle.loads(f.read())

for state, actions in sorted(data.items()):

    max_q = max(actions.values())
    print state, "->", [action for action, q in actions.items() if q == max_q]
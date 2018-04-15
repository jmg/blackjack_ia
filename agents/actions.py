import config

class ACTIONS:
    stand = "stand"
    hit = "hit"
    double = "double"
    split = "split"

    if config.ONLY_HIT_OR_STAND:
        all_actions = [stand, hit]
    else:
        all_actions = [stand, hit, double, split]


import os

try:
    os.remove("policy.pickle")
except:
    pass
try:
    os.remove("best_policy.pickle")
except:
    pass
try:
    os.remove("results.json")
except:
    pass
try:
    os.remove("log.txt")
except:
    pass
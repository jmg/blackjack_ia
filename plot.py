import matplotlib.pyplot as plt
import numpy as np
import json

with open("results.json") as f:
    data = json.loads(f.read())


def plot(algorithm, start=0, end=-1):
    money = [d["money"] for d in data[algorithm][start:end]]
    player_wins = [d["player_wins"] for d in data[algorithm][start:end]]

    plt.plot(money)
    plt.title(algorithm)

    N = len(money) / 20
    rolling_mean = np.convolve(money, np.ones((N,))/N, mode='valid')
    #plt.plot(player_wins)
    plt.plot(rolling_mean)
    plt.show()


try:
    plot("QLearningAgent", start=0)
except Exception, e:
    print e

try:
    plot("BasicStrategyAgent")
except:
    pass
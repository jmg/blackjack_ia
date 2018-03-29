import random
import time
import copy


class Card(object):

    def __init__(self, number, kind):

        self.number = number
        self.kind = kind

    def get_value(self):

        if self.number > 10:
            value = 10
        else:
            value = self.number

        return value

    def is_ace(self):

        return self.number == 1

    def __str__(self):

        number_figure = {
            1: "Ace",
            11: "Jack",
            12: "Queen",
            13: "King",
        }

        return "{} - {}".format(number_figure.get(self.number, self.number), self.kind)


class Deck(object):

    deck_mutiplier = 6

    def __init__(self):

        self.regenerate()

    def regenerate(self):

        self.cards = []
        for number in range(1,14):
            for kind in ["Diamantes", "Treboles", "Picas", "Corazones"]:
                card = Card(number, kind)
                self.cards.append(card)

        self.cards *= self.deck_mutiplier

    def get_random_card(self):

        if len(self.cards) < 60:
            self.regenerate()

        card = random.choice(self.cards)
        self.cards.remove(card)
        return card


class Bet(object):

    def __init__(self, value):

        self.value = value

    def double(self):

        self.value *= 2

    def get_value(self):

        return self.value

    def get_black_jack_value(self):

        return self.value * 1.5


class ACTIONS:
    stand = "stand"
    hit = "hit"
    double = "double"
    split = "split"

    all_actions = [stand, hit, double, split]


class Hand(object):

    def __init__(self, player, deck, bet):

        self.cards = []
        self.deck = deck
        self.bet = bet
        self.player = player

    def draw_init(self):

        self.draw_card()
        self.draw_card()

    def draw_card(self):

        card = self.deck.get_random_card()
        self.cards.append(card)
        return card

    def has_ace(self):

        for card in self.cards:
            if card.is_ace():
                return True

        return False

    def score(self, print_results=False):

        total = 0
        total_2 = 0
        ace = self.has_ace()

        for card in self.cards:
            total += card.get_value()

        if ace:
            total_2 = total + 10

        if print_results:
            total_str = total
            if ace and total_2 <= 21:
                total_str = "{} / {}".format(total, total_2)

        if ace and total_2 <= 21:
            total = total_2

        return total

    def is_soft(self):

        total = 0
        ace = self.has_ace()
        if not ace:
            return False

        for card in self.cards:
            total += card.get_value()

        return total + 10 <= 21

    def can_split(self):

        return len(self.cards) == 2 and self.cards[0].number == self.cards[1].number

    def can_double(self):

        return len(self.cards) <= 2

    def should_stand(self):

        return self.score() >= 21

    def get_valid_actions(self):

        valid_actions = [ACTIONS.stand]
        if self.score() < 21:
            valid_actions.append(ACTIONS.hit)
        if self.can_split():
            valid_actions.append(ACTIONS.split)
        if self.can_double():
            valid_actions.append(ACTIONS.double)

        return valid_actions

    def black_jack(self):

        score = self.score()
        return score == 21 and len(self.cards) == 2

    def busted(self):

        score = self.score()
        if score > 21:
            return True

        return False

    def get_winner_message(self, payment):

        winner_icon = ":(" if self.player.is_house() else ":)"
        message = "{} gana {} (${})".format(self.player.name, winner_icon, payment)
        return message

    def pay_win(self):

        bet = self.bet.get_value()
        payment = -bet if self.player.is_house() else bet

        print "+" * 80
        print self.get_winner_message(payment)
        print "+" * 80

        return payment

    def pay_draw(self):

        print "+" * 80
        print "Han empatado"
        print "+" * 80

        return 0

    def pay_backjack(self):

        bet = self.bet.get_value()
        payment = -bet if self.player.is_house() else self.get_backjack_payment(bet)

        print "+" * 80
        print "BlackJack!"
        print self.get_winner_message(payment)
        print "+" * 80

        return payment

    def get_backjack_payment(self, bet):

        return bet * 1.5

    def __str__(self):

        hand = "-" * 80
        hand += "\n"
        hand += "Hand from {}".format(self.player.name)
        hand += "\n"
        hand += "-" * 80
        hand += "\n"
        for card in self.cards:
            hand += str(card)
            hand += "\n"

        hand += "-" * 80
        hand += "\n"
        hand += "score: {}".format(self.score())
        hand += "\n"
        hand += "-" * 80
        return hand

    def copy(self):

        hand = Hand(self.player, self.deck, self.bet)
        hand.cards = self.cards[:]
        return hand


class Player(object):

    def __init__(self, deck, bet, name):

        self.name = name
        self.bet = bet
        self.deck = deck
        self.hands = []

        self.initial_hand(deck, bet)

    def initial_hand(self, deck, bet):

        hand = Hand(self, deck, bet)
        hand.draw_init()
        self.hands.append(hand)

    def double_bet(self, hand):

        hand.bet.double()
        hand.draw_card()

    def draw_card(self, hand):

        hand.draw_card()

    def split_hand(self, hand):

        hand_1 = Hand(self, self.deck, self.bet)
        hand_1.cards = [hand.cards[0]]
        hand_1.draw_card()

        hand_2 = Hand(self, self.deck, self.bet)
        hand_2.cards = [hand.cards[1]]
        hand_2.draw_card()

        return [hand_1, hand_2]

    def stand(self, hand):

        pass

    def execute_action(self, action, hand):

        actions = {
            ACTIONS.hit: self.draw_card,
            ACTIONS.double: self.double_bet,
            ACTIONS.split: self.split_hand,
            ACTIONS.stand: self.stand,
        }

        return actions[action](hand)

    def is_house(self):

        return False


class House(Player):

    def play(self, policy=None, score_to_stay=17):

        hand = self.hands[0]
        score = hand.score()
        while score < score_to_stay:
            hand.draw_card()
            score = hand.score()

        return hand

    def get_up_card(self):

        return self.hands[0].cards[0].get_value()

    def get_backjack_payment(self, bet):

        return bet

    def is_house(self):

        return True


class BotPlayer(Player):

    def play(self, agent, house_up_card):

        i = 0
        hands = self.hands
        return_hands = []

        while i < len(hands):

            player_hand = hands[i]

            while True:

                reward = 0
                done = False
                player_original_hand = player_hand.copy()

                if player_hand.should_stand():
                    done = True
                    action = ACTIONS.stand
                else:
                    action = agent.get_action(player_hand, house_up_card)
                    return_value = self.execute_action(action, player_hand)

                    if player_hand.busted():
                        done = True
                    elif player_hand.black_jack():
                        done = True
                    elif player_hand.should_stand():
                        done = True
                    else:
                        if action in [ACTIONS.stand, ACTIONS.double]:
                            done = True
                        elif action == ACTIONS.split:
                            hands = return_value
                            player_hand = hands[i]

                if done:
                    return_hands.append((player_original_hand, player_hand, action))
                    break
                else:
                    reward = player_hand.bet.get_value() / 2.0
                    agent.learn(player_original_hand, player_hand, house_up_card, reward, action)

            i += 1

        return return_hands


class IAGame(object):

    player_plays_ia = False

    def __init__(self):

        self.deck = Deck()

    def play(self, agent):

        bet = Bet(value=1)

        player = BotPlayer(self.deck, bet, "Jugador 1")
        house = House(self.deck, bet, "La banca")

        house_up_card = house.get_up_card()
        player_hands = player.play(agent, house_up_card)
        house_hand = house.play(score_to_stay=17)

        print house_hand
        money_results = 0.0

        for player_last_hand, player_hand, last_action in player_hands:

            print player_hand

            if player_hand.busted():
                money_results += house_hand.pay_win()
            elif player_hand.black_jack():
                money_results += player_hand.pay_backjack()
            elif house_hand.busted():
                money_results += player_hand.pay_win()
            elif house_hand.black_jack():
                money_results += house_hand.pay_backjack()
            else:
                player_score = player_hand.score()
                house_score = house_hand.score()

                if player_score > house_score:
                    money_results += player_hand.pay_win()
                elif player_score < house_score:
                    money_results += house_hand.pay_win()
                else:
                    money_results += house_hand.pay_draw()

            agent.learn(player_last_hand, player_hand, house_up_card, money_results, last_action)

        if money_results > 0:
            match_results = 1
        elif money_results < 0:
            match_results = -1
        else:
            match_results = 0

        return money_results, match_results


class BasicStrategyPolicy(object):

    def get_action(self):

        pass


class BasicAgent(object):

    def __init__(self, score_to_stay=21):

        self.score_to_stay = score_to_stay

    def get_action(self, player_hand, house_up_card):

        if player_hand.score() < self.score_to_stay:
            return ACTIONS.hit

        if player_hand.can_split():
            return ACTIONS.split

        return ACTIONS.stand

    def learn(self, player_hand, player_new_hand, house_up_card, reward, action):

        pass

    def end_cycle(self):

        pass

    def learned_policy(self):

        return []


class QLearningAgent(object):

    def __init__(self, epsilon=1, alpha=0.5, gamma=0.9, total_games=1000):

        self.q_table = {}
        self.epsilon = epsilon
        self.gamma = gamma
        self.alpha = alpha

        self.initial_epsilon = epsilon
        self.game_number = 1
        self.total_games = total_games

    def _get_state(self, player_hand, house_up_card):

        return (player_hand.score(), house_up_card, player_hand.is_soft(), player_hand.can_split())

    def _get_max_q_actions(self, state, player_hand):

        if state not in self.q_table:
            return player_hand.get_valid_actions()

        max_q = max(self.q_table[state].values())
        return [action for action, value in self.q_table[state].items() if value == max_q]

    def _get_max_q(self, state):

        if state not in self.q_table:
            return 0

        return max(self.q_table[state].values())

    def _get_q(self, state, action):

        if not state in self.q_table:
            self.q_table[state] = dict([(action, 0) for action in ACTIONS.all_actions])

        return self.q_table[state][action]

    def get_action(self, player_hand, house_up_card):

        state = self._get_state(player_hand, house_up_card)

        if random.random() > self.epsilon:
            actions = self._get_max_q_actions(state, player_hand)
            action = random.choice(actions)
        else:
            action = random.choice(player_hand.get_valid_actions())

        return action

    def learn(self, player_hand, player_new_hand, house_up_card, reward, action):

        state = self._get_state(player_hand, house_up_card)
        new_state = self._get_state(player_new_hand, house_up_card)

        new_q = (1 - self.alpha) * self._get_q(state, action) + self.alpha * (reward + self.gamma * self._get_max_q(new_state))
        self.q_table[state][action] = new_q

    def end_cycle(self):

        self.epsilon = self.initial_epsilon - (self.game_number / float(self.total_games))
        self.game_number += 1

    def learned_policy(self):

        return self.q_table.items()


if __name__ == "__main__":
    #results_file = open("results.txt", "w")
    ia_game = IAGame()

    banca_wins = 0
    player_wins = 0
    draws = 0
    money = 0.0

    total_games = 2000
    #agent = BasicAgent(score_to_stay=17)
    agent = QLearningAgent(epsilon=1, total_games=total_games)

    for game_number in range(total_games):

        print "*" * 80
        print "Juego {}".format(game_number)
        money_results, match_results = ia_game.play(agent)
        print "*" * 80

        if match_results < 0:
            banca_wins += 1
        elif match_results > 0:
            player_wins += 1
        else:
            draws += 1
        print ""

        money += money_results

        agent.end_cycle()

    print "Cantidad de veces que gano el jugador 1: {}".format(player_wins)
    print "Cantidad de veces que gano la banca: {}".format(banca_wins)
    print "Cantidad de veces que empataron: {}".format(draws)
    print "Cantidad neta $: {}".format(money)

    for key, values in sorted(agent.learned_policy()):
        print key, values

    #results_file.write("Cantidad de veces que gano el jugador 1: {}\n".format(player_wins))
    #results_file.write("Cantidad de veces que gano la banca: {}\n".format(banca_wins))
    #results_file.write("Cantidad de veces que empataron: {}\n".format(draws))
    #results_file.write("Cantidad neta $: {}\n".format(money))

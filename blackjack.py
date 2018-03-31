import random
import time
import copy
import json
import pickle


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

        aces_count = 0
        for card in self.cards:
            if card.is_ace():
                aces_count += 1

        return aces_count

    def has_one_ace(self):

        return self.has_ace() == 1

    def score(self, hard=False, print_results=False):

        total = 0
        total_2 = 0
        has_ace = self.has_ace()

        for card in self.cards:
            total += card.get_value()

        if not hard and has_ace:
            total_2 = total + 10

        if print_results:
            total_str = total
            if has_ace and total_2 <= 21:
                total_str = "{} / {}".format(total, total_2)

        if not hard and has_ace and total_2 <= 21:
            total = total_2

        return total

    def is_soft(self):

        total = 0
        has_one_ace = self.has_one_ace()
        if not has_one_ace:
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
                    #should we reward if hits and don't get busted?
                    reward = 0
                    agent.learn(player_original_hand, player_hand, house_up_card, reward, action)

            i += 1

        return return_hands


class IAGame(object):

    player_plays_ia = False

    def __init__(self):

        self.deck = Deck()
        self.total_bet = 0

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
            self.total_bet += player_hand.bet.get_value()

        if money_results > 0:
            match_results = 1
        elif money_results < 0:
            match_results = -1
        else:
            match_results = 0

        return money_results, match_results


class BaseAgent(object):

    def get_action(self, player_hand, house_up_card):
        pass

    def learn(self, player_hand, player_new_hand, house_up_card, reward, action):
        pass

    def end_cycle(self):
        pass

    def learned_policy(self):
        return []


class BasicStrategyAgent(BaseAgent):

    def __init__(self):

        self.basic_strategy_policy = {
            #HARD HANDS
            (16,1,False,False): ACTIONS.hit,
            (16,2,False,False): ACTIONS.stand,
            (16,3,False,False): ACTIONS.stand,
            (16,4,False,False): ACTIONS.stand,
            (16,5,False,False): ACTIONS.stand,
            (16,6,False,False): ACTIONS.stand,
            (16,7,False,False): ACTIONS.hit,
            (16,8,False,False): ACTIONS.hit,
            (16,9,False,False): ACTIONS.hit,
            (16,10,False,False): ACTIONS.hit,

            (15,1,False,False): ACTIONS.hit,
            (15,2,False,False): ACTIONS.stand,
            (15,3,False,False): ACTIONS.stand,
            (15,4,False,False): ACTIONS.stand,
            (15,5,False,False): ACTIONS.stand,
            (15,6,False,False): ACTIONS.stand,
            (15,7,False,False): ACTIONS.hit,
            (15,8,False,False): ACTIONS.hit,
            (15,9,False,False): ACTIONS.hit,
            (15,10,False,False): ACTIONS.hit,

            (14,1,False,False): ACTIONS.hit,
            (14,2,False,False): ACTIONS.stand,
            (14,3,False,False): ACTIONS.stand,
            (14,4,False,False): ACTIONS.stand,
            (14,5,False,False): ACTIONS.stand,
            (14,6,False,False): ACTIONS.stand,
            (14,7,False,False): ACTIONS.hit,
            (14,8,False,False): ACTIONS.hit,
            (14,9,False,False): ACTIONS.hit,
            (14,10,False,False): ACTIONS.hit,

            (13,1,False,False): ACTIONS.hit,
            (13,2,False,False): ACTIONS.stand,
            (13,3,False,False): ACTIONS.stand,
            (13,4,False,False): ACTIONS.stand,
            (13,5,False,False): ACTIONS.stand,
            (13,6,False,False): ACTIONS.stand,
            (13,7,False,False): ACTIONS.hit,
            (13,8,False,False): ACTIONS.hit,
            (13,9,False,False): ACTIONS.hit,
            (13,10,False,False): ACTIONS.hit,

            (12,1,False,False): ACTIONS.hit,
            (12,2,False,False): ACTIONS.hit,
            (12,3,False,False): ACTIONS.hit,
            (12,4,False,False): ACTIONS.stand,
            (12,5,False,False): ACTIONS.stand,
            (12,6,False,False): ACTIONS.stand,
            (12,7,False,False): ACTIONS.hit,
            (12,8,False,False): ACTIONS.hit,
            (12,9,False,False): ACTIONS.hit,
            (12,10,False,False): ACTIONS.hit,

            (11,1,False,False): ACTIONS.hit,
            (11,2,False,False): ACTIONS.double,
            (11,3,False,False): ACTIONS.double,
            (11,4,False,False): ACTIONS.double,
            (11,5,False,False): ACTIONS.double,
            (11,6,False,False): ACTIONS.double,
            (11,7,False,False): ACTIONS.double,
            (11,8,False,False): ACTIONS.double,
            (11,9,False,False): ACTIONS.double,
            (11,10,False,False): ACTIONS.double,

            (10,1,False,False): ACTIONS.hit,
            (10,2,False,False): ACTIONS.double,
            (10,3,False,False): ACTIONS.double,
            (10,4,False,False): ACTIONS.double,
            (10,5,False,False): ACTIONS.double,
            (10,6,False,False): ACTIONS.double,
            (10,7,False,False): ACTIONS.double,
            (10,8,False,False): ACTIONS.double,
            (10,9,False,False): ACTIONS.double,
            (10,10,False,False): ACTIONS.hit,

            (9,1,False,False): ACTIONS.hit,
            (9,2,False,False): ACTIONS.hit,
            (9,3,False,False): ACTIONS.double,
            (9,4,False,False): ACTIONS.double,
            (9,5,False,False): ACTIONS.double,
            (9,6,False,False): ACTIONS.double,
            (9,7,False,False): ACTIONS.hit,
            (9,8,False,False): ACTIONS.hit,
            (9,9,False,False): ACTIONS.hit,
            (9,10,False,False): ACTIONS.hit,

            (8,1,False,False): ACTIONS.hit,
            (8,2,False,False): ACTIONS.hit,
            (8,3,False,False): ACTIONS.hit,
            (8,4,False,False): ACTIONS.hit,
            (8,5,False,False): ACTIONS.hit,
            (8,6,False,False): ACTIONS.hit,
            (8,7,False,False): ACTIONS.hit,
            (8,8,False,False): ACTIONS.hit,
            (8,9,False,False): ACTIONS.hit,
            (8,10,False,False): ACTIONS.hit,

            (7,1,False,False): ACTIONS.hit,
            (7,2,False,False): ACTIONS.hit,
            (7,3,False,False): ACTIONS.hit,
            (7,4,False,False): ACTIONS.hit,
            (7,5,False,False): ACTIONS.hit,
            (7,6,False,False): ACTIONS.hit,
            (7,7,False,False): ACTIONS.hit,
            (7,8,False,False): ACTIONS.hit,
            (7,9,False,False): ACTIONS.hit,
            (7,10,False,False): ACTIONS.hit,

            (6,1,False,False): ACTIONS.hit,
            (6,2,False,False): ACTIONS.hit,
            (6,3,False,False): ACTIONS.hit,
            (6,4,False,False): ACTIONS.hit,
            (6,5,False,False): ACTIONS.hit,
            (6,6,False,False): ACTIONS.hit,
            (6,7,False,False): ACTIONS.hit,
            (6,8,False,False): ACTIONS.hit,
            (6,9,False,False): ACTIONS.hit,
            (6,10,False,False): ACTIONS.hit,

            (5,1,False,False): ACTIONS.hit,
            (5,2,False,False): ACTIONS.hit,
            (5,3,False,False): ACTIONS.hit,
            (5,4,False,False): ACTIONS.hit,
            (5,5,False,False): ACTIONS.hit,
            (5,6,False,False): ACTIONS.hit,
            (5,7,False,False): ACTIONS.hit,
            (5,8,False,False): ACTIONS.hit,
            (5,9,False,False): ACTIONS.hit,
            (5,10,False,False): ACTIONS.hit,
            #SOFT HANDS
            #18 (ace + 7)
            (18,1,True,False): ACTIONS.hit,
            (18,2,True,False): ACTIONS.stand,
            (18,3,True,False): ACTIONS.double,
            (18,4,True,False): ACTIONS.double,
            (18,5,True,False): ACTIONS.double,
            (18,6,True,False): ACTIONS.double,
            (18,7,True,False): ACTIONS.stand,
            (18,8,True,False): ACTIONS.stand,
            (18,9,True,False): ACTIONS.hit,
            (18,10,True,False): ACTIONS.hit,
            #17 (ace + 6)
            (17,1,True,False): ACTIONS.hit,
            (17,2,True,False): ACTIONS.hit,
            (17,3,True,False): ACTIONS.double,
            (17,4,True,False): ACTIONS.double,
            (17,5,True,False): ACTIONS.double,
            (17,6,True,False): ACTIONS.double,
            (17,7,True,False): ACTIONS.hit,
            (17,8,True,False): ACTIONS.hit,
            (17,9,True,False): ACTIONS.hit,
            (17,10,True,False): ACTIONS.hit,
            #16 (ace + 5)
            (16,1,True,False): ACTIONS.hit,
            (16,2,True,False): ACTIONS.hit,
            (16,3,True,False): ACTIONS.hit,
            (16,4,True,False): ACTIONS.double,
            (16,5,True,False): ACTIONS.double,
            (16,6,True,False): ACTIONS.double,
            (16,7,True,False): ACTIONS.hit,
            (16,8,True,False): ACTIONS.hit,
            (16,9,True,False): ACTIONS.hit,
            (16,10,True,False): ACTIONS.hit,
            #15 (ace + 4)
            (15,1,True,False): ACTIONS.hit,
            (15,2,True,False): ACTIONS.hit,
            (15,3,True,False): ACTIONS.hit,
            (15,4,True,False): ACTIONS.double,
            (15,5,True,False): ACTIONS.double,
            (15,6,True,False): ACTIONS.double,
            (15,7,True,False): ACTIONS.hit,
            (15,8,True,False): ACTIONS.hit,
            (15,9,True,False): ACTIONS.hit,
            (15,10,True,False): ACTIONS.hit,
            #14 (ace + 3)
            (14,1,True,False): ACTIONS.hit,
            (14,2,True,False): ACTIONS.hit,
            (14,3,True,False): ACTIONS.hit,
            (14,4,True,False): ACTIONS.hit,
            (14,5,True,False): ACTIONS.double,
            (14,6,True,False): ACTIONS.double,
            (14,7,True,False): ACTIONS.hit,
            (14,8,True,False): ACTIONS.hit,
            (14,9,True,False): ACTIONS.hit,
            (14,10,True,False): ACTIONS.hit,
            #13 (ace + 2)
            (13,1,True,False): ACTIONS.hit,
            (13,2,True,False): ACTIONS.hit,
            (13,3,True,False): ACTIONS.hit,
            (13,4,True,False): ACTIONS.hit,
            (13,5,True,False): ACTIONS.double,
            (13,6,True,False): ACTIONS.double,
            (13,7,True,False): ACTIONS.hit,
            (13,8,True,False): ACTIONS.hit,
            (13,9,True,False): ACTIONS.hit,
            (13,10,True,False): ACTIONS.hit,
            #Can split Hands
            #2 aces
            (2,1,False,True): ACTIONS.split,
            (2,2,False,True): ACTIONS.split,
            (2,3,False,True): ACTIONS.split,
            (2,4,False,True): ACTIONS.split,
            (2,5,False,True): ACTIONS.split,
            (2,6,False,True): ACTIONS.split,
            (2,7,False,True): ACTIONS.split,
            (2,8,False,True): ACTIONS.split,
            (2,9,False,True): ACTIONS.split,
            (2,10,False,True): ACTIONS.split,
            #2 eights
            (16,1,False,True): ACTIONS.split,
            (16,2,False,True): ACTIONS.split,
            (16,3,False,True): ACTIONS.split,
            (16,4,False,True): ACTIONS.split,
            (16,5,False,True): ACTIONS.split,
            (16,6,False,True): ACTIONS.split,
            (16,7,False,True): ACTIONS.split,
            (16,8,False,True): ACTIONS.split,
            (16,9,False,True): ACTIONS.split,
            (16,10,False,True): ACTIONS.split,
            #2 figures or 10s
            (20,1,False,True): ACTIONS.stand,
            (20,2,False,True): ACTIONS.stand,
            (20,3,False,True): ACTIONS.stand,
            (20,4,False,True): ACTIONS.stand,
            (20,5,False,True): ACTIONS.stand,
            (20,6,False,True): ACTIONS.stand,
            (20,7,False,True): ACTIONS.stand,
            (20,8,False,True): ACTIONS.stand,
            (20,9,False,True): ACTIONS.stand,
            (20,10,False,True): ACTIONS.stand,
            #2 nines
            (18,1,False,True): ACTIONS.stand,
            (18,2,False,True): ACTIONS.split,
            (18,3,False,True): ACTIONS.split,
            (18,4,False,True): ACTIONS.split,
            (18,5,False,True): ACTIONS.split,
            (18,6,False,True): ACTIONS.split,
            (18,7,False,True): ACTIONS.stand,
            (18,8,False,True): ACTIONS.split,
            (18,9,False,True): ACTIONS.split,
            (18,10,False,True): ACTIONS.stand,
            #2 sevens
            (14,1,False,True): ACTIONS.hit,
            (14,2,False,True): ACTIONS.split,
            (14,3,False,True): ACTIONS.split,
            (14,4,False,True): ACTIONS.split,
            (14,5,False,True): ACTIONS.split,
            (14,6,False,True): ACTIONS.split,
            (14,7,False,True): ACTIONS.split,
            (14,8,False,True): ACTIONS.hit,
            (14,9,False,True): ACTIONS.hit,
            (14,10,False,True): ACTIONS.hit,
            #2 sixes
            (12,1,False,True): ACTIONS.hit,
            (12,2,False,True): ACTIONS.split,
            (12,3,False,True): ACTIONS.split,
            (12,4,False,True): ACTIONS.split,
            (12,5,False,True): ACTIONS.split,
            (12,6,False,True): ACTIONS.split,
            (12,7,False,True): ACTIONS.hit,
            (12,8,False,True): ACTIONS.hit,
            (12,9,False,True): ACTIONS.hit,
            (12,10,False,True): ACTIONS.hit,
            #2 fives
            (10,1,False,True): ACTIONS.hit,
            (10,2,False,True): ACTIONS.double,
            (10,3,False,True): ACTIONS.double,
            (10,4,False,True): ACTIONS.double,
            (10,5,False,True): ACTIONS.double,
            (10,6,False,True): ACTIONS.double,
            (10,7,False,True): ACTIONS.double,
            (10,8,False,True): ACTIONS.double,
            (10,9,False,True): ACTIONS.double,
            (10,10,False,True): ACTIONS.hit,
            #2 fours
            (8,1,False,True): ACTIONS.hit,
            (8,2,False,True): ACTIONS.hit,
            (8,3,False,True): ACTIONS.hit,
            (8,4,False,True): ACTIONS.hit,
            (8,5,False,True): ACTIONS.split,
            (8,6,False,True): ACTIONS.split,
            (8,7,False,True): ACTIONS.hit,
            (8,8,False,True): ACTIONS.hit,
            (8,9,False,True): ACTIONS.hit,
            (8,10,False,True): ACTIONS.hit,
            #2 threes
            (6,1,False,True): ACTIONS.hit,
            (6,2,False,True): ACTIONS.split,
            (6,3,False,True): ACTIONS.split,
            (6,4,False,True): ACTIONS.split,
            (6,5,False,True): ACTIONS.split,
            (6,6,False,True): ACTIONS.split,
            (6,7,False,True): ACTIONS.split,
            (6,8,False,True): ACTIONS.hit,
            (6,9,False,True): ACTIONS.hit,
            (6,10,False,True): ACTIONS.hit,
            #2 twos
            (4,1,False,True): ACTIONS.hit,
            (4,2,False,True): ACTIONS.split,
            (4,3,False,True): ACTIONS.split,
            (4,4,False,True): ACTIONS.split,
            (4,5,False,True): ACTIONS.split,
            (4,6,False,True): ACTIONS.split,
            (4,7,False,True): ACTIONS.split,
            (4,8,False,True): ACTIONS.hit,
            (4,9,False,True): ACTIONS.hit,
            (4,10,False,True): ACTIONS.hit,
        }

    def get_action(self, player_hand, house_up_card):

        if not player_hand.is_soft() and player_hand.score() >= 17:
            return ACTIONS.stand
        elif player_hand.is_soft() and player_hand.score() >= 19:
            return ACTIONS.stand

        state = (player_hand.score(), house_up_card, player_hand.is_soft(), player_hand.can_split())
        action = self.basic_strategy_policy[state]

        return action


class BasicAgent(BaseAgent):

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


class QLearningAgent(BaseAgent):

    def __init__(self, use_epsilon=True, epsilon=1, alpha=0.5, gamma=0.9, total_games=1000):

        self.q_table = self.load_policy()
        self.epsilon = epsilon
        self.use_epsilon = use_epsilon
        self.gamma = gamma
        self.alpha = alpha

        self.initial_epsilon = epsilon
        self.game_number = 1
        self.total_games = total_games

        self.total_exploration = 0

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

        rand = random.random()
        if self.use_epsilon and rand < self.epsilon:
            action = random.choice(player_hand.get_valid_actions())
            self.total_exploration += 1
        else:
            actions = self._get_max_q_actions(state, player_hand)
            #validate this is a valid action for the current hand
            actions = [action for action in actions if action in player_hand.get_valid_actions()]
            if not actions:
                actions = player_hand.get_valid_actions()

            action = random.choice(actions)

        return action

    def learn(self, player_hand, player_new_hand, house_up_card, reward, action):

        state = self._get_state(player_hand, house_up_card)
        new_state = self._get_state(player_new_hand, house_up_card)

        new_q = (1 - self.alpha) * self._get_q(state, action) + self.alpha * (reward + self.gamma * self._get_max_q(new_state))
        self.q_table[state][action] = new_q

    def end_cycle(self):

        self.epsilon = self.initial_epsilon - self.game_number / float(self.total_games)
        self.game_number += 1

    def learned_policy(self):

        return self.q_table.items()

    def load_policy(self):

        try:
            with open("policy.pickle", "r") as f:
                return pickle.loads(f.read())
        except:
            return {}

    def save_policy(self):

        with open("policy.pickle", "w") as f:
            f.write(pickle.dumps(self.q_table))


if __name__ == "__main__":
    #results_file = open("results.txt", "w")
    ia_game = IAGame()

    banca_wins = 0
    player_wins = 0
    draws = 0
    money = 0.0

    total_games = 100000
    agent = BasicAgent(score_to_stay=17)
    agent = BasicStrategyAgent()
    agent = QLearningAgent(use_epsilon=True, epsilon=0.5, total_games=total_games)

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

    #for key, values in sorted(agent.learned_policy()):
    #    print key, values

    print "Cantidad de veces que gano el jugador 1: {}".format(player_wins)
    print "Cantidad de veces que gano la banca: {}".format(banca_wins)
    print "Cantidad de veces que empataron: {}".format(draws)
    print "Cantidad total apostada $: {}".format(ia_game.total_bet)
    print "Cantidad neta $: {}".format(money)

    try:
        print "Total explorado: {}/{}".format(agent.total_exploration, agent.total_games)
    except:
        pass

    if agent.learned_policy():
        agent.save_policy()

    #results_file.write("Cantidad de veces que gano el jugador 1: {}\n".format(player_wins))
    #results_file.write("Cantidad de veces que gano la banca: {}\n".format(banca_wins))
    #results_file.write("Cantidad de veces que empataron: {}\n".format(draws))
    #results_file.write("Cantidad neta $: {}\n".format(money))

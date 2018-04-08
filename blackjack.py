import random
import time
import copy
from agents import SimpleAgent, QLearningAgent, BasicStrategyAgent, ACTIONS
from helpers import Log


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

        Log.log("+" * 80)
        Log.log(self.get_winner_message(payment))
        Log.log("+" * 80)

        return payment

    def pay_draw(self):

        Log.log("+" * 80)
        Log.log("Han empatado")
        Log.log("+" * 80)

        return 0

    def pay_backjack(self):

        bet = self.bet.get_value()
        payment = -bet if self.player.is_house() else self.get_backjack_payment(bet)

        Log.log("+" * 80)
        Log.log("BlackJack!")
        Log.log(self.get_winner_message(payment))
        Log.log("+" * 80)

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
                    #done if ACTIONS.stand, ACTIONS.double, busted, blackjack or reached 21
                    return_hands.append((player_original_hand, player_hand, action))
                    break
                else:
                    #keep the loop if ACTIONS.hit or ACTIONS.split
                    #if new hand score < previous hand score we should give a negative reward
                    if player_original_hand.score() > player_hand.score():
                        reward = -player_hand.bet.get_value() / 4.0
                    else:
                        reward = player_hand.bet.get_value() / 4.0
                        #reward = player_hand.bet.get_value()

                    agent.learn(player_original_hand, player_hand, house_up_card, reward, action, "Keep playing")

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

        Log.log(house_hand)
        money_total = 0.0

        for player_last_hand, player_hand, last_action in player_hands:

            Log.log(player_hand)

            if player_hand.busted():
                money_results = house_hand.pay_win()
            elif player_hand.black_jack():
                money_results = player_hand.pay_backjack()
            elif house_hand.busted():
                money_results = player_hand.pay_win()
            elif house_hand.black_jack():
                money_results = house_hand.pay_backjack()
            else:
                player_score = player_hand.score()
                house_score = house_hand.score()

                if player_score > house_score:
                    money_results = player_hand.pay_win()
                elif player_score < house_score:
                    money_results = house_hand.pay_win()
                else:
                    money_results = house_hand.pay_draw()

            reward = money_results
            if player_last_hand.score() > player_hand.score():
                #regarless of the match results, if the last score is higher than the new score reduce the reward
                reward = reward - (reward / 4.0)

            #if player_hand.busted():
                #negative *2 if busted
            #    reward *= reward

            agent.learn(player_last_hand, player_hand, house_up_card, reward, last_action, "End Match with {} hands".format(len(player_hands)))
            self.total_bet += player_hand.bet.get_value()

            money_total += money_results

        if money_results > 0:
            match_results = 1
        elif money_results < 0:
            match_results = -1
        else:
            match_results = 0

        return money_results, match_results


def play_stages(stages, fixed_epsilon=None, alpha=0.5, gamma=0.9):

    for stage in range(stages):

        use_epsilon = True

        epsilon = (stages - stage) / float(stages)
        ia_game = IAGame()

        house_wins = 0
        player_wins = 0
        draws = 0
        money = 0.0

        total_games = 1000
        #agent = SimpleAgent(score_to_stay=17)
        #agent = BasicStrategyAgent()
        agent = QLearningAgent(epsilon=epsilon, fixed_epsilon=fixed_epsilon, alpha=alpha, gamma=gamma, total_games=total_games)

        for game_number in range(total_games):

            Log.log("*" * 80)
            Log.log("Juego {}".format(game_number))
            money_results, match_results = ia_game.play(agent)
            Log.log("*" * 80)

            if match_results < 0:
                house_wins += 1
            elif match_results > 0:
                player_wins += 1
            else:
                draws += 1
            Log.log("")

            money += money_results
            agent.end_cycle()

        print "Cantidad de veces que gano el jugador 1: {}".format(player_wins)
        print "Cantidad de veces que gano la banca: {}".format(house_wins)
        print "Cantidad de veces que empataron: {}".format(draws)
        print "Cantidad total apostada $: {}".format(ia_game.total_bet)
        print "Cantidad neta $: {}".format(money)

        try:
            print "Total explorado: {}/{}".format(agent.total_exploration, agent.total_games)
        except:
            pass

        if agent.learned_policy():
            agent.save_policy(money)

        agent.save_results({"money": money, "player_wins": player_wins, "house_wins": house_wins, "draws": draws, "total_games": total_games, "epsilon": epsilon })

        print "Saving policy..."
        #time.sleep(3)


if __name__ == "__main__":

    #play_stages(250)
    #play_stages(250, fixed_epsilon=0.1)
    play_stages(5000, fixed_epsilon=0.0, gamma=1)

    from plot import plot
    plot("QLearningAgent")

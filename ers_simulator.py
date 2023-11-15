"""
Simulate games of ERS using the following parameters:
- num games
- probability of one person getting a slap
- (future): probability of each of more than one person getting a slap

Return:
- win rate of each player
"""
# from queue import Queue
from collections import deque
from enum import Enum
import random
from matplotlib import pyplot as plt
import numpy as np

class Var(Enum):
    SLAP_PROB = 0
    CARDS_DEALT = 1


class Deck:
    def __init__(self, cards=None):
        """Create a deck which is a deque with the top being the left side"""
        if cards == None:
            self.init_full_deck()
        else:
            self.cards = cards
    
    def init_full_deck(self):
        values = 'A23456789TJQK'
        suits = 'SHCD'
        self.cards = deque()
        for val in values:
            for suit in suits:
                self.cards.append(val + suit)
        
        self.shuffle()
    
    def set_deck(self, cards):
        self.cards = cards.copy()
    
    def draw_card(self):
        return self.cards.popleft()
    
    def add_deck(self, deck):
        """Add cards to bottom of deck"""
        self.cards.extend(deck.cards)
        deck.reset()
    
    def add_card(self, card):
        """Add card to top of deck"""
        self.cards.appendleft(card)

    def deal(self, players=2, cards_to_p1=None):
        decks = []
        for player in range(players):
            decks.append(Deck(deque()))
        
        # if specified, draw the first n cards to p1 and the rest to p2
        if cards_to_p1 is not None:
            for _ in range(cards_to_p1):
                decks[0].add_card(self.draw_card())
            while len(self.cards):
                decks[1].add_card(self.draw_card())
            
            return tuple(decks)

        # while cards remaining, deal in alternating order to players
        while len(self.cards):
            for player in range(players):
                decks[player].add_card(self.draw_card())
        
        return tuple(decks)
            
    def is_slap(self):
        double = len(self.cards) >= 2 and Deck.cards_equal(self.cards[0], self.cards[1])
        sandwich = len(self.cards) >= 3 and Deck.cards_equal(self.cards[0], self.cards[2])

        return double or sandwich
    
    def empty(self):
        return not len(self.cards)

    def shuffle(self):
        random.shuffle(self.cards)
    
    def reset(self):
        self.cards = deque()
    
    @staticmethod
    def cards_equal(card1, card2):
        return card1[0] == card2[0]
        


def run_game(num_games=10000, slap_prob=0.5, cards_to_p1=None):
    # num_games = 10000
    # slap_prob = 0.55
    NUM_PLAYERS = 2
    FACE_CARDS = { 'J': 1, 'Q': 2, 'K': 3, 'A': 4 }
    p1_wins = 0
    p2_wins = 0
    all_turns_taken = []
    for game in range(num_games):
        deck = Deck()
        
        # deal cards
        decks = deck.deal(2, cards_to_p1)
        p1_deck = decks[0]
        p2_deck = decks[1]
        assert deck.empty()

        # alternate placing cards into a center deck, checking for slaps
        current_player = random.choice(range(NUM_PLAYERS))
        face_card_seen = False
        turns_taken = 0
        while not p1_deck.empty() and not p2_deck.empty():
            turns_taken += 1
            # add card to top of center deck
            card = decks[current_player].draw_card()
            deck.add_card(card)

            # check for slap or move to next player if not a slap
            if deck.is_slap():
                rand_num = random.random()
                if rand_num < slap_prob:
                    p1_deck.add_deck(deck)
                else:
                    p2_deck.add_deck(deck)

                face_card_seen = False
            elif deck.cards[0][0] in FACE_CARDS:
                face_card_seen = True
                face_card_count = FACE_CARDS[deck.cards[0][0]]
                current_player = (current_player + 1) % NUM_PLAYERS
            else:
                # not a slap
                # stays same player if face card
                if face_card_seen:
                    # if face cards run out, other player gets the cards
                    face_card_count -= 1
                    if face_card_count == 0:
                        opposite_player = (current_player + 1) % NUM_PLAYERS
                        decks[opposite_player].add_deck(deck)
                        face_card_seen = False
                else: # switch player if not a face card
                    current_player = (current_player + 1) % NUM_PLAYERS


        if p1_deck.empty():
            p2_wins += 1
        if p2_deck.empty():
            p1_wins += 1
        all_turns_taken.append(turns_taken)
    
    # print(f'p1 ({slap_prob}): {p1_wins}/{num_games} = {p1_wins / num_games}')
    # print(f'p2 ({1 - slap_prob}): {p2_wins}/{num_games} = {p2_wins / num_games}')
    return p1_wins / num_games, np.average(all_turns_taken)

def run_games(num_games, vary, slap_prob=0.5):
    if vary == Var.SLAP_PROB:
        slap_probs = np.linspace(0.5, 1, 10)
        win_probs = []
        all_turns_taken = []
        for slap_prob in slap_probs:
            win_prob, turns_taken = run_game(num_games, slap_prob)
            win_probs.append(win_prob)
            all_turns_taken.append(turns_taken)

        independent_var = slap_probs
    elif vary == Var.CARDS_DEALT:
        cards_to_p1 = [int(x) for x in np.linspace(1, 51, 10)]
        win_probs = []
        all_turns_taken = []
        for num_cards in cards_to_p1:
            win_prob, turns_taken = run_game(num_games, slap_prob, num_cards)
            win_probs.append(win_prob)
            all_turns_taken.append(turns_taken)
        
        independent_var = cards_to_p1
    
    return independent_var, win_probs, all_turns_taken

        

def plot_win_rates(slap_probs, win_probs):
    plt.plot(slap_probs, win_probs)
    plt.title('ERS win rate based on probability of winning a slap')
    plt.xlabel('Probability of winning a slap')
    plt.ylabel('Probability of winning the game')
    plt.show()

def plot_turns_taken(slap_probs, all_turns_taken):
    plt.plot(slap_probs, all_turns_taken)
    plt.title('ERS avg turns taken for game to finish based on slap probability')
    plt.xlabel('Probability of winning a slap')
    plt.ylabel('Turns taken')
    plt.show()

def plot_handicaps(cards_to_p1, win_probs, slap_prob):
    plt.plot(cards_to_p1, np.full(len(cards_to_p1), 0.5))
    plt.plot(cards_to_p1, win_probs)
    plt.title(f'ERS win rate based on cards dealt with slap prob of {slap_prob}')
    plt.xlabel('Cards dealt to the first player')
    plt.ylabel('Probability of winning')
    plt.show()

def main():
    # print(run_game(slap_prob=1))
    # assert False

    NUM_GAMES = 3000

    slap_prob = 0.70
    cards_to_p1, win_probs, all_turns_taken = run_games(NUM_GAMES, Var.CARDS_DEALT, slap_prob)
    plot_handicaps(cards_to_p1, win_probs, slap_prob)

    slap_probs, win_probs, all_turns_taken = run_games(NUM_GAMES, Var.SLAP_PROB)
    plot_win_rates(slap_probs, win_probs)

    

    


if __name__ == '__main__':
    main()
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
import random


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

    def deal(self, players=2):
        decks = []
        for player in range(players):
            decks.append(Deck(deque()))
        
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
        


def main():
    NUM_GAMES = 10000
    SLAP_PROB = 0.55
    NUM_PLAYERS = 2
    FACE_CARDS = { 'J': 1, 'Q': 2, 'K': 3, 'A': 4 }
    p1_wins = 0
    p2_wins = 0
    for game in range(NUM_GAMES):
        deck = Deck()
        
        # deal cards
        decks = deck.deal(2)
        p1_deck = decks[0]
        p2_deck = decks[1]
        assert deck.empty()

        # alternate placing cards into a center deck, checking for slaps
        current_player = random.choice(range(NUM_PLAYERS))
        face_card_seen = False
        while not p1_deck.empty() and not p2_deck.empty():
            # add card to top of center deck
            card = decks[current_player].draw_card()
            deck.add_card(card)

            # check for slap or move to next player if not a slap
            if deck.is_slap():
                rand_num = random.random()
                if rand_num < SLAP_PROB:
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
    
    print(f'p1 ({SLAP_PROB}): {p1_wins}/{NUM_GAMES} = {p1_wins / NUM_GAMES}')
    print(f'p2 ({1 - SLAP_PROB}): {p2_wins}/{NUM_GAMES} = {p2_wins / NUM_GAMES}')


if __name__ == '__main__':
    main()
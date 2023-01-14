from dataclasses import dataclass, field
import random

RANKS = '2 3 4 5 6 7 8 9 10 Jack Queen King Ace'.split()
SUITS = '♧ ♢ ♡ ♤'.split()

# Should have 52(+?) playing cards,
# Plus a method to return a Hand from itself
class Deck:
    def __init__(self, card = None, hand = None, shuffled = True) -> None:
        self.cards = []
        self.shuffled = shuffled
        self._card = card or Card
        self._hand = hand or Hand
        for suit in SUITS:
            for i in range(2, 11):
                card = self._card(self, suit, str(i), i)
                self.cards.append(card)
            for i, royal in enumerate(RANKS[-4:]):
                card = self._card(self, suit, royal, 10 + i)
                self.cards.append(card)
        if shuffled:
            random.shuffle(self.cards)
    
    def __str__(self):
        cards = ', '.join(str(c) for c in self.cards)
        return f'{self.__class__.__name__}({cards})'
    
    def __len__(self):
        return len(self.cards)
    
    def draw(self):
        """Draws and removes a card from the top of the deck."""
        return self.cards.pop()
    
    def shuffle_into(self, card):
        """Adds a card to the deck, then shuffles it"""
        self.cards.append(card)
        random.shuffle(self.cards)
        self.shuffled = True
    
    def place_bottom(self, card):
        """Adds a card to the bottom of the deck"""
        self.cards = [card] + self.cards
    
    def place_top(self, card):
        """Adds a card to the top of the deck"""
        self.cards.append(card)
    
    def hand(self, cards: int):
        """Creates a Hand from this deck with <cards> cards"""
        return self._hand(self, cards)

@dataclass(order=True)
class Card:
    sort_index: int = field(init=False, repr=False)
    deck: Deck = field(compare = False)
    suit: str = field(compare=False)
    rank: str = field(compare=False)
    worth: int
    up: bool = field(default=True)

    def flip(self):
        self.up = not self.up
    
    @property
    def value(self):
        if self.up:
            return self.worth
        else:
            return -1

    def shuffle_into(self):
        self.deck.shuffle_into(self)

    def place_bottom(self):
        self.deck.place_bottom(self)

    def place_top(self):
        self.deck.place_top(self)

    def __post_init__(self):
        self.sort_index = (RANKS.index(self.rank) * len(SUITS)
                           + SUITS.index(self.suit))

    def __str__(self):
        if self.up:
            return f'{self.suit}{self.rank}'
        else:
            return '??'

    def __repr__(self):
        return str(self)

class Hand:
    def __init__(self, deck: Deck, card_count: int, cards = None) -> None:
        self.deck = deck
        self.cards = []
        if cards is not None:
            self.cards = cards
        else:
            for _ in range(card_count):
                self.hit()

    def __str__(self):
        cards = ', '.join(str(c) for c in self.cards)
        return f'{self.__class__.__name__}({cards})'

    @property
    def hand(self, force=False):
        """Turns this hand's cards into a string"""
        cards = []
        for c in self.cards:
            if not c.up and force:
                c.flip()
                cards.append(str(c))
                c.flip()
            else:
                cards.append(str(c))
        return ', '.join(cards)

    @property
    def remaining(self):
        return len(self.cards)

    def hit(self):
        """Draws a card from the deck and adds it to the hand"""
        card = self.deck.draw()
        self.cards.append(card)
    
    def draw(self, n = None):
        """Draws a card(s) from the hand, removing and returning it in the process"""
        if n == None:
            n = 1
        
        cards = []
        for _ in range(n):
            cards.append(self.cards.pop())
        return cards if len(cards) > 1 else cards[0]

    def place_bottom(self, card):
        """Adds a card to the bottom of the hand"""
        if isinstance(card, list):
            card = card.extend(self.cards)
            self.cards = card
        self.cards = [card] + self.cards
    

if __name__ == '__main__':
    try:
        d = Deck()
        print(d)
        hand = d.hand(3)
        print(hand.hand)
    except Exception as e:
        print(e)
    while True:
        try:
            exec(input('input: '))
        except Exception as e:
            print(e)
    input('hi')




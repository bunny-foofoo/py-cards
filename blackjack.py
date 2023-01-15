from dataclasses import dataclass
from cards import Deck, Hand

#TODO: Add Insurance
#TODO: Add Splits
#TODO: Add Doubles
#TODO: Add case for Round 1 Player BJ becoming Push
#TODO: Add Reshuffling

class Results:
    def __init__(self, gg = False, winners = None, losers = None):
        self.gg = gg
        self._winners = winners
        self._losers = losers
    
    @property
    def winners(self):
        winners = []
        for win, amount in self._winners.items():
            if amount == 0:
                winners.append(f'{win} pushed, keeping their bet.')
            else:
                winners.append(f'{win} won ${amount}')
        return ', '.join(winners)

    @property
    def losers(self):
        losers = []
        for loss, amount in self._losers.items():
            losers.append(f'{loss} lost ${-amount}')
        return ', '.join(losers)

class BlackjackHand(Hand):
    def __init__(self, *args, **kwargs):
        self.standing = False
        self.bet = kwargs.pop('bet', 0)
        self.earnings = None
        self.still_in = True
        self.player_id = None
        super().__init__(*args, **kwargs)
    
    def stand(self):
        self.standing = True
    
    def game_over(self, earnings_multiplier):
        self.earnings = int(self.bet * earnings_multiplier)
        self.still_in = False
    
    def win(self):
        self.game_over(1)
    
    def lose(self):
        self.game_over(-1)
    
    def push(self):
        self.game_over(0)

    @property
    def blackjack(self):
        """Computes score for Blackjack"""
        score = 0
        aces = 0
        for card in self.cards:
            if not card.up:
                continue
            if not card.rank == 'Ace':
                score += min(10, card.value)
            else:
                aces += 1
        for _ in range(aces):
            if score + 11 > 21:
                score += 1
            else:
                score += 11
        return score

class Blackjack:
    def __init__(self):
        self.deck = Deck(hand=BlackjackHand)
        self.players = []
        self.dealer = None
        self.playing = False
        self.rounds = 0
    
    def draw(self, gg = False):
        if self.rounds == 0:
            return 'Not started'
        table_view = ['~ Blackjack ~']
        for player in (self.players):
            player_hand = f'{player.player_id} ({player.blackjack}): {player.hand}'
            if not player.still_in:
                player_hand = f'{player_hand} (Out)'
            elif player.standing:
                player_hand = f'{player_hand} | Standing'
            table_view.append(player_hand)
        dealer_hand = f'Dealer ({self.dealer.blackjack}): {self.dealer.hand}'
        if self.dealer.standing:
            dealer_hand = f'{dealer_hand} | Standing'
        table_view.append(dealer_hand)
        return '\n'.join(table_view)
    
    def hit(self):
        dealer = self.dealer
        if not dealer.cards[1].up:
            dealer.cards[1].flip()
        
        all_standing = True
        for player in self.players:
            all_standing = all_standing and player.standing
            if player.blackjack < 21 and not player.standing:
                player.hit()
        while True:
            if dealer.blackjack < 17:
                dealer.hit()
            else:
                dealer.standing = True
            if dealer.standing or not all_standing:
                break
    
    def start(self, player_count: int = 1):
        self.dealer = self.deck.hand(2)
        self.dealer.cards[1].flip()
        players = []
        for i in range(max(1, player_count)):
            player = self.deck.hand(2)
            player.player_id = f'Player {i + 1}' #TODO: implement this using py class properties
            players.append(player)
        self.players = players
        return self.dealer, tuple(self.players)
    
    def _score(self):
        updates = []
        # Players go first
        dealer = self.dealer
        # If player busts, they lose bet, even if dealer busts too
        #players = list(p.blackjack for p in self.players)
        players = self.players
        standers = []
        for player in players:
            if not player.still_in:
                continue
            if player.blackjack > 21: # Busts (player)
                player.lose()
                updates.append(f'{player.player_id} busts!')
            elif player.blackjack == 21: # Blackjack (player)
                player.game_over(1.5)
                updates.append(f'{player.player_id} got blackjack!')
            elif player.standing:
                standers.append(player)
        # If dealer busts, all players who stood at 1x bet
        if dealer.blackjack > 21: # Busts (dealer)
            for player in standers:
                player.win()
            dealer.still_in = False
            updates.append(f'dealer busts!')
        elif dealer.blackjack == 21:
            updates.append(f'dealer gets blackjack!')
            for player in players:
                if not player.still_in:
                    continue
                if player.blackjack == dealer.blackjack:
                    player.push()
                    updates.append(f'{player.player_id} and the dealer push.')
                else:
                    player.lose()
                    updates.append(f'{player.player_id} gets beat!')
        # If dealer stands at 21 or less, dealer pays the bet
        # of any player having a higher total (not exceeding 21)
        # and collects the bet of any player having a lower total
        # If there is a stand-off (push), no chips are paid out or collected
        elif dealer.standing:
            updates.append(f'dealer stands!')
            for player in standers:
                pbj = player.blackjack
                dbj = dealer.blackjack
                if pbj > dbj: # Higher than dealer
                    player.win()
                    updates.append(f'{player.player_id} beat the dealer!')
                elif pbj < dbj: # Lower than dealer
                    player.lose()
                    updates.append(f'{player.player_id} lost to the dealer!')
                else: # Same as dealer
                    player.push()
                    updates.append(f'{player.player_id} and the dealer push!')
            dealer.still_in = False

        gg = False
        still_going = sum(p.still_in for p in self.players) > 0
        if not still_going or not dealer.still_in:
            updates.append(f'Game over.')
            gg = True
        
        return gg, updates

    def score(self):
        self.rounds += 1
        gg, result = self._score()
        if gg:
            print(self.draw(gg=True))
            return True, tuple((result, self.pay_out()))
        return False, result
    
    def pay_out(self):
        pays = []
        for player in self.players:
            if player.earnings is not None:
                if player.earnings < 0:
                    pays.append(f'{player.player_id} lost ${-player.earnings}')
                elif player.earnings > 0:
                    pays.append(f'Paid {player.player_id} ${player.earnings}')
        return pays


if __name__ == '__main__':
    bj = Blackjack()
    print('Welcome! First up,')
    player_count = int(input('How many players will there be? '))
    players = []
    dealer, players = bj.start(player_count)
    print(f'Alright! {len(players)} players!')
    for player in players:
        player_id = player.player_id
        bet = int(input(f'{player_id}: What will your bet be? $'))
        player.bet = bet
        print(f'{player_id} is  betting ${bet}')
    print('Starting the game...')
    # Game loop
    while True:
        # Check for naturals right off the bat
        # And for later rounds, we'll check scores right here too
        # Handle scoring / game end
        game_over, info = bj.score()
        # if game_over: info is payout_info, else info is updates
        if not game_over:
            print('\n'.join(info))
        else:
            updates, payments = info
            print('\n'.join(updates))
            print('Bets: ')
            print('\n'.join(payments))
            break
        # Draw the table and ask for actions
        print(bj.draw())
        #* 1. Ask all the players if they want to hit or stand
        for player in players:
            if player.standing:
                continue
            player_id = player.player_id
            standing = input(f'{player_id}: Do you want to hit or stand? [hit/stand]: ').startswith('s')
            if standing:
                print(f'{player_id} will stand.')
                player.stand()
            else:
                print(f'{player_id} will hit.')
        bj.hit()


    

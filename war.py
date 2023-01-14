from cards import Deck

class TooManyRounds(Exception):
	pass

class Player:
	def __init__(self, hand) -> None:
		self.hand = hand
		self.spoils = [] # spoils of war (cards collected after rounds)
	
	@property
	def remaining(self):
		return self.hand.remaining


class Game:
	"""A game of War"""

	def __init__(self) -> None:
		self.deck = Deck()
		self.player_one = self.deck.hand(26)
		self.player_two = self.deck.hand(26)
		self.round = 0
	
	def outcome(self, card1, card2):
		# 0 if tie
		# 1 if card1 wins
		# 2 if card2 wins
		
		try:
			if card1.worth == card2.worth:
				return 0
			elif card1.worth > card2.worth:
				return 1
			elif card1.worth < card2.worth:
				return 2
		except AttributeError as e:
			print('card1:', card1)
			print('card2:', card2)
			raise(e)


	def play_round(self, bounty = None):
		player1_card = self.player_one.draw()
		player2_card = self.player_two.draw()

		if bounty is None:
			bounty = []
		bounty.extend([player1_card, player2_card])

		outcome = self.outcome(player1_card, player2_card)

		if outcome == 1 or self.player_two.remaining < 4:
			victor = self.player_one
		elif outcome == 2 or self.player_one.remaining < 4:
			victor = self.player_two
		elif outcome == 0:
			bounty.extend(self.player_one.draw(3))
			bounty.extend(self.player_two.draw(3))
			#print('went to war for', bounty)
			self.play_round(bounty=bounty)

		if outcome in (1,2):
			self.round += 1
			# if self.round <= 10:
			# 	print(f"{self.round}) Player {outcome} won the round.\n")
			if self.round == 100_000:
				print("Game went on too long (100,000 rounds).")
				print('Player 1:', self.player_one)
				print('Player 2:', self.player_two)
				raise TooManyRounds()
			#print('bounty:', bounty, '\n')
			for card in bounty:
				victor.place_bottom(card)
	
	def start(self):
		while self.player_one.remaining * self.player_two.remaining != 0:
			self.play_round()
		print('game over after', self.round, 'rounds')
		if self.player_one.remaining != 0:
			print('The winner is player 2')
		else:
			print('The winner is player 1')

if __name__ == '__main__':
	game = Game()
	game.start()
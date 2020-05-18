from engines import RandomEngine
from itertools import chain
from random import choice

class HitShip:
	def __init__(self, coord):
		self.coord = coord
		self.knownSunk = False #Has to be sunk as a single boat type
		self.sinkParty = -1 #The ship which was sunk when known
		self.vagueSink = False #Unclear what type of boat the hit is
		self.sinkGroup = {} #The possible positions of boats which this is part of

	def clearSink(self, ship):
		self.knownSunk = True
		self.sinkParty = ship

	def partySink(self, ship, group):
		assert not self.knownSunk
		self.vagueSink = True
		if not ship in self.sinkGroup.keys():
			self.sinkGroup[ship] = []
		self.sinkGroup[ship].append(group)

	def __str__(self):
		return "Sunk " + str(self.sinkParty) if self.knownSunk else "Vague sink of " + str(self.sinkGroup) if self.vagueSink else "Hit"

class GameTheoreticEngine(RandomEngine):
	def __init__(self, game):
		super().__init__(game)

		self.trailingShips = {}

	def attackShips(self):
		currentBoard = self.opponentsShips()
		print(currentBoard)

		weights = self.searchingWeights()
		maxWeighting = max(weights.keys())

		coord = choice(weights[maxWeighting])
		print(currentBoard[coord])
		assert coord in self.game.available_moves()
		if not self.game.fire(coord):
			print(self.opponentsShips())
			print(self.trailingShips)
			raise RuntimeError("It's gone wrong hitting " + str(coord))

		if self.didHit(coord):
			if self.didSink(coord):
				#The number of squares the sunk ship was
				ship = self.game.ship_positions[self.game.player_state][coord]
				positions = self.possibleSinks(coord, self.game.ships[ship])

				if len(positions) == 1:
					#Unambigous sink
					for position in positions[0]:
						del self.trailingShips[position]
						purgeSinkGroup(position)
				else:
					#Number of possible sinks, not ideal
					common = set(position[0]) & set(chain.from_iterable(positions[1:]))

					for position in common:
						self.trailingShips[position].clearSink(ship)
						purgeSinkGroup(position)

					for position in positions:
						for coord in position:
							if coord not in common:
								self.trailingShips[coord].partySink(ship, position)
			else:
				self.trailingShips[coord] = HitShip(coord)
		else:
			print("Missed " + str(coord))

	def searchingWeights(self):
		known = self.opponentsShips()
		weights = {}

		for ship in self.game.ships:
			if self.game.ships_remaining[self.game.player_state, self.game.ships.index(ship)] < 1: continue #All sunk
			for y in range(10 - ship):
				for x in range(10 - ship):
					for (xOffset, yOffset) in ((1, 0), (0, 1)):
						room = True

						for offset in range(ship):
							if known[x + (offset * xOffset), y + (offset * yOffset)] < 0:
								room = False #No room
								break

						if room:
							for offset in range(ship):
								coord = (x + (offset * xOffset), y + (offset * yOffset))
								if coord not in weights:
									weights[coord] = 0
								weights[coord] += 1

		#If we have some unfinished ships we should go after as more of a priority
		if len(self.trailingShips) > 0:
			longestLeft = max(self.game.ships[ship] for ship in range(5) if self.game.ships_remaining[self.game.opposite_player_state, ship] > 0)
			for (coord, hit) in self.trailingShips.items():
				if not hit.knownSunk:
					for x in range(coord[0] - longestLeft, coord[0] + longestLeft):
						if x < 0 or x > 9: continue
						coord = (x, coord[1])
						if coord not in weights:
							weights[coord] = 0
						weights[coord] += longestLeft - 1

					for y in range(coord[1] - longestLeft, coord[1] + longestLeft):
						if y < 0 or y > 9: continue
						coord = (coord[0], y)
						if coord not in weights:
							weights[coord] = 0
						weights[coord] += longestLeft - 1

		squareWeights = {}
		totalPlacements = sum(weights.values())
		for (coord, placements) in weights.items():
			if coord in self.trailingShips or coord in known: continue #Avoid trying to hit already hit places
			weight = placements / totalPlacements
			if weight not in squareWeights:
				squareWeights[weight] = []
			squareWeights[weight].append(coord)

		return squareWeights

	def didHit(self, coord):
		return self.game.state[self.game.player_state, 0, coord[0], coord[1]] == -1

	#Expected to be called after self.game.fire on coordinates that had a ship
	def didSink(self, coord):
		print("Checking ship of type " + str(self.game.ship_positions[self.game.player_state][coord]))
		"""Whether the ship which was a (x, y) has been sunk"""
		return self.game.ships_remaining[self.game.player_state,
										 self.game.ship_positions[self.game.player_state][coord]] == 0

	def possibleSinks(self, coord, length):
		x, y = coord
		placements = []

		for shift in range(-length, 0):
			possible = True

			for offset in range(length):
				coord = (x + shift + offset, y)
				if not (0 <= coord[0] < 10) or coord not in self.trailingShips or self.trailingShips[coord].knownSunk:
					possible = False
					break

			if possible:
				placements.append([(x + shift + offset, y) for offset in range(length)])

		for shift in range(-length, 0):
			possible = True

			for offset in range(length):
				coord = (x, y + shift + offset)
				if not (0 <= coord[1] < 10) or coord not in self.trailingShips or self.trailingShips[coord].knownSunk:
					possible = False
					break

			if possible:
				placements.append([(x, y + shift + offset) for offset in range(length)])

		assert len(placements) > 0, "Could find sink around " + str(x) + ", " + str(y)
		return placements

	def purgeSinkGroup(self, containingCoord):
		clarity = set()

		for hit in self.trailingShips.values():
			if hit.knownSunk: continue #Already clear

			for (ship, groups) in hit.sinkGroup.items():
				if containingCoord in groups:
					if len(hit.sinkGroup[ship]) == 1:
						hit.sinkGroup.pop(ship)
					else:
						groups.remove(groups.index(groups))
					clarity.add(ship)

		for ship in clarity:
			clear = True

			for (coord, hit) in self.trailingShips.items():
				if hit.vagueSink and ship in hit.sinkGroup:
					clear = len(hit.sinkGroup[ship]) == 1
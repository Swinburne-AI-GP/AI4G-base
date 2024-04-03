"""Game Entities for the PlanetWars world

There are two game entity classes: `Planet` and `Fleet`. Both are derived from
an `Entity` base class. Conceptually both planets and fleets contain "ships",
and have a unique game id given to them.

Planets are either "owned" by a player or neutral. When occupied by a player,
planets create new ships (based on their `growth_rate`).

Fleets are launched from a planet (or fleet) and sent to a target planet.
Fleets are always owned by one of the players.

"""
import math
import uuid

NEUTRAL_ID = '0'
FLEET_SPEED = 20
SCALE_FACTOR = 1000

class Entity():

	
	''' Abstract class representing entities in the 2d game world.
		See Fleet and Planet classes.
	'''

	def __init__(self, x, y, ID=None, owner=None, ships=0):
		if ID:
			self.ID = ID
		else:
			self.ID = str(uuid.uuid1())

		self.x = x*SCALE_FACTOR
		self.y = y*SCALE_FACTOR
		self.ships = ships
		if owner:
			self.owner = owner
		else:
			self.owner = NEUTRAL_ID
		self.vision_age = 0
		# self._name = "%s:%s" % (type(self).__name__, str(id))


	#distance_to does not sqrt by default - still effective for comparisons etc., but not strictly accurate.
	#if you need the precise distance for whatever reason, pass in sqrt = True
	#can pass in an entity, or an x and y param (e.g. if your point is not an entity)
	def distance_to(self, other=None, x=None, y=None, sqrt=False):
		if other:
			if self.ID == other.ID:
				return 0.0
			dx = self.x - other.x
			dy = self.y - other.y
		else:
			dx = self.x - x
			dy = self.y - y
		if sqrt:
			return math.sqrt(dx * dx + dy * dy)
		else:
			return dx * dx + dy * dy

	def remove_ships(self, ships):
		if ships <= 0:
			raise ValueError("%s (owner %s) tried to send %d ships (of %d)." %
							 (self.ID, self.owner, ships, self.ships))
		if self.ships < ships:
			raise ValueError("%s (owner %s) can't remove more ships (%d) then it has (%d)!" %
							 (self.ID, self.owner, ships, self.ships))
		self.ships -= ships

	def add_ships(self, ships):
		if ships < 0:
			raise ValueError("Cannot add a negative number of ships...")
		self.ships += ships

	def update(self):
		raise NotImplementedError("This method cannot be called on this 'abstract' class")

	def is_in_vision(self):
		return self.vision_age == 0

	def in_range(self, entities):
		''' Returns a list of entity id's that are within vision range of this entity.'''
		limit = self.vision_range()
		return [p.ID for p in entities if self.distance_to(p) <= limit]

	def __str__(self):
		return "%s, owner: %s, ships: %d" % (self.ID, self.owner, self.ships)

	def serialise(self):
		return {
			'ID': self.ID,
			'owner': self.owner,
			'ships': self.ships,
			'x': self.x/SCALE_FACTOR,
			'y': self.y/SCALE_FACTOR
		}


class Planet(Entity):

	''' A planet in the game world. When occupied by a player, the planet
		creates new ships each time step (when `update` is called). Each
		planet also has a `vision_range` which is partially proportional
		to the growth rate (size).
	'''

	def __init__(self, x, y, ID=None, owner=None, ships=None, growth=1):
		super().__init__(x, y, ID, owner, ships)
		self.growth = growth

	def update(self):
		''' If the planet is owned, grow the number of ships (advancement). '''
		if self.owner != NEUTRAL_ID:
			self.add_ships(self.growth)

	def vision_range(self):
		return 100+50*self.growth+self.ships
	
	def serialise(self):
		serial = super().serialise()
		serial['growth'] = self.growth
		return serial

class Fleet(Entity):
	''' A fleet in the game world. Each fleet is owned by a player and launched
		from either a planet or a fleet (mid-flight). All fleets move at the
		same speed each game step.

		Fleet id values are deliberately obscure (using UUID) to remove any
		possible value an enemy players might gather from it.
	'''


	def __init__(self, ID=None, owner=None, ships=None, src=None, dest=None, x=None, y=None):
		super().__init__(
			x or src.x/SCALE_FACTOR,
			y or src.y/SCALE_FACTOR,
			ID, owner, ships)
		self.dest = dest
		# we cache heading because it is unlikely to change from tick to tick
		self.heading = math.atan2((self.dest.y-self.y),(self.dest.x-self.x))

	# def in_range(self, entities, ignoredest=True):
	# 	result = super(Fleet, self).in_range(entities)
	# 	if (not ignoredest) and (self.turns_remaining == 1) and (self.dest not in result):
	# 		result.append(self.dest)
	# 	return result

	def vision_range(self):
		return 50+self.ships*2.5

	def update(self):
		''' Move the fleet (progress) by one game time step.'''
		# update position
		self.x += math.cos(self.heading) * FLEET_SPEED
		self.y += math.sin(self.heading) * FLEET_SPEED

	def serialise(self):
		return super().serialise()
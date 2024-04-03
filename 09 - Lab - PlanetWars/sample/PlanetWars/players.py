import uuid
from entities import NEUTRAL_ID

class Player(object):
	# This is used by the actual `PlanetWars` game instance to represent each
	# player, and also finds, creates and contains the "bot" controller
	# instance specified by `name`.
	#
 	# Each game step `update` the PlanetWars game updates the info held by the player,
	# taking into account the entities the players is actually aware of
	# The Player then passes itself to the bot controller, which then issues orders
	# (via the Player order methods). The orders may be ignored if they are invalid.
	# Player contains a range of helper functions for prvoiding useful views on the facade
	#
 	# The Player facade represents a "fog-of-war" view of the true game
	# environment. A player bot can only "see" what is in range of it's own
	# occupied planets or fleets in transit across the map. This creates an
	# incentive for bots to exploit scout details.
 
	def __init__(self, ID, name):
		self.ID = ID  # as allocated by the game
		self.name = name.replace('.py', '')  # accept both "Dumbo" or "Dumbo.py"
		#self.log = log or (lambda *p, **kw: None)
		self.orders = []
		self.ships = 0
		self._alive = True
		self.planets = {}	#actually the planets in the facade.. rename?
		self.fleets = {}	#actually the fleets in the facade.. rename?

		if self.ID != NEUTRAL_ID:
			# Create a controller object based on the name
			# - Look for a ./bots/BotName.py module (file) we need
			mod = __import__('bots.' + name)  # ... the top level bots mod (dir)
			mod = getattr(mod, name)	   # ... then the bot mod (file)
			cls = getattr(mod, name)	  # ... the class (eg DumBo.py contains DumBo class)
			self.controller = cls()

	def __str__(self):
		return "%s(id=%s)" % (self.name, str(self.id))
	
	def serialise(self):
		return {
			'ID': self.ID,
			'name': self.name
		}

	def update(self):
		# Assumes gameinfo facade details are ready - let the bot issue orders!
		# Note: the bot controller has a reference to our *_order methods.
		if self.ID != NEUTRAL_ID:
			self.controller.update(self)

	def fleet_order(self, src_fleet, dest, ships):
		''' Order fleet to divert (some/all) fleet ships to a destination planet.
			Note: this is just a request for it to be done, and fleetid is our reference
			if it is done, but no guarantee - the game decides and enforces the rules.
		'''
		# If source fleet splitting we'll need a new fleet_id else keep old one
		fleetid = uuid.uuid4() if ships < src_fleet.ships else src_fleet.ID
		self.orders.append(('fleet', src_fleet.ID, fleetid, ships, dest.ID))
		return fleetid

	def planet_order(self, src_planet, dest, ships):
		''' Order planet to launch a new fleet to the destination planet.
			Note: this is just a request for it to be done, and fleetid is our reference
			if it is done, but no guarantee - the game decides and enforces the rules.
		'''
		fleetid = uuid.uuid4()
		self.orders.append(('planet', src_planet.ID, fleetid, ships, dest.ID))
		return fleetid

	# Helper functions
	# It is strongly recommended that you cache the results of these function calls
	# Multiple calls within the same game tick will produce the same results
	def _my_planets(self):
		return dict([(k, p) for k, p in self.planets.items() if p.owner == self.ID])

	def _enemy_planets(self):
		return dict([(k, p) for k, p in self.planets.items() if p.owner not in (NEUTRAL_ID, self.ID)])

	def _not_my_planets(self):
		return dict([(k, p) for k, p in self.planets.items() if p.owner != self.ID])

	def _neutral_planets(self):
		return dict([(k, p) for k, p in self.planets.items() if p.owner == NEUTRAL_ID])

	def _my_fleets(self):
		return dict([(k, f) for k, f in self.fleets.items() if f.owner == self.ID])

	def _enemy_fleets(self):
		return dict([(k, f) for k, f in self.fleets.items() if f.owner != self.ID])

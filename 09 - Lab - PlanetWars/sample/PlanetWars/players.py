import uuid
from entities import NEUTRAL_ID


class GameInfo(object):

    ''' This is the facade of game information given to each "bot" controller
        each `update` call. It contains the players unique view of the game
        (limited by fog-of-war).

        It also has bound to it player-specific `log`, `planet_order` and
        `fleet_order` functions which a bot can call to make notes and issue
        orders. It is up to the PlanetWars instance to "process" pending orders,
        and so enforce any required game limits or rules.
    '''
    NEUTRAL_ID = NEUTRAL_ID

    def __init__(self, fleet_order, planet_order, logger):
        # planets
        self.planets = {}
        self.neutral_planets = {}
        self.my_planets = {}
        self.enemy_planets = {}
        self.not_my_planets = {}  # == enemy + neutral
        # fleets
        self.fleets = {}
        self.my_fleets = {}
        self.enemy_fleets = {}
        # numbers
        self.num_ships = 0
        # store helper functions
        self.fleet_order = fleet_order
        self.planet_order = planet_order
        self.log = logger

    def clear(self):
        # planets
        self.planets.clear()
        self.neutral_planets.clear()
        self.my_planets.clear()
        self.enemy_planets.clear()
        self.not_my_planets.clear()
        # fleets
        self.fleets.clear()
        self.my_fleets.clear()
        self.enemy_fleets.clear()
        # numbers
        self.num_ships = 0


class Player(object):

    ''' This is used by the actual `PlanetWars` game instance to represent each
        player, and also finds, creates and contains the "bot" controller
        instance specified by `name`.

        Each game step `update` the Player instance refreshes the GameInfo
        instance and passes it to the bot controller, which then issues orders
        (via the facade). The orders may be ignored if they are invalid.

        The facade details represent a "fog-of-war" view of the true game
        environment. A player bot can only "see" what is in range of it's own
        occupied planets or fleets in transit across the map. This creates an
        incentive for bots to exploit scout details.
    '''

    def __init__(self, id, name, color, log, cfg):
        self.id = id  # as allocated by the game
        self.name = name.replace('.py', '')  # accept both "Dumbo" or "Dumbo.py"
        self.color = color  # if others want to know
        self.cfg = cfg  # nice to know details
        self.log = log or (lambda *p, **kw: None)
        self.gameinfo = GameInfo(self.fleet_order, self.planet_order, self.log)
        self.orders = []
        self.planets = {}  # our copy of all planets (known and unknown)
        self.fleets = {}  # our copy of all fleets we know about
        self.num_ships = 0
        self._alive = True

        # Create a controller object based on the name
        # - Look for a ./bots/BotName.py module (file) we need
        mod = __import__('bots.' + name)  # ... the top level bots mod (dir)
        mod = getattr(mod, name)       # ... then the bot mod (file)
        cls = getattr(mod, name)      # ... the class (eg DumBo.py contains DumBo class)
        self.controller = cls()

    def __str__(self):
        return "%s(id=%s)" % (self.name, str(self.id))

    def refresh_gameinfo(self):
        ''' Update the player's view (facade) of planets/fleets  '''
        # set handy lists of planets/fleet id's
        self.gameinfo.clear()
        # set planet details
        self.gameinfo.planets.update(self.planets)
        self.gameinfo.neutral_planets.update(self._neutral_planets())
        self.gameinfo.my_planets.update(self._my_planets())
        self.gameinfo.enemy_planets.update(self._enemy_planets())
        self.gameinfo.not_my_planets.update(self._not_my_planets())
        # set fleet details
        self.gameinfo.fleets.update(self.fleets)
        self.gameinfo.my_fleets.update(self._my_fleets())
        self.gameinfo.enemy_fleets.update(self._enemy_fleets())
        # update total number of ships we have
        total = sum([p.num_ships for p in self.gameinfo.my_planets.values()])
        total += sum([f.num_ships for f in self.gameinfo.my_fleets.values()])
        self.num_ships = self.gameinfo.num_ships = total

    def update(self):
        # Assumes gameinfo facade details are ready - let the bot issue orders!
        # Note: the bot controller has a reference to our *_order methods.
        self.controller.update(self.gameinfo)

    def is_alive(self):
        result = self.num_ships > 0
        # only do this log message once.
        if not result and self._alive:
            self._alive = False
            self.log(f"I'm dead. {self.name}, [{self.id}]")
        return result

    def fleet_order(self, src_fleet, dest, num_ships):
        ''' Order fleet to divert (some/all) fleet ships to a destination planet.
            Note: this is just a request for it to be done, and fleetid is our reference
            if it is done, but no guarantee - the game decides and enforces the rules.
        '''
        # If source fleet splitting we'll need a new fleet_id else keep old one
        fleetid = uuid.uuid4() if num_ships < src_fleet.num_ships else src_fleet.id
        self.orders.append(('fleet', src_fleet.id, fleetid, num_ships, dest.id))
        return fleetid

    def planet_order(self, src_planet, dest, num_ships):
        ''' Order planet to launch a new fleet to the destination planet.
            Note: this is just a request for it to be done, and fleetid is our reference
            if it is done, but no guarantee - the game decides and enforces the rules.
        '''
        fleetid = uuid.uuid4()
        self.orders.append(('planet', src_planet.id, fleetid, num_ships, dest.id))
        return fleetid

    def _my_planets(self):
        return [(k, p) for k, p in self.planets.items() if p.owner_id == self.id]

    def _enemy_planets(self):
        return [(k, p) for k, p in self.planets.items() if p.owner_id not in (NEUTRAL_ID, self.id)]

    def _not_my_planets(self):
        return [(k, p) for k, p in self.planets.items() if p.owner_id != self.id]

    def _neutral_planets(self):
        return [(k, p) for k, p in self.planets.items() if p.owner_id == NEUTRAL_ID]

    def _my_fleets(self):
        return [(k, f) for k, f in self.fleets.items() if f.owner_id == self.id]

    def _enemy_fleets(self):
        return [(k, f) for k, f in self.fleets.items() if f.owner_id != self.id]

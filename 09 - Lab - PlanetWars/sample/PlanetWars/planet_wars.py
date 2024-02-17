from entities import Fleet, Planet, NEUTRAL_ID
from players import Player
from collections import defaultdict
from logger import Logger


class PlanetWars(object):

    def __init__(self, gamestate=None, logger=None, gameid=0, cfg=None):
        # Note: using {} for planets, fleets to support quick "in" test based on id
        self.planets = {}
        self.fleets = {}
        self.extent = [0, 0, 0, 0]
        self.tick = 0
        self.players = {}
        self.alive_players = 0
        self.winner = None
        self.gameid = gameid
        self.orders = []
        self.cfg = cfg

        if gamestate:
            self._parse_gamestate_text(gamestate)
        self.logger = logger or Logger('./logs/%s.log')
        self.turn_log = self.logger.turn

    def add_player(self, name, color=None):
        ''' Add a player by name, which will be created and contain a
            controller "bot" loaded from the bot directory.
        '''
        # determine the player id, and get their unique logging function
        player_id = len(self.players) + 1
        log = self.logger.get_player_logger(player_id)
        # create a new player insance,
        self.players[player_id] = Player(player_id, name, color, log, self.cfg)
        # - tell them about all initial planet instances
        self.players[player_id].planets.update(
            (k, v.copy()) for k, v in self.planets.items())
        # check / warn missing home planet for player! (won't get any moves)
        planets = [p_id for p_id, p in self.planets.items() if p.owner_id == player_id]
        if not planets:
            print(f"WARNING! There is no home planet in map for player [{player_id}] '{name}'")
            for p_id, p, in self.planets.items():
                if p.owner_id == NEUTRAL_ID:
                    p.owner_id = player_id
                    print(f" - selected first available planet id={p_id}")
                    break
        # track how many are alive
        self.alive_players = player_id

    def _parse_gamestate_text(self, gamestate):
        # get the lines, remove comments
        lines = [v for v in gamestate.split("\n") if (v.strip() != '') and (v[0] != '#')]
        # todo: maps must indicate a place for each player - only two for current maps.
        for line in lines:
            bits = line.split(" ")
            if bits[0] == "P":
                assert len(bits) == 7, "Wrong number of details for Planet"
                # Planet(x, y, planet_id, owner_id, num_ships, growth_rate)
                # todo: use "unpack" format (struct?/pickle?)
                p = Planet(float(bits[1]), float(bits[2]), int(
                    bits[3]), int(bits[4]), int(bits[5]), int(bits[6]))
                self.planets[p.id] = p
                # update extent (area) of map as required
                if p.y + p.growth_rate > self.extent[0]:
                    self.extent[0] = p.y + p.growth_rate
                if p.x + p.growth_rate > self.extent[1]:
                    self.extent[1] = p.x + p.growth_rate
                if p.y - p.growth_rate < self.extent[2]:
                    self.extent[2] = p.y - p.growth_rate
                if p.x - p.growth_rate < self.extent[3]:
                    self.extent[3] = p.x - p.growth_rate
            elif bits[0] == "F":
                assert len(bits) == 8, "Wrong number of details for Fleet"
                bits = [int(b) for b in bits[1:]]  # all ints, pop the "F"
                # Fleet(fleet_id, owner_id, num_ships, src.x, src.y, dest_id, progress)
                f = Fleet(bits[0], bits[1], bits[2], bits[3], bits[4], bits[5], bits[6])
                self.fleets[f.id] = f
            elif bits[0] == "M":
                self.gameid = int(bits[1])
                self.player_id = int(bits[2])
                self.tick = int(bits[3])
                self.winner = int(bits[4])
            else:
                assert False, "Eh? Unknown line!"

    def __str__(self):
        # todo: this doesn't match the _parse_gamestate_text format anymore
        s = []
        s.append("M %d %d %d %d" %
                 (self.gameid, self.player_id, self.tick, self.winner.id))
        for p in self.planets:
            s.append("P %f %f %d %d %d" % (p.x, p.y, p.owner_id, p.num_ships, p.growth_rate))
        for f in self.fleets:
            s.append("F %d %d %d %d %d %d" % (f.owner_id, f.num_ships, f.src, f.dest,
                                              f.total_trip_length, f.turns_remaining))
        return "\n".join(s)

    def reset(self):
        # Get ready for first update call
        for player in self.players.values():
            self._sync_player_view(player)
            player.refresh_gameinfo()

    def update(self):
        if self.winner:
            return
        # phase 0, Give each player (controller) a chance to create new fleets
        for player in self.players.values():
            player.update()
        # phase 1, Retrieve and process all pending orders from each player
        for player in self.players.values():
            self._process_orders(player)
        # phase 2, Planet ship number growth (advancement)
        for planet in self.planets.values():
            planet.update()
        # phase 3, Update fleets, check for arrivals
        arrivals = defaultdict(list)
        for f in self.fleets.values():
            f.update()
            if f.turns_remaining <= 0:
                arrivals[f.dest].append(f)
        # phase 4, Collate fleet arrivals and planet forces by owner
        for p, fleets in arrivals.items():
            forces = defaultdict(int)
            # add the current occupier of the planet
            forces[p.owner_id] = p.num_ships
            # add arriving fleets
            for f in fleets:
                self.fleets.pop(f.id)
                forces[f.owner_id] += f.num_ships
            # Simple reinforcements?
            if len(forces) == 1:
                p.num_ships = forces[p.owner_id]
            # Battle!
            else:
                # There are at least 2 forces, maybe more. Biggest force is winner.
                # Gap between 1st and 2nd is the remaining force. (The rest cancel each out.)
                result = sorted([(v, k) for k, v in forces.items()], reverse=True)
                winner_id = result[0][1]
                gap_size = result[0][0] - result[1][0]
                # If meaningful outcome, log it
                if winner_id == 0:  # neutral defense - log nothing
                    pass
                elif winner_id == p.owner_id:
                    self.turn_log(
                        "{0:4d}: Player {1} defended planet {2}".format(self.tick, winner_id, p.id))
                else:
                    self.turn_log(
                        "{0:4d}: Player {1} now owns planet {2}".format(self.tick, winner_id, p.id))
                # Set the new winner
                p.owner_id = winner_id
                p.num_ships = gap_size
                p.was_battle = True
        # phase 5, Update the game tick count.
        self.tick += 1
        # phase 6, Resync current facade view of the map for each player
        for player in self.players.values():
            self._sync_player_view(player)

    def _sync_player_view(self, player):
        player.tick = self.tick
        # find out which planets / fleets are currently in view
        planetsinview = set()
        fleetsinview = set()
        for planet in self.planets.values():
            if planet.owner_id == player.id:
                # planet-to-planet in view?
                planetsinview.update(planet.in_range(self.planets.values()))
                # planet-to-flee in view?
                fleetsinview.update(planet.in_range(self.fleets.values()))
        for fleet in self.fleets.values():
            # ignore old fleets
            if (fleet.owner_id == player.id) and (fleet.id in self.fleets):
                # fleet-to-planet in view?
                planetsinview.update(fleet.in_range(self.planets.values()))
                # fleet-to-fleet in view?
                fleetsinview.update(fleet.in_range(self.fleets.values()))

        # Create and update the facade details! ("Age" planets if not in view)
        # - new planets? (rare event - requires dynamic map)
        new_planets = {p_id: p.copy() for p_id, p in self.planets.items() if p_id not in player.planets}
        if new_planets:
            player.planets.update(new_planets)
        # - update in-vision and age out-of-vision ...
        for p_id, planet in player.planets.items():
            # - update (recopy) accurate current details for all planets in view
            if p_id in planetsinview:
                player.planets[p_id] = self.planets[p_id].copy()
                player.planets[p_id].vision_age = 0
            # - Increase vision_age of planets that are no longer in view
            else:
                if planet.owner_id == player.id:  # lost planet?
                    # let player know winner
                    planet.owner_id = self.planets[p_id].owner_id
                planet.vision_age += 1
        # clear old fleet list, (if they aren't in view they disappear), copy in view
        player.fleets.clear()
        for f_id in fleetsinview:
            player.fleets[f_id] = self.fleets[f_id].copy()
        # get the player to update their gameinfo with new details
        player.refresh_gameinfo()

    def _process_orders(self, player):
        ''' Process all pending orders for the player, then clears the orders.
            An order sends ships from a player-owned fleet or planet to a planet.

            Checks for valid order conditions:
            - Valid source src (planet or fleet)
            - Valid destination dest (planet only)
            - Source is owned by player
            - Source has ships to launch (>0)
            - Limits number of ships to number available

            Invalid orders are modfied (ship number limit) or ignored.
        '''
        player_id = player.id
        for order in player.orders:
            o_type, src_id, new_id, num_ships, dest_id = order
            # Check for valid fleet or planet id?
            if src_id not in (self.planets.keys() | self.fleets.keys()):
                self.turn_log("Invalid order ignored - not a valid source.")
            # Check for valid planet destination?
            elif dest_id not in self.planets:
                self.turn_log("Invalid order ignored - not a valid destination.")
            else:
                # Extract and use the src and dest details
                src = self.fleets[src_id] if o_type == 'fleet' else self.planets[src_id]
                dest = self.planets[dest_id]
                # Check that player owns the source of ships!
                if src.owner_id is not player_id:
                    self.turn_log("Invalid order ignored - player does not own source!")
                # Is the number of ships requested valid?
                if num_ships > src.num_ships:
                    self.turn_log("Invalid order modified - not enough ships. Max used.")
                    num_ships = src.num_ships
                # Still ships to launch? Do it ...
                if num_ships > 0:
                    fleet = Fleet(new_id, player_id, num_ships, src, dest)
                    src.remove_ships(num_ships)
                    # old empty fleet removal
                    if o_type == 'fleet' and src.num_ships == 0:
                        del self.fleets[src.id]
                    # keep new fleet
                    self.fleets[new_id] = fleet
                    msg = "{0:4d}: Player {1} launched {2} (left {3}) ships from {4} {5} to planet {6}".format(
                        self.tick, player_id, num_ships, src.num_ships, o_type, src.id, dest.id)
                    self.turn_log(msg)
                    player.log(msg)
                else:
                    self.turn_log("Invalid order ignored - no ships to launch.")
        # Done - clear orders.
        player.orders[:] = []

    def is_alive(self):
        ''' Return True if two or more players are still alive. '''
        # already stopped?
        if self.winner:
            return False
        # check ...
        status = [p for p in self.players.values() if p.is_alive()]
        if len(status) == 1:
            self.winner = status[0]
            status[0].log(f"{self.tick:4d}: I won! {status[0].name} [{status[0].id}]")
            print(f"Game result: [{self.winner}] in {self.tick} steps.")
            return False
        else:
            return True

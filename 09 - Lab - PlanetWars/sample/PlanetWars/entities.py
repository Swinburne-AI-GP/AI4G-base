"""
Game Entities for the PlanetWars world

There are two game entity classes: `Planet` and `Fleet`. Both are derived from
an `Entity` base class. Conceptually both planets and fleets contain "ships",
and have a unique game id given to them.

Planets are either "owned" by a player or neutral. When occupied by a player,
planets create new ships (based on their `growth_rate`).

Fleets are launched from a planet (or fleet) and sent to a target planet.
Fleets are always owned by one of the players.

"""
from math import sqrt

NEUTRAL_ID = 0


class Entity(object):

    ''' Abstract class representing entities in the 2d game world.
        See Fleet and Planet classes.
    '''

    def __init__(self, x, y, id, owner_id, num_ships):
        self.x = x
        self.y = y
        self.num_ships = num_ships
        self.id = id  # type int or uuid
        self.owner_id = owner_id
        self.vision_age = 0
        self.vision_range = 0
        self.was_battle = False
        self._name = "%s:%s" % (type(self).__name__, str(id))

    def distance_to(self, other):
        if self.id == other.id:
            return 0.0
        dx = self.x - other.x
        dy = self.y - other.y
        return sqrt(dx * dx + dy * dy)

    def remove_ships(self, num_ships):
        if num_ships <= 0:
            raise ValueError(
                "Eh! %s (owner %s) tried to send %d ships (of %d)." %
                (self._name, self.owner_id, num_ships, self.num_ships))
        if self.num_ships < num_ships:
            raise ValueError(
                "Eh! %s (owner %s) can't remove more ships (%d) then it has (%d)!" %
                (self._name, self.owner_id, num_ships, self.num_ships))
        self.num_ships -= num_ships

    def add_ships(self, num_ships):
        if num_ships < 0:
            raise ValueError("Cannot add a negative number of ships...")
        self.num_ships += num_ships

    def update(self):
        raise NotImplementedError("This method cannot be called on this 'abstract' class")

    def is_in_vision(self):
        return self.vision_age == 0

    def in_range(self, entities):
        ''' Returns a list of entity id's that are within vision range of this entity.'''
        limit = self.vision_range
        return [p.id for p in entities if self.distance_to(p) <= limit]

    def __str__(self):
        return "%s, owner: %s, ships: %d" % (self._name, self.owner_id, self.num_ships)


class Planet(Entity):

    ''' A planet in the game world. When occupied by a player, the planet
        creates new ships each time step (when `update` is called). Each
        planet also has a `vision_range` which is partially proportional
        to the growth rate (size).
    '''
    PLANET_RANGE = 3
    PLANET_FACTOR = 0.5

    def __init__(self, x, y, id, owner_id, num_ships, growth_rate):
        super(Planet, self).__init__(x, y, id, owner_id, num_ships)
        self.growth_rate = growth_rate
        self.update_vision_range()

    def update(self):
        ''' If the planet is owned, grow the number of ships (advancement). '''
        if self.owner_id != NEUTRAL_ID:
            self.add_ships(self.growth_rate)
        self.was_battle = False

    def update_vision_range(self):
        ''' The size of the planet will add some vision range with the formula:
            totalrange = PLANET_RANGE + (planet.growth_rate * PLANET_FACTOR)
        '''
        self.vision_range = self.PLANET_RANGE + (self.growth_rate * self.PLANET_FACTOR)

    def copy(self):
        ''' Provides a copy of the Planet instance. '''
        p = Planet(self.x, self.y, self.id, self.owner_id, self.num_ships, self.growth_rate)
        p.was_battle = self.was_battle
        return p


class Fleet(Entity):

    ''' A fleet in the game world. Each fleet is owned by a player and launched
        from either a planet or a fleet (mid-flight). All fleets move at the
        same speed each game step.

        Fleet id values are deliberately obscure (using UUID) to remove any
        possible value an enemy players might gather from it.
    '''
    FLEET_RANGE = 2
    # the size of the fleet will add some vision range
    # with the formula: totalrange = FLEET_RANGE + (fleet.num_ships * FLEET_FACTOR)
    # todo remove FLEET_FACTOR?
    FLEET_FACTOR = 0

    def __init__(self, id, owner_id, num_ships, src, dest, progress=0):
        super(Fleet, self).__init__(src.x, src.y, id, owner_id, num_ships)
        self.src = src
        self.dest = dest
        self.total_trip_length = self.src.distance_to(dest)
        if self.total_trip_length == 0:
            raise ValueError("Distance from source to dest is 0?")
        self.turns_remaining = self.total_trip_length - progress
        self.progress = 0
        self.update_vision_range()

        self.growth_rate = 0

    def in_range(self, entities, ignoredest=True):
        result = super(Fleet, self).in_range(entities)
        if (not ignoredest) and (self.turns_remaining == 1) and (self.dest not in result):
            result.append(self.dest)
        return result

    def update_vision_range(self):
        self.vision_range = self.FLEET_RANGE + (self.num_ships * self.FLEET_FACTOR)

    def update(self):
        ''' Move the fleet (progress) by one game time step.'''
        self.turns_remaining -= 1
        # update position and progress
        src = self.src
        dest = self.dest
        scale = 1 - (float(self.turns_remaining) / float(self.total_trip_length))
        self.x = src.x + (dest.x - src.x) * scale
        self.y = src.y + (dest.y - src.y) * scale
        self.progress = self.total_trip_length - self.turns_remaining

    def copy(self):
        ''' Provides a copy of the Fleet instance, with copies of the src and dest. '''
        f = Fleet(self.id, self.owner_id, self.num_ships, self.src.copy(), self.dest.copy(), self.progress)
        f.x, f.y, f.turns_remaining = self.x, self.y, self.turns_remaining
        return f

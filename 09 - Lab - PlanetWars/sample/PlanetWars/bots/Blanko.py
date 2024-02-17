''' Simple "Blank" PlanetWars controller bot.

The Bot does nothing, but shows the minimum a bot needs to have.

See the `update` method which is where your code goes.

The `PlanetWars` `Player` object (see players.py), will contain your bot
controller instance. The Player will provide a current `GameInfo` instance
to your bot `update` method each time it is called.

The `gameinfo` instance is a facade of the state of the game for the `Player`,
and includes all planets and fleets that currently exist. Note that the
details are limited by "fog of war" vision and only match what you can see. If
you want to know more you'll need to scout!

A gameinfo instance has various (possibly useful) dict's for you to use:

    # all planet and fleets (that you own or can see)
    planets
    fleets

    # dict's of just your planets/fleets
    my_planets
    my_fleets

    # dict's of both neutral and enemy planets/fleets
    not_my_planets
    not_my_fleets

    # dict's of just the enemy planet/fleets (fog limited)
    enemy_planets
    enemy_fleets

You issue orders from your bot using the methods of the gameinfo instance.

    gameinfo.planet_order(src, dest, ships)
    gameinfo.fleet_order(src, dest, ships)

For example, to send 10 ships from planet src to planet dest, you would
say `gameinfo.planet_order(src, dest, 10)`.

There is also a player specific log if you want to leave a message

    gameinfo.log("Here's a message from the bot")

'''


class Blanko:

    def update(self, gameinfo):
        pass

class OneMove:

    def update(self, gameinfo):

        if gameinfo.my_planets and gameinfo.not_my_planets:
            # print(gameinfo.my_planets)
            src = list(gameinfo.my_planets.values())[0]
            dest = list(gameinfo.not_my_planets.values())[0]
            gameinfo.planet_order(src, dest, src.num_ships)
            gameinfo.log("I'll send %d ships from planet %s to planet %s" % (src.num_ships, src, dest))

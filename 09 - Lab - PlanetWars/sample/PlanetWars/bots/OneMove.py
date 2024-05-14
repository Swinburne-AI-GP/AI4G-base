class OneMove(object):

	def update(self, gameinfo):

		if gameinfo._my_planets() and gameinfo._not_my_planets():
			src = list(gameinfo._my_planets().values())[0]
			dest = list(gameinfo._not_my_planets().values())[0]
			gameinfo.planet_order(src, dest, src.ships)
			#gameinfo.log("I'll send %d ships from planet %s to planet %s" % (src.ships, src, dest))


""" Deceptive PlanetWars Simulation

Created by 
Michale Jensen (2011)
Clinton Woodward (2012)
James Bonner (2023)
contact: cwoodward@swin.edu.au

Updated 2023
- Added pyglet 2.x graphics support
- Made data interfaces JSON
Updated 2024
- Refactor
- Discord bot support
"""

from planet_wars import PlanetWarsGame

import argparse
import json
import pathlib
import uuid
import collections

if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		prog="PlanetWars",
		description=""" 
					Deceptive PlanetWars Simulation

						Created by 
						Michale Jensen (2011)
						Clinton Woodward (2012)
						James Bonner (2023/4)
						contact: jbonner@swin.edu.au""",
		formatter_class=argparse.RawDescriptionHelpFormatter,
	)
	parser.add_argument(
		"-p",
		"--players",
		nargs="*",
		help="Players in this run. Should be the name (no extension) of file found in /bots. Ignored if the map or replay has players hardcoded.",
	)
	parser.add_argument(
		"-m",
		"--map",
		help="Filename (no extension) of map to play on. If not supplied, a random map is generated for play.",
	)
	# parser.add_argument(
	# 	"-g",
	# 	"--generate",
	# 	help="Generate a new random map. Outputs the json for the map to the filename provided.",
	# )
	parser.add_argument(
		"-r",
		"--replay",
		help="Filename (no extension) of replay to run. Does nothing without either --gui or --logscript being provided",
	)
	parser.add_argument(
		"--gui", help="Runs with the graphical output", action="store_true"
	)
	parser.add_argument(
		"--logscript",
		help="Adds a log output script. Could be used to make game ticks/actions human readable or to print statistics about the game states.",
	)
	parser.add_argument(
		"--save-replay",
		nargs="?",
		default=argparse.SUPPRESS,
		help="Saves a replay. Optional: filename (no extension) to save the replay to. If not provided, the replay is saved to the replays directory with a UUID filename.",
	)
	parser.add_argument(
		"--max-ticks",
		type=int,
		default=10000,
		help="Saves a replay. Optional: filename (no extension) to save the replay to. If not provided, the replay is saved to the replays directory with a UUID filename.",
	)
	args = parser.parse_args()

	if args.map and args.replay:
		print("Cannot use both --maps and --replay")
		exit()

	if args.map or args.replay:
		filename = args.map or args.replay
		if args.map:
			filename = pathlib.PurePath(".\\maps").joinpath(filename + ".json")
		if args.replay:
			filename = pathlib.PurePath(".\\replays").joinpath(filename + ".json")
		f = open(filename, "r+")
		gamestate = json.loads(f.read())
	else:
		#TODO: generate random map
		pass

	if not "players" in gamestate:
		if not args.players:
			print(
				"Players not specified in the map/replay, or on the command line. To run with this map/replay, specify the players using -p."
			)
			exit()
		gamestate["players"] = []
		for player in args.players:
			gamestate["players"].append({"ID": str(uuid.uuid1()), "name": player})

	if(args.max_ticks):
		gamestate["max_ticks"] = args.max_ticks

	replay_object = None
	if not args.replay and hasattr(args, "save_replay"):
		replay_object = collections.defaultdict(list)
		

	game = PlanetWarsGame(gamestate, args.logscript, replay_object)

	def write_replay():
		if replay_object:
			try:
				#args.save_replay will either be
				# a) undefined - there is no replay, we error out and move on
				# b) a string - we save the replay to that filename
				# c) None - we save the replay to a UUID filename
				if args.save_replay:
					replay_file = open(f".\\replays\\{args.save_replay}.json", "w")
				else:
					replay_file = open(f".\\replays\\{uuid.uuid1()}.json", "w")
				replay_file.write(json.dumps(replay_object))
			except:
				pass


	if args.gui:
		from planet_wars_draw import PlanetWarsWindow
		window = PlanetWarsWindow(game)
	else:
		game.paused = False
		while game.is_alive() and game.tick < game.max_ticks:
			game.update()
	write_replay()

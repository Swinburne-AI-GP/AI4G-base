game = None

from enum import Enum
import pyglet
from box_world import BoxWorld, search_modes
from graphics import window

# Mouse mode indicates what the mouse "click" should do...
class MouseModes(Enum):
		CLEAR = 	pyglet.window.key._1
		MUD = 		pyglet.window.key._2
		WATER = 	pyglet.window.key._3
		WALL = 		pyglet.window.key._4
		START = 	pyglet.window.key._5
		TARGET = 	pyglet.window.key._6

class SearchModes(Enum):
		DFS = 		1
		BFS = 		2
		Dijkstra = 	3
		AStar = 	4

class Game():
	def __init__(self, map):
		self.world = BoxWorld.FromFile(map)
		# Mouse mode indicates what the mouse "click" should do...
		self.mouse_mode = MouseModes.MUD
		window._update_label('mouse', 'Click to place: '+self.mouse_mode.name)

		# search mode cycles through the search algorithm used by box_world
		self.search_mode = 1
		window._update_label('search', 'Search Type: '+SearchModes(self.search_mode).name)
		# search limit
		self.search_limit = 0 # unlimited.
		window._update_label('status', 'Status: Loaded')

	
	def plan_path(self):
		self.world.plan_path(self.search_mode, self.search_limit)
		window._update_label('status', 'Status: Path Planned')

	def input_mouse(self, x, y, button, modifiers):
		box = self.world.get_box_by_pos(x,y)
		if box:
			if self.mouse_mode == MouseModes.START:
				self.world.set_start(box.node.idx)
			elif self.mouse_mode == MouseModes.TARGET:
				self.world.set_target(box.node.idx)
			else:
				box.set_type(self.mouse_mode.name)
			self.world.reset_navgraph()
			self.plan_path()
			window._update_label('status','Status: Graph Changed')

	def input_keyboard(self, symbol, modifiers):
		# mode change?
		if symbol in MouseModes:
			self.mouse_mode = MouseModes(symbol)
			window._update_label('mouse', 'Click to place: '+self.mouse_mode.name)

		# Change search mode? (Algorithm)
		elif symbol == pyglet.window.key.M:
			self.search_mode += 1
			if self.search_mode > len(search_modes):
				self.search_mode = 1
			self.world.plan_path(self.search_mode, self.search_limit)
			window._update_label('search', 'Search Type: '+SearchModes(self.search_mode).name)
		elif symbol == pyglet.window.key.N:
			self.search_mode -= 1
			if self.search_mode <= 0:
				self.search_mode = len(search_modes)
			self.world.plan_path(self.search_mode, self.search_limit)
			window._update_label('search', 'Search Type: '+SearchModes(self.search_mode).name)
		# Plan a path using the current search mode?
		elif symbol == pyglet.window.key.SPACE:
			self.world.plan_path(self.search_mode, self.search_limit)
		elif symbol == pyglet.window.key.UP:
			self.search_limit += 1
			window._update_label('status', 'Status: limit=%d' % self.search_limit)
			self.world.plan_path(self.search_mode, self.search_limit)
		elif symbol == pyglet.window.key.DOWN:
			if self.search_limit-1 > 0:
				self.search_limit -= 1
				window._update_label('status', 'Status: limit=%d' % self.search_limit)
				self.world.plan_path(self.search_mode, self.search_limit)
		elif symbol == pyglet.window.key._0:
			self.search_limit = 0
			window._update_label('status', 'Status: limit=%d' % self.search_limit)
			self.world.plan_path(self.search_mode, self.search_limit)
''' Basic square grid based world (BoxWorld) to test/demo path planning.

Created for COS30002 AI for Games, Lab,
by Clinton Woodward <cwoodward@swin.edu.au>

For class use only. Do not publically share or post this code without
permission.

See readme.txt for details. Look for ### comment lines.

Note that the box world "boxes" (tiles) are created and assigned an index (idx)
value, starting from the origin in the bottom left corder. This matches the
convention of coordinates used by pyglet which uses OpenGL, rather than a
traditional 2D graphics with the origin in the top left corner.

   +   ...
   ^   5 6 7 8 9
   |   0 1 2 3 4
 (0,0) ---> +

A BoxWorld can be loaded from a text file. The file uses the following format.

* Values are separated by spaces or tabs (not commas)
* Blank lines or lines starting with # (comments) are ignored
* The first data line is two integer values to specify width and height
* The second row specifies the Start and the Target boxes as index values.
	S 10 T 15
* Each BowWorld row is the specified per line of the text file.
	- Each type is specified by a single character ".", "~", "m" or "#".
	- Number of tile values must match the number of columns
* The number of rows must match the number of specified rows.

Example BoxWorld map file.

# This is a comment and is ignored
# First specify the width x height values
6 5
# Second specify the start and target box indexes
0 17
# Now specify each row of column values
. . . . . .
~ ~ X . . .
. ~ X ~ . .
. . X . . .
. m m m . .
# Note the number of rows and column values match

'''
from math import hypot
from enum import Enum
from graphics import COLOUR_NAMES, window
import pyglet
from point2d import Point2D
from graph import SparseGraph, Node, Edge
from searches import SEARCHES

box_types = {
	"CLEAR":{"symbol":'.', "cost":{"CLEAR":1, "MUD":2,"WATER":5}, "colour":"WHITE"},
	"MUD":{"symbol":'m', "cost":{"CLEAR":2, "MUD":4,"WATER":9}, "colour":"BROWN"},
	"WATER":{"symbol":'~', "cost":{"CLEAR":5, "MUD":9,"WATER":10}, "colour":"AQUA"},
	"WALL":{"symbol":'X', "colour":"GREY"},
}

min_edge_cost = 10.0 # must be min value for heuristic cost to work

# def edge_cost(k1, k2):
# 	k1 = box_type.index(k1)
# 	k2 = box_type.index(k2)
# 	return edge_cost_matrix[k1][k2]

search_modes = list(SEARCHES.keys())

class Box(object):
	'''A single box for boxworld. '''

	def __init__(self,index, x, y, width, height, type='.'):
		self.x = x
		self.y = y
		self.index = index
		self.width = width
		self.height = height
		for key, value in box_types.items():
			if value['symbol'] == type:
				self.type = key
		#a box must be able to draw:
		# - a box with a grey outline and an (optional) filled colour
		self.box = pyglet.shapes.BorderedRectangle(
			x, y, width, height, border=1,
			color=COLOUR_NAMES[box_types[self.type]["colour"]], 
			border_color=COLOUR_NAMES["LIGHT_GREY"],
			batch=window.get_batch()
		)
		# - a label showing the box index
		self.label = pyglet.text.Label(
			str(index),
			font_name='Times New Roman',
			font_size=12,
			x=x+width//2, y=y+height//2,
			anchor_x='center', anchor_y='center',
			color=COLOUR_NAMES["BLACK"],
			batch=window.get_batch("numbers")
		)
		
		# nav graph node
		self.node = None

	def set_type(self, type):
		#this code gets repeated in a couple of places in theis func, so I made it a function-within-a-function
		#it's usually good practice to make sure things are only ever done in a single location, but sometimes that can make things harder to read
		def update_box(type):
			self.type = type
			self.box.color = COLOUR_NAMES[box_types[self.type]["colour"]]
		if type in box_types:
			update_box(type)
			return
		else:
			for key, value in box_types.items():
				if value['symbol'] == type:
					update_box(key)
					return
		print('not a known tile type "%s"' % type)
	
	def center(self):
		return Point2D(self.x+self.width//2, self.y+self.height//2)

class BoxWorld(object):
	'''A world made up of boxes. '''

	def __init__(self, x_boxes, y_boxes, window_width, window_height):
		self.boxes = [None]*x_boxes*y_boxes
		self.x_boxes= x_boxes 
		self.y_boxes= y_boxes 
		box_width = window_width // x_boxes
		box_height = window_height // y_boxes
		self.wx = (window_width-1) // self.x_boxes
		self.wy = (window_height-1) // self.y_boxes 
		for i in range(len(self.boxes)):
			self.boxes[i] = Box(
				i,
				i%x_boxes*box_width,
				i//x_boxes%y_boxes*box_height,
				box_width,box_height
			)
		# create nav_graph
		self.path = None
		self.graph = None
		
		self.start = self.boxes[1]
		self.start_marker = pyglet.shapes.Arc( #in pyglet a circle is filled, an arc is unfilled
			self.boxes[1].center().x,
			self.boxes[1].center().y,
			15, segments=30,
			color=COLOUR_NAMES["RED"],
			batch=window.get_batch("path"),
			thickness=4
		)
		self.target = self.boxes[2]
		self.target_marker = pyglet.shapes.Arc(
			self.boxes[2].center().x,
			self.boxes[2].center().y,
			15, segments=30,
			color=COLOUR_NAMES["GREEN"],
			batch=window.get_batch("path"),
			thickness=4
		)

		#lists used to store the primitives that render out our various pathfinding data
		self.render_path = []
		self.render_tree = []
		self.render_open_nodes = []
		self.render_graph = []

		self.reset_navgraph()

	def get_box_by_xy(self, ix, iy):
		idx = (self.x_boxes * iy) + ix
		return self.boxes[idx] if idx < len(self.boxes) else None

	def get_box_by_pos(self, x, y):
		idx = (self.x_boxes * (y // self.wy)) + (x // self.wx)
		return self.boxes[idx] if idx < len(self.boxes) else None

	def _add_edge(self, from_idx, to_idx, distance=1.0):
		b = self.boxes
		if "cost" in box_types[b[from_idx].type] and b[to_idx].type in box_types[b[from_idx].type]["cost"]:
			cost = box_types[b[from_idx].type]["cost"][b[to_idx].type]
			self.graph.add_edge(Edge(from_idx, to_idx, cost*distance))

	def _manhattan(self, idx1, idx2):
		''' Manhattan distance between two nodes in boxworld, assuming the
		minimal edge cost so that we don't overestimate the cost). '''
		x1, y1 = self.boxes[idx1].pos
		x2, y2 = self.boxes[idx2].pos
		return (abs(x1-x2) + abs(y1-y2)) * min_edge_cost

	def _hypot(self, idx1, idx2):
		'''Return the straight line distance between two points on a 2-D
		Cartesian plane. Argh, Pythagoras... trouble maker. '''
		x1, y1 = self.boxes[idx1].pos
		x2, y2 = self.boxes[idx2].pos
		return hypot(x1-x2, y1-y2) * min_edge_cost

	def _max(self, idx1, idx2):
		'''Return the straight line distance between two points on a 2-D
		Cartesian plane. Argh, Pythagoras... trouble maker. '''
		x1, y1 = self.boxes[idx1].pos
		x2, y2 = self.boxes[idx2].pos
		return max(abs(x1-x2),abs(y1-y2)) * min_edge_cost


	def reset_navgraph(self):
		''' Create and store a new nav graph for this box world configuration.
		The graph is build by adding NavNode to the graph for each of the
		boxes in box world. Then edges are created (4-sided).
		'''
		self.path = None # invalid so remove if present
		self.graph = SparseGraph()
		# Set a heuristic cost function for the search to use
		self.graph.cost_h = self._manhattan
		#self.graph.cost_h = self._hypot
		#self.graph.cost_h = self._max

		nx, ny = self.x_boxes, self.y_boxes
		# add all the nodes required
		for i, box in enumerate(self.boxes):
			box.pos = (i % nx, i // nx) #tuple position
			box.node = self.graph.add_node(Node(idx=i))
		# build all the edges required for this world
		for i, box in enumerate(self.boxes):
			# four sided N-S-E-W connections
			if "cost" not in box_types[box.type]:
				continue
			# UP (i + nx)
			if (i+nx) < len(self.boxes):
				self._add_edge(i, i+nx)
			# DOWN (i - nx)
			if (i-nx) >= 0:
				self._add_edge(i, i-nx)
			# RIGHT (i + 1)
			if (i%nx + 1) < nx:
				self._add_edge(i, i+1)
			# LEFT (i - 1)
			if (i%nx - 1) >= 0:
				self._add_edge(i, i-1)
			# # Diagonal connections
			# # UP LEFT(i + nx - 1)
			# j = i + nx
			# if (j-1) < len(self.boxes) and (j%nx - 1) >= 0:
			# 	self._add_edge(i, j-1, 1.4142) # sqrt(1+1)
			# # UP RIGHT (i + nx + 1)
			# j = i + nx
			# if (j+1) < len(self.boxes) and (j%nx + 1) < nx:
			# 	self._add_edge(i, j+1, 1.4142)
			# # DOWN LEFT(i - nx - 1)
			# j = i - nx
			# if (j-1) >= 0 and (j%nx - 1) >= 0:
			# 	print(i, j, j%nx)
			# 	self._add_edge(i, j-1, 1.4142)
			# # DOWN RIGHT (i - nx + 1)
			# j = i - nx
			# if (j+1) >= 0 and (j%nx +1) < nx:
			# 	self._add_edge(i, j+1, 1.4142)
		
		# add the graph to the render_graph
		for line in self.render_graph:
			try:
				line.delete() #pyglets Line.delete method is slightly broken
			except:
				pass
		for start, edge in self.graph.edgelist.items():
			for target in edge.keys():
				self.render_graph.append(
					pyglet.shapes.Line(
						self.boxes[start].center().x, 
						self.boxes[start].center().y,
						self.boxes[target].center().x,
						self.boxes[target].center().y,
						width=0.5, 
						color=COLOUR_NAMES['PURPLE'],
						batch=window.get_batch("edges")
					)
				)

	def set_start(self, idx):
		'''Set the start box based on its index idx value. '''
		# remove any existing start node, set new start node
		if self.target == self.boxes[idx]:
			print("Can't have the same start and end boxes!")
			return
		self.start = self.boxes[idx]
		self.start_marker.x = self.start.center().x
		self.start_marker.y = self.start.center().y

	def set_target(self, idx):
		'''Set the target box based on its index idx value. '''
		# remove any existing target node, set new target node
		if self.start == self.boxes[idx]:
			print("Can't have the same start and end boxes!")
			return
		self.target = self.boxes[idx]
		self.target_marker.x = self.target.center().x
		self.target_marker.y = self.target.center().y

	def plan_path(self, search, limit):
		'''Conduct a nav-graph search from the current world start node to the
		current target node, using a search method that matches the string
		specified in `search`.
		'''
		cls = SEARCHES[search]
		self.path = cls(self.graph, self.start.index, self.target.index, limit)
		# print the path details
		print(self.path.report())
		#then add them to the renderer
		#render the final path
		for line in self.render_path:
			try:
				line.delete() #pyglets Line.delete method is slightly broken
			except:
				pass
		p = self.path.path # alias to save us some typing
		if(len(p) > 1):
			for idx in range(len(p)-1):
				self.render_path.append(
					pyglet.shapes.Line(
						self.boxes[p[idx]].center().x, 
						self.boxes[p[idx]].center().y,
						self.boxes[p[idx+1]].center().x,
						self.boxes[p[idx+1]].center().y,
						width=3, 
						color=COLOUR_NAMES['BLUE'],
						batch=window.get_batch("path")
					)
				)
		for line in self.render_tree:
			try:
				line.delete() #pyglets Line.delete method is slightly broken
			except:
				pass
		#render the search tree
		t = self.path.route # alias to save us some typing
		if(len(t) > 1):
			for start, end in t.items():
				self.render_tree.append(
					pyglet.shapes.Line(
						self.boxes[start].center().x, 
						self.boxes[start].center().y,
						self.boxes[end].center().x,
						self.boxes[end].center().y,
						width=2, 
						color=COLOUR_NAMES['PINK'],
						batch=window.get_batch("tree")
					)
				)
		for circle in self.render_open_nodes:
			try:
				circle.delete() #pyglets Line.delete method is slightly broken
			except:
				pass
		#render the nodes that were still on the search stack when the search ended
		o = self.path.open # alias to save us some typing
		if(len(o) > 0):
			for idx in o:
				self.render_open_nodes.append(
					pyglet.shapes.Circle(
						self.boxes[idx].center().x, 
						self.boxes[idx].center().y,
						5, 
						color=COLOUR_NAMES['ORANGE'],
						batch=window.get_batch("tree")
					)
				)


	@classmethod
	def FromFile(cls, filename ):
		'''Support a the construction of a BoxWorld map from a simple text file.
		See the module doc details at the top of this file for format details.
		'''
		# open and read the file
		f = open(filename)
		lines = []
		for line in f.readlines():
			line = line.strip()
			if line and not line.startswith('#'):
				lines.append(line)
		f.close()
		# first line is the number of boxes width, height
		nx, ny = [int(bit) for bit in lines.pop(0).split()]
		# Create a new BoxWorld to store all the new boxes in...
		world = BoxWorld(nx, ny, window.width, window.height)
		# Get and set the Start and Target tiles
		s_idx, t_idx = [int(bit) for bit in lines.pop(0).split()]
		world.set_start(s_idx)
		world.set_target(t_idx)
		# Ready to process each line
		assert len(lines) == ny, "Number of rows doesn't match data."
		# read each line
		idx = 0
		for line in reversed(lines): # in reverse order
			bits = line.split()
			assert len(bits) == nx, "Number of columns doesn't match data."
			for bit in bits:
				bit = bit.strip()
				world.boxes[idx].set_type(bit)
				idx += 1
		world.reset_navgraph()
		return world
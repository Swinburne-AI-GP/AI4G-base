import pyglet, math

COLOUR_NAMES = {
	'BLACK':  (000, 000, 000, 255),
	'WHITE':  (255, 255, 255, 255),
	'RED':    (255, 000, 000, 255),
	'GREEN':  (000, 255, 000, 255),
	'BLUE':   (000, 000 ,255, 255),
	'GREY':   (100, 100, 100, 255),
	'PINK':   (255, 175, 175, 255),
	'YELLOW': (255, 255, 000, 255),
	'ORANGE': (255, 175, 000, 255),
	'PURPLE': (200, 000, 175, 200),
	'BROWN':  (125, 125, 100, 255),
	'AQUA':   (100, 230, 255, 255),
	'DARK_GREEN': (000, 100, 000, 255),
	'LIGHT_GREEN':(150, 255, 150, 255),
	'LIGHT_BLUE': (150, 150, 255, 255),
	'LIGHT_GREY': (200, 200, 200, 255),
	'LIGHT_PINK': (255, 230, 230, 255)
}

class ShapeGroup:
	def __init__(self, anchor, batch):
		self._x = anchor.x
		self._y = anchor.y
		self._anchor_x = self._x
		self._anchor_y = self._y
		self._rgba = (255, 255, 255, 255)
		self._visible = True
		self._batch = batch
		self.shapes = []

	def draw(self):
		for shape in self.shapes:
			shape.draw()

	def translate(self, v):
		for shape in self.shapes:
			shape.x += v.x
			shape.y += v.y
		self._anchor_x += v.x
		self._anchor_y += v.y

	@property
	def x(self):
		"""X coordinate of the shape.
		:type: int or float
		"""
		return self._x

	@x.setter
	def x(self, value):
		self.position = pyglet.math.Vec2(value, self._y)

	@property
	def y(self):
		"""Y coordinate of the shape.
		:type: int or float
		"""
		return self._y

	@y.setter
	def y(self, value):
		self.position = pyglet.math.Vec2(self._x, value)

	@property
	def position(self):
		"""The (x, y) coordinates of the shape, as a tuple.
		:Parameters:
			`x` : int or float
				X coordinate of the sprite.
			`y` : int or float
				Y coordinate of the sprite.
		"""
		return pyglet.math.Vec2(self._x, self._y)

	@position.setter
	def position(self, values):
		if type(values) is tuple:
			values = pyglet.math.Vec2(values[0], values[1])
		pos = pyglet.math.Vec2(self.position[0], self.position[1])
		v = values - pos
		self.translate(v)
		self._x = values.x
		self._y = values.y

	@property
	def anchor_x(self):
		"""The X coordinate of the anchor point
		:type: int or float
		"""
		return self._anchor_x

	@anchor_x.setter
	def anchor_x(self, value):
		self._anchor_x = value

	@property
	def anchor_y(self):
		"""The Y coordinate of the anchor point
		:type: int or float
		"""
		return self._anchor_y

	@anchor_y.setter
	def anchor_y(self, value):
		self._anchor_y = value

	@property
	def anchor_position(self):
		"""The (x, y) coordinates of the anchor point, as a tuple.
		:Parameters:
			`x` : int or float
				X coordinate of the anchor point.
			`y` : int or float
				Y coordinate of the anchor point.
		"""
		return self._anchor_x, self._anchor_y

	@anchor_position.setter
	def anchor_position(self, values):
		if type(values) is tuple:
			values = pyglet.math.Vec2(values[0], values[1])
		self._anchor_x = values.x
		self._anchor_y = values.y

	@property
	def color(self):
		"""The shape color.
		This property sets the color of the shape.
		The color is specified as an RGB tuple of integers '(red, green, blue)'.
		Each color component must be in the range 0 (dark) to 255 (saturated).
		:type: (int, int, int)
		"""
		return self._rgba

	@property
	def colour(self):
		"""The shape colour.
		This property sets the colour of the shape.
		The colour is specified as an RGB tuple of integers '(red, green, blue)'.
		Each colour component must be in the range 0 (dark) to 255 (saturated).
		:type: (int, int, int)
		"""
		return self._rgba

	@colour.setter
	def colour(self, values):
		r, g, b, *a = values

		if a:
			self._rgba = r, g, b, a[0]
		else:
			self._rgba = r, g, b, self._rgba[3]

		for line in self.shapes:
			line.color = self._rgba

	@color.setter
	def color(self, values):
		self.colour = values

	@property
	def opacity(self):
		"""Blend opacity.
		This property sets the alpha component of the color of the shape.
		With the default blend mode (see the constructor), this allows the
		shape to be drawn with fractional opacity, blending with the
		background.
		An opacity of 255 (the default) has no effect.  An opacity of 128
		will make the shape appear translucent.
		:type: int
		"""
		return self._rgba[3]

	@opacity.setter
	def opacity(self, value):
		self._rgba = (*self._rgba[:3], value)
		for shape in self.shapes:
			shape.color = self._rgba

	@property
	def visible(self):
		"""True if the shape will be drawn.
		:type: bool
		"""
		return self._visible

	@visible.setter
	def visible(self, value):
		self._visible = value
		for shape in self.shapes:
			shape.visible = value

	@property
	def group(self):
		raise NotImplementedError

	@group.setter
	def group(self, group):
		raise NotImplementedError

	@property
	def batch(self):
		"""User assigned :class:`Batch` object."""
		return self._batch

	@batch.setter
	def batch(self, batch):
		if self._batch == batch:
			return

		for line in self.shapes:
			line.batch = batch 

		self._batch = batch
		
class LineGroup(ShapeGroup):
	def __init__(self,
		position,
		rotation = 0,
		batch = None
	) -> None:
		
		super(LineGroup, self).__init__(
			position,
			batch = batch
		)
		self._rotation = rotation

	@property
	def rotation(self):
		return self._rotation

	@rotation.setter
	def rotation(self, value):
		a_v = pyglet.math.Vec2(self._anchor_x, self.anchor_y)
		rel_r = value-self._rotation
		for line in self.shapes:
			#move into line space
			v1 = pyglet.math.Vec2(line.x, line.y) - a_v
			v2 = pyglet.math.Vec2(line.x2, line.y2) - a_v
			#rotate
			v1 = v1.rotate(rel_r)
			v2 = v2.rotate(rel_r)
			#back into world space
			v1 = v1+a_v
			v2 = v2+a_v
			#update line
			line.x = v1.x
			line.y = v1.y
			line.x2 = v2.x
			line.y2 = v2.y
		self._rotation = value

class PolyLine(LineGroup):
	def __init__(self,
		vertices,
		width=1,
		colour=COLOUR_NAMES['AQUA'], 
		batch=None,
		closed=False
	) -> None:
		
		super(PolyLine, self).__init__(
			vertices[0],
			batch = batch
		)

		line = []
		for v in vertices:
			line.append(v)
			if len(line) == 2:
				self.shapes.append(
					pyglet.shapes.Line(
						line[0].x, line[0].y,
						line[1].x, line[1].y,
						width,
						color=colour,
						batch=batch
					)
				)
				line = []
				line.append(v)
		if closed:
			self.shapes.append(
					pyglet.shapes.Line(
						vertices[0].x, vertices[0].y,
						vertices[-1].x, vertices[-1].y,
						width,
						color=colour,
						batch=batch
					)
				)

class ArrowLine(LineGroup):
	def __init__(self,
		v1, v2,
		width=1,
		colour=COLOUR_NAMES['AQUA'], 
		batch=None,
		arrow_length=10,
		arrow_offset=0,
		arrow_angle=math.pi/4
	) -> None:
		super(ArrowLine, self).__init__(
			v1,
			batch = batch
		)
		self._endx = v2.x
		self._endy = v2.y
		self.width = width
		self.colour = colour
		self.arrow_length = arrow_length
		self.arrow_offset = arrow_offset
		self.arrow_angle = arrow_angle
		self.shapes.append(
			pyglet.shapes.Line(
				v1.x, v1.y,
				v2.x, v2.y,
				width,
				color=colour,
				batch=batch
			)
		)
		self.update_arrow_tines()
		
	def update_arrow_tines(self):
		#vector from v1 to v2
		arrow_vec = self.end_pos-self.position
		#shrink by arrow offset
		arrow_vec = arrow_vec*(1-self.arrow_offset)
		#back into worldspace
		arrow_anchor = self.position+arrow_vec
		#arrow tines
		av0 = pyglet.math.Vec2(0, self.arrow_length)
		av0 = arrow_vec.from_magnitude(av0.mag)
		av0 = -av0
		av1 = av0.rotate(self.arrow_angle)
		av2 = av0.rotate(-self.arrow_angle)
		av1 += self.end_pos
		av2 += self.end_pos
		if len(self.shapes)>1:
			self.shapes[1].x = arrow_anchor.x
			self.shapes[1].y = arrow_anchor.y
			self.shapes[1].x2 = av1.x
			self.shapes[1].y2 = av1.y	
		else:
			self.shapes.append(
				pyglet.shapes.Line(
					arrow_anchor.x, arrow_anchor.y,
					av1.x, av1.y,
					self.width,
					color=self.colour,
					batch=self.batch
				)
			)
		if len(self.shapes)>2:
			self.shapes[2].x = arrow_anchor.x
			self.shapes[2].y = arrow_anchor.y
			self.shapes[2].x2 = av2.x
			self.shapes[2].y2 = av2.y
		else:
			self.shapes.append(
				pyglet.shapes.Line(
					arrow_anchor.x, arrow_anchor.y,
					av2.x, av2.y,
					self.width,
					color=self.colour,
					batch=self.batch
				)
			)

	@property
	def x2(self):
		return self.end_pos.x

	@x2.setter
	def x2(self, value):
		self.end_pos.x = value
		self.update_arrow_tines()
	
	@property
	def y2(self):
		return self.end_pos.y

	@y2.setter
	def y2(self, value):
		self.end_pos.y = value
		self.update_arrow_tines()

	@property
	def end_pos(self):
		return pyglet.math.Vec2(self._endx, self._endy)

	@end_pos.setter
	def end_pos(self, value):
		self._endx = value.x
		self._endy = value.y
		self.shapes[0].x2 = value.x
		self.shapes[0].y2 = value.y
		self.update_arrow_tines()

class GameWindow(pyglet.window.Window):
	MIN_UPS = 5
	def __init__(self, **kwargs):
		kwargs['config'] = pyglet.gl.Config(double_buffer=True, sample_buffers=1, samples=8) #antialiasing. TODO enable fallback if graphics card doesn't support
		# set and use pyglet window settings
		super(GameWindow, self).__init__(**kwargs)

		# prep the fps display and some labels
		self.fps_display = pyglet.window.FPSDisplay(self)
		self.cfg = {
			'INFO': False
		}
		#pyglet batches vastly improve rendering efficiency, 
		#and allow us to efficiently turn on and off rendering groups of primitives
		self.batches = {
			"main": pyglet.graphics.Batch(),
			"info": pyglet.graphics.Batch()
		}
		self.labels = {
			'mode':	pyglet.text.Label('', x=200, y=self.height-20, color=COLOUR_NAMES['WHITE']),
			'status':	pyglet.text.Label('', x=400, y=self.height-20, color=COLOUR_NAMES['WHITE']) 
		}
		# add extra event handlers we need
		self.add_handlers()

	def _update_label(self, label, text='---'):
		if label in self.labels:
			self.labels[label].text = text
		

	def add_handlers(self):
		@self.event
		#didn't test this... whoops
		def on_resize(cx, cy):
			from game import game
			game.world.cx = cx
			game.world.cy = cy

		@self.event
		def on_mouse_press(x, y, button, modifiers):
			# we need to import game here to avoid circular imports
			# and to make sure that the game object is created before we try to use it
			from game import game
			game.input_mouse(x, y, button, modifiers)


		@self.event
		def on_key_press(symbol, modifiers):
			if symbol == pyglet.window.key.I:
				self.cfg['INFO'] = not self.cfg['INFO']
			# we need to import game here to avoid circular imports
			# and to make sure that the game object is created before we try to use it
			from game import game
			game.input_keyboard(symbol, modifiers)

		@self.event
		def on_draw():
			self.clear()
			self.batches["main"].draw()
			if self.cfg['INFO']:
				self.batches["info"].draw()
			self.fps_display.draw()
			for label in self.labels.values():
				label.draw()
		
	def get_batch(self, batch_name="main"):
		return self.batches[batch_name]

#window creation has to be here so the window object is as global as python lets it be.
settings = {
		# window (passed to pyglet) details
		'width': 800,
		'height': 800,
		'vsync': True,
		'resizable': False,
		'caption': "Autonomous Agent Steering",
	}
	
window = GameWindow(**settings)
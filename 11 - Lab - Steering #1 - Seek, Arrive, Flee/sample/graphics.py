import pyglet

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

class GameWindow(pyglet.window.Window):
	MIN_UPS = 5
	def __init__(self, **kwargs):
		kwargs['config'] = pyglet.gl.Config(double_buffer=True, sample_buffers=1, samples=8) #antialiasing. TODO enable fallback if graphics card doesn't support
		# set and use pyglet window settings
		super(GameWindow, self).__init__(**kwargs)

		# prep the fps display and some labels
		self.fps_display = pyglet.window.FPSDisplay(self)
		#pyglet batches vastly improve rendering efficiency, 
		#and allow us to efficiently turn on and off rendering groups of primitives
		self.batches = {
			"main": pyglet.graphics.Batch(),
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
			# we need to import game here to avoid circular imports
			# and to make sure that the game object is created before we try to use it
			from game import game
			game.input_keyboard(symbol, modifiers)

		@self.event
		def on_draw():
			self.clear()
			self.batches["main"].draw()
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
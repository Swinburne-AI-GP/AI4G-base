import pyglet
import pathlib
from entities import NEUTRAL_ID, SCALE_FACTOR


PLANET_RADIUS_FACTOR = 12
FLEET_SIZE_FACTOR = 0.25
WINDOW_X = 1000
WINDOW_Y = 800

#region colours
COLOR_NAMES = {
	"BLACK": (0.0, 0.0, 0.0, 1),
	"WHITE": (1.0, 1.0, 1.0, 1),
	"GREY": (0.6, 0.6, 0.6, 1),
	"LIGHT_GREY": (0.9, 0.9, 0.9, 1),
	"RED": (1.0, 0.0, 0.0, 1),
	"GREEN": (0.0, 1.0, 0.0, 1),
	"BLUE": (0.0, 0.0, 1.0, 1),
	"PINK": (1.0, 0.7, 0.7, 1),
	"YELLOW": (1.0, 1.0, 0.0, 1),
	"ORANGE": (1.0, 0.7, 0.0, 1),
	"PURPLE": (1.0, 0.0, 0.7, 1),
	"BROWN": (0.5, 0.35, 0.0, 1),
	"AQUA": (0.0, 1.0, 1.0, 1),
	"DARK_GREEN": (0.0, 0.4, 0.0, 1),
	"LIGHT_BLUE": (0.6, 0.6, 1.0, 1),
	"LIGHT_RED": (1.0, 0.6, 0.6, 1),
	"LIGHT_GREEN": (0.6, 1.0, 0.6, 1),
}

def to_rgb(a_gl_color):
	return tuple([int(x * 255) for x in a_gl_color])

COLOR_NAMES_255 = {k: to_rgb(v) for k, v in COLOR_NAMES.items()}
#endregion colours

IMAGES = {
	"background": "images/space.jpg",
}


class RenderableEntity:
	def __init__(self, entity):
		self.entity = entity
		self.x = ((entity.x/SCALE_FACTOR-0.5)*0.9+0.5)*WINDOW_X	#convert from game space to render space
		self.y = ((entity.y/SCALE_FACTOR-0.5)*0.9+0.5)*WINDOW_Y

	def update(self, displayproperty):
		self.label.text = str(self.entity.__getattribute__(displayproperty))

class RenderablePlanet(RenderableEntity):
	def __init__(self, planet, batch, displayproperty, colour):
		super().__init__(planet)
		self.circles = [
			pyglet.shapes.Circle(
				self.x,
				self.y,
				(planet.growth+1) * PLANET_RADIUS_FACTOR,
				color=COLOR_NAMES_255["WHITE"],
				segments=40,
				batch=batch
			),
			pyglet.shapes.Circle(
				self.x,
				self.y,
				(planet.growth+1) * PLANET_RADIUS_FACTOR-2,
				color=colour,
				segments=40,
				batch=batch
			)
		]
		self.label = pyglet.text.Label(
			str(planet.__getattribute__(displayproperty)),
			x=self.x-2,
			y=self.y+4,	#centering is weirdly off
			anchor_x="center", 
			anchor_y="center",
			batch=batch
		)



class RenderableFleet(RenderableEntity):
	def __init__(self, fleet, batch, displayproperty, colour):
		super().__init__(fleet)
		triangle_half_size = min(max(FLEET_SIZE_FACTOR*fleet.ships//2, 10), 50)
		
		#vector pointing straight up defines size of triangle
		v_temp = pyglet.math.Vec2(triangle_half_size, 0)
		#rotate vector to travel direction, v1 is then the 'forward' point of the triangle
		self.v1 = v_temp.from_heading(fleet.heading)
		
		#same vector, a little shorter, forms the trailing points, each rotated 120deg off the travel direction
		v_temp = pyglet.math.Vec2(triangle_half_size*.75, 0)
		v_temp = v_temp.from_heading(fleet.heading)
		v2 = v_temp.rotate(2.094)	#120 deg in radian
		v3 = v_temp.rotate(-2.094)	#120 deg in radian
		
		self.triangle = (pyglet.shapes.Triangle(
			self.v1.x,	#x
			self.v1.y,	#y
			v2.x,	#x2
			v2.y,	#y2
			v3.x,	#x3
			v3.y,	#y3
			color=colour,
			batch=batch
		))
		self.label = pyglet.text.Label(
			str(fleet.__getattribute__(displayproperty)),
			x=self.x,
			y=self.y,
			anchor_x="center", 
			anchor_y="center",
			batch=batch,
			font_size=10
		)

	def update(self, displayproperty):
		super().update(displayproperty)
		self.triangle.x = self.x+self.v1.x
		self.triangle.y = self.y+self.v1.y
		self.label.x=self.x
		self.label.y=self.y

class PlanetWarsEntityRenderer:
	# handles drawing/cached pos/size of PlanetWars game instance for a GUI

	def __init__(self, game, window):
		self.game = game
		#set the playour colours
		self.playercolours = {NEUTRAL_ID: "GREY"}
		for p in game.players:
			if p == NEUTRAL_ID:
				continue
			#players can't be BLACK, WHITE, GREY or LIGHT GREY
			for k in list(COLOR_NAMES.keys())[4:]:
				#colours must be unique
				#TODO: check for running out of colours
				if k not in self.playercolours.values():
					self.playercolours[p] = k
					break
		self.batch = pyglet.graphics.Batch()
		self.displayproperty = "ships"
		self.view_id = 0
		self.sync_all()

	def draw(self):
		#dirty is set whenever a planet changes hands, a fleet is created
		if self.game.dirty:
			self.sync_all()
		# update planet text labels
		for planet in self.renderableplanets:
			planet.update(self.displayproperty)
		#update fleet positions & labels
		for fleet in self.renderablefleets:
			fleet.update(self.displayproperty)
		# draw planets
		self.batch.draw()

	def sync_all(self):
		#sync_all and dirty are used to update the renderer when:
		#planet ownership changes
		#fleets are created and destroyed
		#TODO: this is actually called every tick, which is not ideal
		if self.view_id == 0:
			planets = self.game.planets.values()
			fleets = self.game.fleets.values()
		else:
			player = list(self.game.players.keys())[self.view_id-1]
			planets = self.game.players[player].planets.values()
			fleets = self.game.players[player].fleets.values()
			


		self.renderableplanets = []
		for p in planets:
			#something something view type
			self.renderableplanets.append(
				RenderablePlanet(
					p, 
					self.batch, 
					self.displayproperty, 
					COLOR_NAMES_255[self.playercolours[p.owner]] #bad practice to have properties of p accessed here
				))

		self.renderablefleets = []
		for f in fleets:
			#something something view type
			self.renderablefleets.append(
				RenderableFleet(
					f, 
					self.batch, 
					self.displayproperty, 
					COLOR_NAMES_255[self.playercolours[f.owner]] #bad practice to have properties of p accessed here
				))
		self.game.dirty = False

	def update(self):
		#todo upate text labels after every game loop
		pass


class PlanetWarsUI:
	def __init__(self, window):
		self.fps_display = pyglet.window.FPSDisplay(window)
		self.step_label = pyglet.text.Label(
			"STEP", x=5, y=window.height - 20, color=COLOR_NAMES_255["WHITE"])

	def draw(self):
		self.fps_display.draw()
		self.step_label.draw()


class PlanetWarsWindow(pyglet.window.Window):

	def __init__(self, game):
		self.game = game

		#init the Pyglet window
		super(PlanetWarsWindow, self).__init__(
			WINDOW_X,
			WINDOW_Y,
			vsync=True,
			resizable=False,
			caption="Planet Wars",
			config=pyglet.gl.Config(double_buffer=True, sample_buffers=1, samples=8) #antialiasing. TODO enable fallback if graphics card doesn't support
		)
		#set our location on the screen
		#we use game.extent directly to set screen size opn the previous line,
		#and it's not resizable, so we want it pretty high on the screen
		#essentially there's a 1:1 map between screen size and map size that can be displayed
		self.set_location(10, 10)

		#load the background and scale it to the widnow size
		
		self.bg = pyglet.sprite.Sprite(pyglet.image.load(pathlib.PurePath().joinpath(".\\images\\space.jpg")))
		self.bg.scale_x = self.width / self.bg.image.width
		self.bg.scale_y = self.height / self.bg.image.height
		#load the global UI elements (FPS counter, etc.)
		self.ui = PlanetWarsUI(self)
		#load the renderer for game elements
		self.gamerenderer = PlanetWarsEntityRenderer(self.game, self)

		pyglet.clock.schedule_interval(self.update, 1/60.)
		pyglet.app.run()

	def update(self, args):
		# update step label
		msg = "Step:" + str(self.game.tick)
		if self.game.paused:
			msg += " [PAUSED]"
		msg += f'  --  POV: [{self.gamerenderer.view_id}] '
		if self.gamerenderer.view_id == 0:
			msg += 'ALL'
		else:
			view_id = list(self.game.players.keys())[self.gamerenderer.view_id-1]
			msg += self.game.players[view_id].name
		msg += "  --  Show: " + self.gamerenderer.displayproperty
		self.ui.step_label.text = msg
		
		# gets called by the scheduler at the step_fps interval set
		if self.game:
			self.game.update()
			# Has the game ended? (Should we close?)
			if not self.game.is_alive() or self.game.tick >= self.game.max_ticks:
				self.close()
			if self.game.dirty or True: #or True bypasses game.dirty render optimisation - TODO: figure out a way to bring it back
				self.gamerenderer.sync_all()


	def on_key_press(self, symbol, modifiers):
		# Single Player View, or All View
		#TODO: Pass input into GameRenderer
		if symbol == pyglet.window.key.BRACKETLEFT:
			if self.gamerenderer.view_id > 0:
				self.gamerenderer.view_id -= 1
			else:
				self.gamerenderer.view_id = len(self.game.players)
		if symbol == pyglet.window.key.BRACKETRIGHT:
			if self.gamerenderer.view_id < len(self.game.players):
				self.gamerenderer.view_id += 1
			else:
				self.gamerenderer.view_id = 0
		# Everyone view
		elif symbol == pyglet.window.key.A:
			self.gamerenderer.view_id = 0  # == "all"
		# Planet attribute type to show?
		elif symbol == pyglet.window.key.L:
			i = self.gamerenderer.displayproperty
			l = ["ID", "ships", "vision_age", "owner"]
			self.gamerenderer.displayproperty = l[l.index(i) + 1] if l.index(i) < (len(l) - 1) else l[0]
		# Do one step
		elif symbol == pyglet.window.key.N:
			self.game.update(manual=True)
		# Pause toggle?
		elif symbol == pyglet.window.key.P:
			self.game.paused = not self.game.paused
		# Speed up (+) or slow down (-) the sim
		elif symbol in [pyglet.window.key.PLUS, pyglet.window.key.EQUAL]:
			self.set_fps(pyglet.window.fps + 5)
		elif symbol == pyglet.window.key.MINUS:
			self.set_fps(pyglet.window.fps - 5)
		elif symbol == pyglet.window.key.ESCAPE:
			pyglet.app.exit()

	def on_draw(self):
		self.clear()
		self.bg.draw()
		self.ui.draw()
		self.gamerenderer.draw()
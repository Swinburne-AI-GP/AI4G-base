''' Deceptive PlanetWars Simulation

Created by Michale Jensen (2011) and Clinton Woodward (2012)
contact: cwoodward@swin.edu.au

2015
- Added pyglet graphics support
- Added bot order rules (removed order exploit bugs/features)
- Added multi-player support
2023-03-10:
- Update to Pyglet 2.x, removed old-style OpenGL/glu calls, using pyglet.shapes
- Refactored display classes to suit. Improved view_modes (fog of war)
- Added game rule/exploit/code tests
- Supports dynamic planets (add/remove, move, radii changes in growth/vision)
- Supports 2+ players (even if map doesn't)


'''
from collections import defaultdict
from planet_wars import PlanetWars

from pyglet import window, clock, app, resource, sprite
from pyglet.window import key
from pyglet import shapes
from pyglet.text import Label
import pyglet

COLOR_NAMES = {
    # RGBA. A=1 == solid colour.
    'BLACK':  (0.0, 0.0, 0.0, 1),
    'WHITE':  (1.0, 1.0, 1.0, 1),
    'RED':    (1.0, 0.0, 0.0, 1),
    'GREEN':  (0.0, 1.0, 0.0, 1),
    'BLUE':   (0.0, 0.0, 1.0, 1),
    'GREY':   (0.6, 0.6, 0.6, 1),
    'PINK':   (1.0, 0.7, 0.7, 1),
    'YELLOW': (1.0, 1.0, 0.0, 1),
    'ORANGE': (1.0, 0.7, 0.0, 1),
    'PURPLE': (1.0, 0.0, 0.7, 1),
    'BROWN':  (0.5, 0.35, 0.0, 1),
    'AQUA':   (0.0, 1.0, 1.0, 1),
    'DARK_GREEN':   (0.0, 0.4, 0.0, 1),
    'LIGHT_BLUE':   (0.6, 0.6, 1.0, 1),
    'LIGHT_GREY':   (0.9, 0.9, 0.9, 1),
    'LIGHT_RED':    (1.0, 0.6, 0.6, 1),
    'LIGHT_GREEN':  (0.6, 1.0, 0.6, 1),
    'LIGHT_YELLOW': (1.0, 1.0, 0.6, 1),
    'LIGHT_PURPLE': (1.0, 0.5, 0.8, 1),
}


def to_rgb(a_gl_color):
    return tuple([int(x * 255) for x in a_gl_color])


# convert 0..1.0 values to 0..255 values
COLOR_NAMES = {k: to_rgb(v) for k, v in COLOR_NAMES.items()}

# player to colour map - if more than 6 players, this will need to be extended.
COLOR = {
    0: COLOR_NAMES['LIGHT_GREY'],   # neutral
    1: COLOR_NAMES['LIGHT_RED'],    # player 1
    2: COLOR_NAMES['LIGHT_BLUE'],   # player 2
    3: COLOR_NAMES['LIGHT_GREEN'],  # ...
    4: COLOR_NAMES['LIGHT_YELLOW'],
    5: COLOR_NAMES['LIGHT_PURPLE'],
    6: COLOR_NAMES['LIGHT_GREEN'],
}

IMAGES = {
    'background': 'images/space.jpg',
}


class ScreenPlanet:

    LABEL_COLOR = COLOR_NAMES['BLACK']
    VISION_COLOR = (100, 100, 100, 100)
    BORDER_COLOR = COLOR_NAMES['WHITE']
    # magic values ...
    PLANET_MIN_R = 0.85
    PLANET_FACTOR = 0.10  # 0.05 - scaling factor w.r.t. growth_rate

    def __init__(self, adaptor):
        # refs to keep
        self.planet = None
        self.adaptor = adaptor  # has ratio, batch, convert
        # derived values
        self.radius = None
        self.view_radius = None
        self.color = None
        # graphic element refs - we keep them otherwise some get removed (by gc)
        pos = (0, 0)
        self.circle = None
        self.border = None
        self.view_circle = None
        self.label = Label('', color=self.LABEL_COLOR, x=pos[0], y=pos[1], anchor_x='center', anchor_y='center')
        # cache details - see if new shapes needed
        self._cache = defaultdict(str)  # if key not present, default empty string

    def _check_update_radii(self):
        # radii are scaled and based on "growth rate" (planet size), and "vision radius"
        # ratio is essentially a scaling factor. If window is resizedm this changes
        is_change = False
        if self._cache['ratio'] != self.adaptor.ratio: is_change = True
        if self._cache['growth_rate'] != self.planet.growth_rate: is_change = True
        if self._cache['vision_range'] != self.planet.vision_range: is_change = True

        if is_change:
            # set the values
            ratio = self.adaptor.ratio
            self.radius = (ratio * self.PLANET_MIN_R) + ((self.PLANET_FACTOR * ratio) * self.planet.growth_rate)
            self.view_radius = self.planet.vision_range * ratio  # fog of war vision size
            # note the values
            self._cache.update({
                'ratio': ratio,
                'growth_rate': self.planet.growth_rate,
                'vision_range': self.planet.vision_range
            })
            return True
        else:
            return False  # no change

    def update(self, planet, view_id, view_mode):
        self.planet = planet
        # prep vars
        self.color = COLOR[self.planet.owner_id]
        pos = self.adaptor.game_to_screen(self.planet.x, self.planet.y)

        # check for any changes ...
        do_update = False
        if self._cache['view_mode'] != view_mode: do_update = True  # pos
        if self._cache['owner_id'] != self.planet.owner_id: do_update = True
        if self._cache['pos'] != pos: do_update = True  # pos

        if self._check_update_radii():  # radius (size), vision_range
            self.circle, self.border, self.view_circle = None, None, None
            do_update = True

        # recreate shapes to draw in batch?
        if do_update:
            # print("planet changed:", self.planet.id)
            # background circle
            if not self.circle:
                self.circle = shapes.Circle(
                    x=pos[0], y=pos[1], radius=int(self.radius), color=self.color, batch=self.adaptor.batch)
            else:
                self.circle.x, self.circle.y = pos  # can be updated
                self.circle.color = self.color

            # circle border (arc, default 360 == cirlce)
            if not self.border:
                self.border = shapes.Arc(
                    x=pos[0], y=pos[1], radius=int(self.radius), color=self.BORDER_COLOR, batch=self.adaptor.batch)
            else:
                self.border.x, self.border.y = pos

            # vision circle?
            if view_mode in ['vision_range', 'vision_age'] and view_id in [0, self.planet.owner_id]:
                if not self.view_circle:
                    self.view_circle = shapes.Circle(
                        x=pos[0], y=pos[1], radius=int(self.view_radius),
                        color=self.VISION_COLOR, batch=self.adaptor.batch_vision)
                else:
                    self.view_circle.x, self.view_circle.y = pos
                self.view_circle.visible = True
            else:
                if self.view_circle:
                    self.view_circle.visible = False

            # track new values in cache
            # - note: radii changes already cached
            self._cache['owner_id'] = self.planet.owner_id
            self._cache['pos'] = pos
            self._cache['view_mode'] = view_mode

        # text label change? (common)
        label_text = str(self.planet.__getattribute__(view_mode))
        if self._cache['label_text'] != label_text or do_update:
            # move the existing label
            self.label.x, self.label.y = pos  # x,y tuple
            self.label.text = label_text
            self._cache['label_text'] = label_text

    def draw(self):
        self.label.draw()


class ScreenFleet:

    LABEL_COLOR = COLOR_NAMES['WHITE']
    CIRCLE_SIZE = 1.0  # size not related to fleet size.

    def __init__(self, adaptor):
        # refs to keep
        self.fleet = None
        self.adaptor = adaptor  # has ratio, batch, convert
        # derived values
        self.radius = None
        self.view_radius = None
        self.color = None
        self.view_color = None
        # graphic element refs
        self.circle = None  # really an arc
        self.view_circle = None
        self.label = Label('', color=self.LABEL_COLOR, x=0, y=0, anchor_x='center', anchor_y='center')
        # cache details - see if new shapes needed
        self._cache = defaultdict(str)

    def _check_update_radii(self):
        is_change = False
        if self._cache['ratio'] != self.adaptor.ratio: is_change = True
        if self._cache['vision_range'] != self.fleet.vision_range: is_change = True

        if is_change:
            # set the values
            ratio = self.adaptor.ratio
            self.radius = self.CIRCLE_SIZE * ratio  # has no meaning - visual only.
            self.view_radius = self.fleet.vision_range * ratio  # fog of war vision size
            # note the values
            self._cache.update({
                'ratio': ratio,
                'vision_range': self.fleet.vision_range
            })
            return True
        else:
            return False  # no change

    def update(self, fleet, view_id, view_mode):
        # prep vars
        self.fleet = fleet
        self.color = COLOR[fleet.owner_id]
        self.view_color = tuple([int(v / 2) for v in self.color[:3]] + [150])
        pos = self.adaptor.game_to_screen(fleet.x, fleet.y)

        label_text = str(fleet.__getattribute__(view_mode))

        # check for any changes ...
        do_update = False
        if self._cache['pos'] != pos:
            self._cache['pos'] = pos
            do_update = True

        if self._cache['label_text'] != label_text:
            self._cache['label_text'] = label_text
            self.label.text = label_text

        if self._check_update_radii():  # ie. radius (size) and/or vision_range changed
            # - note: radii changes already cached
            self.circle, self.view_circle = None, None
            do_update = True

        if self._cache['view_id'] != view_id or self._cache['view_mode'] != view_mode:
            self._cache['view_id'] = view_id
            self._cache['view_mode'] = view_mode
            self.circle, self.view_circle = None, None
            do_update = True

        # something changed, so ... create or update shape details
        if do_update:
            # fleet circle (no fill - just border, so an Arc is used)
            if not self.circle:
                self.circle = shapes.Arc(
                    x=pos[0], y=pos[1], radius=int(self.radius),
                    color=self.color, batch=self.adaptor.batch)
            else:
                self.circle.x, self.circle.y = pos  # can be updated

            # vision circle?
            if view_mode in ['vision_range', 'vision_age'] and view_id in [0, self.fleet.owner_id]:
                if not self.view_circle:
                    self.view_circle = shapes.Circle(
                        x=pos[0], y=pos[1], radius=int(self.view_radius),
                        color=self.view_color, batch=self.adaptor.batch_vision)
                else:
                    self.view_circle.x, self.view_circle.y = pos
            else:
                if self.view_circle:
                    self.view_circle.visible = False

            # label pos changed?
            self.label.x, self.label.y = pos  # x,y tuple

    def draw(self):
        # other shape elements are linked to a batch that is drawn.
        self.label.draw()


class PlanetWarsScreenAdapter:
    ''' handles drawing/cached pos/size of PlanetWars game instance for a GUI '''

    def __init__(self, game, background, margin=20):
        self.game = game
        self.screen_planets = {}
        self.screen_fleets = {}
        self.margin = margin
        self.batch = pyglet.graphics.Batch()
        self.batch_vision = pyglet.graphics.Batch()
        # want a pretty background image
        if background:
            self.bk_img = resource.image(IMAGES['background'])
            self.bk_sprite = sprite.Sprite(self.bk_img)
        else:
            self.bk_sprite = None

    def draw(self):
        if self.bk_sprite:
            self.bk_sprite.draw()
        # draws circls/arcs
        self.batch_vision.draw()
        self.batch.draw()
        # draws label text
        for k, p in self.screen_planets.items():
            p.draw()

        for k, f in self.screen_fleets.items():
            f.draw()

    def screen_resize(self, width, height):
        # if the screen has been resized, update point conversion factors
        self.max_y, self.max_x, self.min_y, self.min_x = self.game.extent
        # get game width and height
        self.dx = abs(self.max_x - self.min_x)
        self.dy = abs(self.max_y - self.min_y)
        # set display box width and height
        self.display_dx = width - self.margin * 2
        self.display_dy = height - self.margin * 2
        # get the smaller ratio (width height) for radius drawing
        self.ratio = min(self.display_dx / self.dx, self.display_dy / self.dy)

        # resize the background image also
        if self.bk_sprite:
            self.bk_img.width = width
            self.bk_img.height = height
            self.bk_sprite = sprite.Sprite(self.bk_img)

    def sync_all(self, view_id, view_mode):
        # recache all planets/fleets (may have changed)
        if view_id == 0:
            planets = self.game.planets
            fleets = self.game.fleets
        else:
            planets = self.game.players[view_id].planets
            fleets = self.game.players[view_id].fleets

        # Planets
        # - remove any screen_planets for planets that don't exist anymore. (Only in dynamic maps)
        self.screen_planets = {k: p for k, p in self.screen_planets.items() if k in planets}
        for k, p in planets.items():
            if k not in self.screen_planets:
                self.screen_planets[k] = ScreenPlanet(self)
            # view_mode - the detail text to show (id, num_ships, vision etc)
            self.screen_planets[k].update(p, view_id, view_mode)

        # Fleets
        # - remove any screen_fleets for fleets that don't exist anymore
        self.screen_fleets = {k: f for k, f in self.screen_fleets.items() if k in fleets}
        for k, f in fleets.items():
            if k not in self.screen_fleets:
                self.screen_fleets[k] = ScreenFleet(self)
            self.screen_fleets[k].update(f, view_id, view_mode)

    def game_to_screen(self, wx, wy):
        # convert xy values from game space to screen space
        x = ((wx - self.min_x) / self.dx) * self.display_dx + self.margin
        y = ((wy - self.min_y) / self.dy) * self.display_dy + self.margin
        return (x, y)


class PlanetWarsWindow(window.Window):

    MIN_UPS = 5

    def __init__(self, **kwargs):
        # rip out the game settings we want
        players = kwargs.pop('players')
        # read the map file and create game with it
        gamestate = open(kwargs.pop('map_file')).read()
        self.game = PlanetWars(gamestate)
        # add players (based on names matching bot class names)
        for p in players:
            self.game.add_player(p)
        # other args?
        self.max_tick = kwargs.pop('max_game_length')
        self.paused = kwargs.pop('start_paused')
        self.game_over_quit = kwargs.pop('game_over_quit')
        target_ups = max(int(kwargs.pop('update_target')), self.MIN_UPS)
        background_img = kwargs.pop('background_img')

        # set and use pyglet window settings
        super(PlanetWarsWindow, self).__init__(**kwargs)

        # prep the fps display and some labels
        self.fps_display = pyglet.window.FPSDisplay(self)
        self.step_label = Label('STEP', x=5, y=self.height - 20, color=COLOR_NAMES['WHITE'])
        self.ups_label = Label('UPS', x=self.width - 10, y=10, color=COLOR_NAMES['WHITE'], anchor_x='right')
        self.mode_label = Label("MODE", x=5, y=self.height - 50, color=COLOR_NAMES['WHITE'])
        self.ups = 0
        self.set_ups(target_ups)
        self.view_id = 0
        self.view_mode = 'num_ships'

        # create adaptor to help with drawing, and batch for drawing
        self.adaptor = PlanetWarsScreenAdapter(self.game, background_img)

        # prep the game (space!)
        self.reset_space()
        # add extra event handlers we need
        self.add_handlers()

    def reset_space(self):
        self.adaptor.screen_resize(self.width, self.height)
        self.adaptor.sync_all(self.view_id, self.view_mode)

    def set_ups(self, ups):
        '''target game updates per second, using clock interval callback to update.'''
        self.ups = max(ups, self.MIN_UPS)
        clock.unschedule(self.update)  # remove old (if there)
        clock.schedule_interval(self.update, 1.0 / self.ups)
        print(f"Target game update interval set to {self.ups} / sec")

    def update(self, dt):
        # gets called by the scheduler at the step_ups interval set
        game = self.game
        if game:
            if not self.paused:
                game.update()
                self.adaptor.sync_all(self.view_id, self.view_mode)

            # update step label
            msg = f'Step: {game.tick} '
            if self.paused:
                msg += '[PAUSED] '
            msg += f' -- POV: [{self.view_id}] '
            if self.view_id in game.players:
                msg += f' BOT = {game.players[self.view_id].name}'
            elif self.view_id == 0:
                msg += ' All '
            self.step_label.text = msg
            self.mode_label.text = 'Show: ' + self.view_mode

            # time since last update call? ie. the actual game update interval?
            # - ie. actual updates per second c/w target
            ups = 1.0 / dt
            self.ups_label.text = f"Update/sec: {ups:.2f} [target: {self.ups}]"

            # Has the game ended? (Should we close?)
            if not self.game.is_alive() or self.game.tick >= self.max_tick:
                self.paused = True
                if self.game_over_quit:
                    self.close()

    def add_handlers(self):
        @self.event
        def on_resize(cx, cy):
            self.adaptor.screen_resize(cx, cy)
            pass

        @self.event
        def on_mouse_press(x, y, button, modifiers):
            pass

        @self.event
        def on_key_press(symbol, modifiers):
            # Single Player View, or All View
            if symbol == key.BRACKETLEFT:
                self.view_id = self.view_id - 1 if self.view_id > 1 else len(self.game.players)
            if symbol == key.BRACKETRIGHT:
                self.view_id = self.view_id + 1 if self.view_id < len(self.game.players) else 1
            # Everyone view
            elif symbol == key.A:
                self.view_id = 0  # == "all"
            # Planet attribute type to show?
            elif symbol == key.L:
                i = self.view_mode
                modes = ['id', 'num_ships', 'vision_age', 'owner_id', 'growth_rate', 'vision_range']
                self.view_mode = modes[modes.index(i) + 1] if modes.index(i) < (len(modes) - 1) else modes[0]
            # Reset?
            elif symbol == key.R:
                self.reset_space()
            # Do one step
            elif symbol == key.N:
                self.game.update()
            # Pause toggle?
            elif symbol == key.P:
                self.paused = not self.paused
            # Speed up (+) or slow down (-) the sim
            elif symbol in [key.PLUS, key.EQUAL]:
                self.set_ups(self.ups + 5)
            elif symbol == key.MINUS:
                self.set_ups(self.ups - 5)

            self.adaptor.sync_all(self.view_id, self.view_mode)

        @self.event
        def on_draw():
            self.clear()
            self.adaptor.draw()
            self.fps_display.draw()
            self.step_label.draw()
            self.ups_label.draw()
            self.mode_label.draw()


if __name__ == '__main__':

    # Supplied map sizes were generated for (500, 500) size
    # Scale the visual size with this
    screen_size_scale = 2

    settings = {
        # text file - planet position/size, player start locations (and fleet details)
        'map_file': './maps/map5.txt',
        # usually two players (what maps expect) but can have more
        'players': [
            'OneMove',
            'Blanko'
            #'PingPong',
        ],
        # start / stop conditions
        'max_game_length': 500,
        'start_paused': True,
        'game_over_quit': True,  # quit (close window) when game stops
        # game updates per second (not UI) ?
        'update_target': 20,
        # show the image or just black?
        'background_img': True,
        # window (passed to pyglet) details
        'width': int(500 * screen_size_scale),
        'height': int(500 * screen_size_scale),
        'vsync': True,
        'resizable': False,
    }

    window = PlanetWarsWindow(**settings)
    app.run()
    window.game.logger.flush()

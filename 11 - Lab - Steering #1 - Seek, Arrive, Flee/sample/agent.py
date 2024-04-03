'''An agent with Seek, Flee, Arrive, Pursuit behaviours

Created for COS30002 AI for Games, by 
    Clinton Woodward <cwoodward@swin.edu.au>
    James Bonner <jbonner@swin.edu.au>
For class use only. Do not publically share or post this code without permission.

'''
import pyglet
from vector2d import Vector2D
from vector2d import Point2D
from math import sin, cos, radians
from random import random, randrange
from graphics import COLOUR_NAMES, window

AGENT_MODES = {
    pyglet.window.key._1: 'seek',
    pyglet.window.key._2: 'arrive_slow',
    pyglet.window.key._3: 'arrive_normal',
    pyglet.window.key._4: 'arrive_fast',
    pyglet.window.key._5: 'flee',
    pyglet.window.key._6: 'pursuit'
}

class Agent(object):

    # NOTE: Class Object (not *instance*) variables!
    DECELERATION_SPEEDS = {
        'slow': 0.9,
        ### ADD 'normal' and 'fast' speeds here
    }

    def __init__(self, world=None, scale=30.0, mass=1.0, mode='seek'):
        # keep a reference to the world object
        self.world = world
        self.mode = mode
        # where am i and where am i going? random
        dir = radians(random()*360)
        self.pos = Vector2D(randrange(world.cx), randrange(world.cy))
        self.vel = Vector2D()
        self.heading = Vector2D(sin(dir), cos(dir))
        self.side = self.heading.perp()
        self.scale = Vector2D(scale, scale)  # easy scaling of agent size
        self.acceleration = Vector2D()  # current steering force
        self.mass = mass
        # limits?
        self.max_speed = 2500.0
        # data for drawing this agent
        self.color = 'ORANGE'
        self.vehicle_shape = [
            Point2D(-10,  6),
            Point2D( 10,  0),
            Point2D(-10, -6)
        ]
        self.vehicle = pyglet.shapes.Triangle(
            self.pos.x+self.vehicle_shape[1].x, self.pos.y+self.vehicle_shape[1].y,
            self.pos.x+self.vehicle_shape[0].x, self.pos.y+self.vehicle_shape[0].y,
            self.pos.x+self.vehicle_shape[2].x, self.pos.y+self.vehicle_shape[2].y,
            color= COLOUR_NAMES[self.color],
            batch=window.get_batch("main")
        )

    def calculate(self):
        # reset the steering force
        mode = self.mode
        target_pos = Vector2D(self.world.target.x, self.world.target.y)
        if mode == 'seek':
            accel = self.seek(target_pos)
        elif mode == 'arrive_slow':
            accel = self.arrive(target_pos, 'slow')
##        elif mode == 'arrive_normal':
##            force = self.arrive(target_pos, 'normal')
##        elif mode == 'arrive_fast':
##            force = self.arrive(target_pos, 'fast')
        elif mode == 'flee':
            accel = self.flee(target_pos)
##        elif mode == 'pursuit':
##            force = self.pursuit(self.world.hunter)
        else:
            accel = Vector2D()
        self.acceleration = accel
        return accel

    def update(self, delta):
        ''' update vehicle position and orientation '''
        acceleration = self.calculate()
        # new velocity
        self.vel += acceleration * delta
        # check for limits of new velocity
        self.vel.truncate(self.max_speed)
        # update position
        self.pos += self.vel * delta
        # update heading is non-zero velocity (moving)
        if self.vel.lengthSq() > 0.00000001:
            self.heading = self.vel.get_normalised()
            self.side = self.heading.perp()
        # treat world as continuous space - wrap new position if needed
        self.world.wrap_around(self.pos)
        # update the vehicle render position
        self.vehicle.x = self.pos.x+self.vehicle_shape[0].x
        self.vehicle.y = self.pos.y+self.vehicle_shape[0].y
        self.vehicle.rotation = -self.heading.angle_degrees()


    def speed(self):
        return self.vel.length()

    #--------------------------------------------------------------------------

    def seek(self, target_pos):
        ''' move towards target position '''
        desired_vel = (target_pos - self.pos).normalise() * self.max_speed
        return (desired_vel - self.vel)

    def flee(self, hunter_pos):
        ''' move away from hunter position '''
## add panic distance (second)
## add flee calculations (first)
        return Vector2D()

    def arrive(self, target_pos, speed):
        ''' this behaviour is similar to seek() but it attempts to arrive at
            the target position with a zero velocity'''
        decel_rate = self.DECELERATION_SPEEDS[speed]
        to_target = target_pos - self.pos
        dist = to_target.length()
        if dist > 0:
            # calculate the speed required to reach the target given the
            # desired deceleration rate
            speed = dist / decel_rate
            # make sure the velocity does not exceed the max
            speed = min(speed, self.max_speed)
            # from here proceed just like Seek except we don't need to
            # normalize the to_target vector because we have already gone to the
            # trouble of calculating its length for dist.
            desired_vel = to_target * (speed / dist)
            return (desired_vel - self.vel)
        return Vector2D(0, 0)

    def pursuit(self, evader):
        ''' this behaviour predicts where an agent will be in time T and seeks
            towards that point to intercept it. '''
## OPTIONAL EXTRA... pursuit (you'll need something to pursue!)
        return Vector2D()

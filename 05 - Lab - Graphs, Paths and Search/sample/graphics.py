'''A simple proceedural style graphics drawing wrapper.

Created for COS30002 AI for Games, Lab,
by Clinton Woodward <cwoodward@swin.edu.au>

For class use only. Do not publically share or post this code without
permission.

This module creates a simple object named "egi", which is an instance of the
EasyGraphics interface, as well as making the pyglet key codes avaiable as
KEY.

Note: This has not been designed for performance! In particular, excessive
text drawing will be very expensive. If you need better performance, you
should implement opengl code for yourself.

'''

from pyglet.gl import *
from pyglet import text, media, window, clock
from math import cos, sin, pi

KEY = window.key # the key codes

COLOR_NAMES = {
    'BLACK':  (0.0, 0.0, 0.0, 1),
    'WHITE':  (1.0, 1.0, 1.0, 1),
    'RED':    (1.0, 0.0, 0.0, 1),
    'GREEN':  (0.0, 1.0, 0.0, 1),
    'BLUE':   (0.0, 0.0 ,1.0, 1),
    'GREY':   (0.6, 0.6, 0.6, 1),
    'PINK':   (1.0, 0.7, 0.7, 1),
    'YELLOW': (1.0, 1.0, 0.0, 1),
    'ORANGE': (1.0, 0.7, 0.0, 1),
    'PURPLE': (1.0, 0.0, 0.7, 1),
    'BROWN':  (0.5, 0.35,0.0, 1),
    'AQUA':   (0.0, 1.0, 1.0, 1),
    'DARK_GREEN': (0.0, 0.4, 0.0, 1),
    'LIGHT_GREEN':(0.6, 1.0, 0.6, 1),
    'LIGHT_BLUE': (0.6, 0.6, 1.0, 1),
    'LIGHT_GREY': (0.8, 0.8, 0.8, 1),
    'LIGHT_PINK': (1.0, 0.9, 0.9, 1)
}

class EasyGraphics(object):

    def __init__(self):
        # current "pen" colour of lines
        self.pen_color = (1.0, 0.0, 0.0, 1.0)
        self.stroke = 1.0 # - thickness the default

    def InitWithPyglet(self, window):
        # stuff that needs to be done *after* the pyglet window is created
        self.set_pen_color(self.pen_color)
        self.set_stroke(self.stroke)
        self.window = window
        # prep the text object
        self.text = text.Label('', color=(1, 1, 1, 1),
                              anchor_y='bottom', anchor_x='left')
        # prep the quadric object used by glu* functions (circle)
        # styles GLU_LINE, GLU_FILL, GLU_SILHOUETTE, GLU_POINT
        self.qobj = gluNewQuadric()
        gluQuadricDrawStyle(self.qobj, GLU_SILHOUETTE)

    def dot(self, x=0, y=0, pos=None, color=None):
        ''' Draw a single pixel at a given location. will use pos (with x and y
            values) if provided. Colour is (R,G,B,A) values 0.0 to 1.0 '''
        if pos is not None:
            x, y = pos.x, pos.y
        if color is not None:
            glColor4f(*color)
        glBegin(GL_POINTS) # draw points (only one!)
        glVertex3f(x, y, 0.0)
        glEnd()

    def line(self, x1=0, y1=0, x2=0, y2=0, pos1=None, pos2=None):
        ''' Draw a single line. Either with xy values, or two position (that
            contain x and y values). Uses existing colour and stroke values. '''
        if pos1 is not None and pos2 is not None:
            x1, y1, x2, y2 = pos1.x, pos1.y, pos2.x, pos2.y
        glBegin(GL_LINES)
        glVertex2f(x1, y1)
        glVertex2f(x2, y2)
        glEnd()

    def line_by_pos(self,pos1,pos2):
        ''' Draw a single line. Either with xy values, or two position (that
            contain x and y values). Uses existing colour and stroke values. '''
        x1, y1, x2, y2 = pos1.x, pos1.y, pos2.x, pos2.y
        glBegin(GL_LINES)
        glVertex2f(x1, y1)
        glVertex2f(x2, y2)
        glEnd()

    def polyline(self, points):
        if len(points) < 2: return
        pts = [(p.x, p.y) for p in points] # convert to list of tuples
        pts = ((GLfloat * 2)*len(pts))(*pts) # convert to GLfloat list
        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(2,GL_FLOAT, 0, pts)
        glDrawArrays(GL_LINE_STRIP, 0, len(pts))
        glPopClientAttrib()

    def line_with_arrow(self,v1,v2,size):
        norm = v2-v1
        norm.normalise()
        # calculate where arrow is attached
        xpoint = v2 - (norm * size)
        # calculate the two extra points required to make the arrowhead
        ap1 = xpoint + (norm.perp() * 0.4 * size)
        ap2 = xpoint - (norm.perp() * 0.4 * size)
        # draw line from start to head crossing point
        glBegin(GL_LINES)
        glVertex2f(v1.x, v1.y)
        glVertex2f(xpoint.x, xpoint.y)
        glEnd()
        # draw triangle for head
        self.closed_shape((v2, ap1, ap2), filled=False)

    def cross(self, pos, diameter):
        d = diameter
        x, y = pos.x, pos.y
        glBegin(GL_LINES)
        # TL to BR
        glVertex2f(x-d, y-d)
        glVertex2f(x+d, y+d)
        # TR to BL
        glVertex2f(x+d, y-d)
        glVertex2f(x-d, y+d)
        glEnd()

    def rect(self, left, top, right, bottom, filled=False):
        if filled:
            glBegin(GL_QUADS)
        else:
            glBegin(GL_LINE_LOOP)
        # A single quad - TL to TR to BR to BL (to TL...)
        glVertex2f(left,top)
        glVertex2f(right,top)
        glVertex2f(right,bottom)
        glVertex2f(left,bottom)
        glEnd()

    def closed_shape(self, points, filled=False):
        if len(points) < 2: return
        gl_array_type = GL_POLYGON if filled else GL_LINE_LOOP
        # convert points to a list of types, then GLfloat list
        pts = [(p.x, p.y) for p in points]
        pts = ((GLfloat * 2)*len(pts))(*pts)
        # tell GL system about the array of points
        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(2,GL_FLOAT, 0, pts)
        # draw array of points, and clean up
        glDrawArrays(gl_array_type, 0, len(pts))
        glPopClientAttrib()

    def circle(self, pos, radius, filled=False, slices=0):
        glPushMatrix()
        glTranslatef(pos.x, pos.y, 0.0)
        gluDisk(self.qobj, 0, radius, 32, 1) # default style (filled? line?)
        glPopMatrix()

    # ----- COLOUR/STROKE STUFF -----
    def set_pen_color(self, color=None, name=None):
        if name is not None:
            color = COLOR_NAMES[name]
        self.curr_color = color
        glColor4f(*self.curr_color)

    def red_pen(self):    self.set_pen_color(name='RED')
    def blue_pen(self):   self.set_pen_color(name='BLUE')
    def green_pen(self):  self.set_pen_color(name='GREEN')
    def black_pen(self):  self.set_pen_color(name='BLACK')
    def white_pen(self):  self.set_pen_color(name='WHITE')
    def grey_pen(self):   self.set_pen_color(name='GREY')
    def aqua_pen(self):   self.set_pen_color(name='AQUA')
    def orange_pen(self): self.set_pen_color(name='ORANGE')

    def set_stroke(self, stroke):
        self.stroke = stroke
        glLineWidth(self.stroke)


    # ----- TEXT METHODS -----
    def text_color(self,color=None,name=None):
        ''' Colour is a tuple (R,G,B,A) with values from 0.0 to 1.0 '''
        if name is not None:
            color = COLOR_NAMES[name]
        self.text.color = color #

    def text_at_pos(self, x, y, text):
        self.text.text = text
        self.text.x = x
        self.text.y = self.window.height + y if y < 0 else y
        self.text.draw()

    # ----- simple wrappers to gl push / pop matrix -----
    def push(self, x, y):
        glPushMatrix()
        glTranslatef(x,y,0.0)
    def pop(self):
        glPopMatrix()

# create an instance for anyone to use
egi = EasyGraphics()

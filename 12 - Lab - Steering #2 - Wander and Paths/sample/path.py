'''Path container to support easy path following by Agents

Created for COS30002 AI for Games by Clinton Woodward <cwoodward@swin.edu.au>

For class use only. Do not publically share or post this code without permission.

'''

from random import random, uniform
from matrix33 import Matrix33
from vector2d import Vector2D
from graphics import egi

from math import pi

TWO_PI = pi * 2.0


def vec2D_rotate_around_origin(vec, rads):
    ''' Rotates a vector a given angle (in radians) around the origin.
        Note: the vec parameter is altered (does not return a new vector. '''
    mat = Matrix33()
    mat.rotate_update(rads)
    mat.transform_vector2d(vec)


class Path(object):
    ''' Container to hold a number of way points and a cursor to the
        current way point. The cursor can be moved to the next way point by
        calling set_next_way_pt(). Paths can be open or looped. '''

    def __init__(self, num_pts=0, minx=0, miny=0, maxx=0, maxy=0, looped=False):
        ''' If number of points (num_pts) is provided, a path of random
            non-overlapping waypoints will be created in the region specified
            by the min/max x/y values provided. If the path is looped, the last
            way point is connected to the first. '''
        self.looped = looped
        self._num_pts = num_pts
        self._cur_pt_idx = -1
        self._pts = []
        if num_pts > 0:
            self.create_random_path(num_pts, minx, miny, maxx, maxy)

    def current_pt(self):
        ''' Return the way point of the path indicated by the current point
            index. '''
        return self._pts[self._cur_pt_idx]

    def inc_current_pt(self):
        ''' Update the current point to the next in the path list.
            Resets to the first point if looped is True. '''
        assert self._num_pts > 0
        self._cur_pt_idx += 1
        if self.is_finished() and self.looped:
            self._cur_pt_idx = 0

    def is_finished(self):
        ''' Return True if at the end of the path. '''
        return self._cur_pt_idx >= self._num_pts - 1

    def create_random_path(self, num_pts, minx, miny, maxx, maxy, looped=False):
        ''' Creates random path within the rectangle described by the
            min/max values. Stores and returns path. '''
        self.looped = looped
        self.clear()
        midX = (maxx + minx) / 2.0
        midY = (maxy + miny) / 2.0
        smaller = min(midX, midY)
        spacing = TWO_PI / num_pts

        for i in range(num_pts):
            radial_dist = uniform(smaller*0.2, smaller)
            temp = Vector2D(radial_dist, 0.0)
            vec2D_rotate_around_origin(temp, i*spacing)
            temp.x += midX
            temp.y += midY
            self._pts.append(temp)

        self._reset()  # reset num_pts and cur_pt_idx
        return self._pts

    def add_way_pt(self, new_pt):
        ''' Add the waypoint to the end of the path.'''
        self._pts.append(new_pt)
        self._num_pts += 1

    def set_pts(self, path_pts):
        ''' Replace our internal set of points with the container of points
            provided. '''
        self._pts = path_pts
        self._reset()

    def _reset(self):
        ''' Point to the first waypoint and set the limit count based on the
            number of points we've been given. '''
        self._cur_pt_idx = 0
        self._num_pts = len(self._pts)

    def clear(self):
        ''' Remove all way points and reset internal counters. '''
        self._pts = []
        self._reset()

    def get_pts(self):
        ''' Simple wrapper to return a reference to the internal list of
            points.'''
        return self._pts

    def render(self):
        ''' Draw the path, open or closed, using the current pen colour. '''
        # draw base line
        egi.blue_pen()
        if self.looped:
            egi.closed_shape(self._pts)
        else:
            egi.polyline(self._pts)
        # draw current waypoint
        egi.orange_pen()
        wp = self.current_pt()
        egi.circle(pos=wp, radius=5, slices=32)


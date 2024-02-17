'''2D Point

Created for COS30002 AI for Games by Clinton Woodward <cwoodward@swin.edu.au>

For class use only. Do not publically share or post this code without permission.

'''


class Point2D(object):

    __slots__ = ('x', 'y')

    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def copy(self):
        return Point2D(self.x, self.y)

    def __str__(self):
        return '(%5.2f,%5.2f)' % (self.x, self.y)

'''3x3 matrix class for 2d operations on 2d points

Created for COS30002 AI for Games by Clinton Woodward <cwoodward@swin.edu.au>

For class use only. Do not publically share or post this code without permission.

Updated by Steve Dower

'''

from math import cos, sin


class Matrix33(object):
    '''3x3 matrix for two-dimensional operations.'''

    def __init__(self, m=None):
        if isinstance(m, Matrix33):
            m = list(m._m)

        self._m = m or [1., 0., 0., 0., 1., 0., 0., 0., 1.]

    def reset(self):
        self._m = [1., 0., 0., 0., 1., 0., 0., 0., 1.]

    def translate(self, x, y):
        '''Returns this matrix translated by x, y.'''
        return self * Matrix33([1., 0., 0., 0., 1., 0., x, y, 1.])

    def translate_update(self, x, y):
        '''Update self (matrix) with a translation amount of x,y'''
        self._fast_imul(Matrix33([1., 0., 0., 0., 1., 0., x, y, 1.]))

    def scale(self, xscale, yscale):
        '''Returns this matrix scaled by xscale and yscale'''
        return self * Matrix33([xscale, 0., 0., 0., yscale, 0., 0., 0., 1.])

    def scale_update(self, xscale, yscale):
        '''Update self with scale amounts of xscale and yscale'''
        self._fast_imul(Matrix33([xscale, 0., 0., 0., yscale, 0., 0., 0., 1.]))

    def rotate(self, rads):
        '''Returns this matrix rotated by rad (radians)'''
        sin_r = sin(rads)
        cos_r = cos(rads)
        return self * Matrix33([cos_r, sin_r, 0., -sin_r, cos_r, 0., 0., 0., 1.])

    def rotate_update(self, rads):
        '''Update self with rotation amount of rad (radians)'''
        sin_r = sin(rads)
        cos_r = cos(rads)
        self._fast_imul(Matrix33([cos_r, sin_r, 0., -sin_r, cos_r, 0., 0., 0., 1.]))

    def rotate_by_vectors(self, fwd, side):
        ''' Update self with rotation based on forward and side vectors.'''
        return self * Matrix33([fwd.x, fwd.y, 0., side.x, side.y, 0., 0., 0., 1.])

    def rotate_by_vectors_update(self, fwd, side):
        ''' Update self with rotation based on forward and side vectors.'''
        self._fast_imul(Matrix33([fwd.x, fwd.y, 0., side.x, side.y, 0., 0., 0., 1.]))

    def transform_vector2d_list(self, points):
        ''' Apply self as a transformation matrix to the provided collection
        of Vector2D points '''
        a11, a12, a13, a21, a22, a23, a31, a32, a33 = self._m
        # apply self matrix as a transformation to each pt's coordinates
        for pt in points:
            tmp_x = a11*pt.x + a21*pt.y + a31
            tmp_y = a12*pt.x + a22*pt.y + a32
            pt.x = tmp_x
            pt.y = tmp_y

    def transform_vector2d(self, pt):
        ''' Apply self as a transformation matrix to a single point '''
        a11, a12, a13, a21, a22, a23, a31, a32, a33 = self._m
        # apply self matrix as a transformation to pt's coordinates
        tmp_x = a11*pt.x + a21*pt.y + a31
        tmp_y = a12*pt.x + a22*pt.y + a32
        pt.x = tmp_x
        pt.y = tmp_y

    def __mul__(self, rhs):  # the self * rhs operator
        ''' 3x3 matrix matrix multiplication. Rarely used however...'''
        a11, a12, a13,  a21, a22, a23,  a31, a32, a33 = self._m
        b11, b12, b13,  b21, b22, b23,  b31, b32, b33 = rhs._m

        retm = [
            a11*b11 + a12*b21 + a13*b31,
            a11*b12 + a12*b22 + a13*b32,
            a11*b13 + a12*b23 + a13*b33,

            a21*b11 + a22*b21 + a23*b31,
            a21*b12 + a22*b22 + a23*b32,
            a21*b13 + a22*b23 + a23*b33,

            a31*b11 + a32*b21 + a33*b31,
            a31*b12 + a32*b22 + a33*b32,
            a31*b13 + a32*b23 + a33*b33
        ]

        return Matrix33(retm)

    def __imul__(self, rhs):  # the *= operator
        ''' 3x3 matrix matrix multiplication result applied to self. '''
        a11, a12, a13,  a21, a22, a23,  a31, a32, a33 = self._m
        b11, b12, b13,  b21, b22, b23,  b31, b32, b33 = rhs._m

        self._m = [
            a11*b11 + a12*b21 + a13*b31,
            a11*b12 + a12*b22 + a13*b32,
            a11*b13 + a12*b23 + a13*b33,

            a21*b11 + a22*b21 + a23*b31,
            a21*b12 + a22*b22 + a23*b32,
            a21*b13 + a22*b23 + a23*b33,

            a31*b11 + a32*b21 + a33*b31,
            a31*b12 + a32*b22 + a33*b32,
            a31*b13 + a32*b23 + a33*b33
        ]

    def _fast_imul(self, rhs):  # the *= operator
        ''' Fast 3x3 matrix multiplication result applied to self.
            Because column 3 is always 0,0,1 for translate, scale and rotate
            we can reduce this operation for these cases.'''
        a11, a12, a13,  a21, a22, a23,  a31, a32, a33 = self._m
        #         0.0             0.0             1.0
        b11, b12, b13,  b21, b22, b23,  b31, b32, b33 = rhs._m

        self._m = [
            a11*b11 + a12*b21, a11*b12 + a12*b22, 0,
            a21*b11 + a22*b21, a21*b12 + a22*b22, 0,
            a31*b11 + a32*b21 + b31, a31*b12 + a32*b22 + b32, 1
        ]

    def __str__(self):
        return '[%5.1f, %5.1f, %5.1f]\n[%5.1f, %5.1f, %5.1f]\n[%5.1f, %5.1f, %5.1f]' % tuple(self._m)

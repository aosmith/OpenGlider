import copy
import math
import numpy
from openglider import Profile2D
from openglider.airfoil import Profile3D, get_x_value
from openglider.utils.cache import cached_property, CachedObject
from openglider.utils.bezier import BezierCurve
from openglider.vector import rotation_3d, HashedList


class Rib(CachedObject):
    """Openglider Rib Class: contains a airfoil, needs a startpoint, angle (arcwide), angle of attack,
        glide-wide rotation and glider ratio.
        optional: name, absolute aoa (bool), startposition"""
    hashlist = ('aoa_absolute', 'glide', 'arcang', 'zrot', 'chord', 'pos')  # pos

    def __init__(self, profile_2d=None,
                 ballooning=None,
                 startpoint=None,
                 chord=1.,
                 arcang=0, aoa=0, zrot=0,
                 glide=1, name="unnamed rib", aoa_abs=False, startpos=0.):
        # TODO: Startpos > Set Rotation Axis in Percent
        self.name = name
        self.profile_2d = profile_2d or Profile2D()
        self.ballooning = ballooning
        self.glide = glide
        self._aoa = (0, 0)
        if aoa_abs:
            self.aoa_absolute = aoa
        else:
            self.aoa_relative = aoa
        self.arcang = arcang
        self.zrot = zrot
        self.pos = startpoint  # or HashedList([0, 0, 0])
        self.chord = chord

    def __json__(self):
        return {"profile_2d": self.profile_2d,
                "ballooning": self.ballooning,
                "startpoint": self.pos.tolist(),
                "chord": self.chord,
                "arcang": self.arcang,
                "aoa": self._aoa[0],
                "zrot": self.zrot,
                "glide": self.glide,
                "name": self.name,
                "aoa_abs": self._aoa[1]}

    def align(self, point):
        if len(point) == 2:
            return self.align([point[0], point[1], 0])
        elif len(point) == 3:
            return self.pos + self.rotation_matrix.dot(point) * self.chord
        raise ValueError("Can only Align one single 2D or 3D-Point")

    @property
    def aoa_absolute(self):
        if not self._aoa[1]:
            return self._aoa[0]
        else:
            return self._aoa[0] - self.__aoa_diff(self.arcang, self.glide)

    @aoa_absolute.setter
    def aoa_absolute(self, aoa):
        self._aoa = (aoa, False)

    @property
    def aoa_relative(self):
        if self._aoa[1]:
            return self._aoa[0]
        else:
            return self._aoa[0] + self.__aoa_diff(self.arcang, self.glide)

    @aoa_relative.setter
    def aoa_relative(self, aoa):
        self._aoa = (aoa, True)

    @cached_property('profile_3d')
    def normvectors(self):
        return map(lambda x: self.rotation_matrix.dot([x[0], x[1], 0]), self.profile_2d.normvectors)

    @cached_property('arcang', 'glide', 'zrot', '_aoa')
    def rotation_matrix(self):
        zrot = numpy.arctan(self.arcang) / self.glide * self.zrot
        return rotation_rib(self.aoa_absolute, self.arcang, zrot)

    @cached_property('self')
    def profile_3d(self):
        if self.profile_2d.data is not None:
            return Profile3D(map(self.align, self.profile_2d.data))
        else:
            raise ValueError("no 2d-profile present fortharib at rib {}".format(
                self.name))

    def point(self, x_value):
        return self.align(self.profile_2d.point(x_value))

    @staticmethod
    def __aoa_diff(arc_angle, glide):
        ##Formula for aoa rel/abs: ArcTan[Cos[alpha]/gleitzahl]-aoa[rad];
        return numpy.arctan(numpy.cos(arc_angle) / glide)

    def mirror(self):
        self.arcang = -self.arcang
        self.zrot = -self.zrot
        self.pos = numpy.multiply(self.pos, [1, -1., 1])

    def copy(self):
        new = copy.deepcopy(self)
        new.name += "_copy"
        return new


class MiniRib():
    def __init__(self, yvalue, front_cut, back_cut=1, func=None, name="minirib"):
        #Profile3D.__init__(self, [], name)

        if not func:  # Function is a bezier-function depending on front/back
            if front_cut > 0:
                points = [[front_cut, 1], [front_cut * 2. / 3 + back_cut * 1. / 3]]  #
            else:
                points = [[front_cut, 0]]

            if back_cut < 1:
                points = points + [[front_cut * 1. / 3 + back_cut * 2. / 3, 0], [back_cut, 1]]
            else:
                points = points + [[back_cut, 0]]
            func = BezierCurve(points).interpolation()

        self.__function__ = func

        self.y_value = yvalue
        self.front_cut = front_cut
        self.back_cut = back_cut

    def function(self, x):
        if self.front_cut <= abs(x) <= self.back_cut:
            return min(1, max(0, self.__function__(abs(x))))
        else:
            return 1


def rotation_rib(aoa, arc, zrot):
    """Rotation Matrix for Ribs, aoa, arcwide-angle and glidewise angle in radians"""
    # Rotate Arcangle, rotate from lying to standing (x-z)
    rot = rotation_3d(-arc + math.pi / 2, [-1, 0, 0])
    axis = rot.dot([0, 0, 1])
    rot = rotation_3d(aoa, axis).dot(rot)
    axis = rot.dot([0, 1, 0])
    rot = rotation_3d(zrot, axis).dot(rot)
    #rot = rotation_3d(-math.pi/2, [0, 0, 1]).dot(rot)

    return rot
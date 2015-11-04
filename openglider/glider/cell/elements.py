#! /usr/bin/python2
# -*- coding: utf-8; -*-
#
# (c) 2013 booya (http://booya.at)
#
# This file is part of the OpenGlider project.
#
# OpenGlider is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# OpenGlider is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with OpenGlider.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import division
import copy

from openglider.airfoil import get_x_value
from openglider.plots.projection import flatten_list
from openglider.vector import norm


class DiagonalRib(object):
    def __init__(self, left_front, left_back, right_front, right_back, material_code="", name="unnamed"):
        """
        [left_front, left_back, right_front, right_back]
            -> Cut: (x_value, height)
        """
        # Attributes
        self.left_front = left_front
        self.left_back = left_back
        self.right_front = right_front
        self.right_back = right_back
        self.material_code = material_code
        self.name = name

    def __json__(self):
        return {'left_front': self.left_front,
                'left_back': self.left_back,
                'right_front': self.right_front,
                'right_back': self.right_back,
                "material_code": self.material_code
        }

    def copy(self):
        return copy.copy(self)

    def mirror(self):
        self.left_front, self.right_front = self.right_front, self.left_front
        self.left_back, self.right_back = self.right_back, self.left_back

    def get_3d(self, cell):
        """
        Get 3d-Points of a diagonal rib
        :return: (left_list, right_list)
        """

        def get_list(rib, cut_front, cut_back):
            # Is it at 0 or 1?
            if cut_back[1] == cut_front[1] and cut_front[1] in (-1, 1):
                side = -cut_front[1]  # -1 -> lower, 1->upper
                front = rib.profile_2d(cut_front[0] * side)
                back = rib.profile_2d(cut_back[0] * side)
                return rib.profile_3d[front:back]
            else:

                return [rib.align(rib.profile_2d.align(p) + [0]) for p in (cut_front, cut_back)]

        left = get_list(cell.rib1, self.left_front, self.left_back)
        right = get_list(cell.rib2, self.right_front, self.right_back)

        return left, right

    def get_flattened(self, cell, ribs_flattened=None):
        first, second = self.get_3d(cell)
        left, right = flatten_list(first, second)
        return left, right

    def get_average_x(self):
        """
        return average x value for sorting
        """
        return (self.left_front[0] + self.left_back[0] +
                self.right_back[0] + self.right_front[0]) / 4


class DoubleDiagonalRib():
    pass  # TODO


class TensionStrap(DiagonalRib):
    def __init__(self, left, right, width, material_code=None, name=""):
        width /= 2
        super(TensionStrap, self).__init__((left - width, -1),
                                           (left + width, -1),
                                           (right - width, -1),
                                           (right + width, -1),
                                           material_code,
                                           name)


class TensionStrapSimple():
    def __init__(self, left, right, material_code="", name=""):
        self.left = left
        self.right = right
        self.name = name
        self.material_code = material_code

    def __json__(self):
        return {"left": self.left,
                "right": self.right,
                "material_code": self.material_code}

    def get_length(self, cell):
        rib1 = cell.rib1
        rib2 = cell.rib2
        left = rib1.profile_3d[rib1.profile_2d(self.left)]
        right = rib2.profile_3d[rib2.profile_2d(self.right)]

        return norm(left - right)

    def mirror(self):
        self.left, self.right = self.right, self.left


class Panel(object):
    """
    Glider cell-panel
    :param cut_front {'left': 0.06, 'right': 0.06, 'type': 'orthogonal'}
    """

    def __init__(self, cut_front, cut_back, material_code=None, name="unnamed"):
        self.cut_front = cut_front  # (left, right, style(int))
        self.cut_back = cut_back
        self.material_code = material_code or ""
        self.name = name

    def __json__(self):
        return {'cut_front': self.cut_front,
                'cut_back': self.cut_back,
                "material_code": self.material_code
                }

    def get_3d(self, cell, numribs=0):
        """
        Get 3d-Panel
        :param glider: glider class
        :param numribs: number of miniribs to calculate
        :return: List of rib-pieces (Vectorlist)
        """
        xvalues = cell.rib1.profile_2d.x_values
        ribs = []
        for i in range(numribs + 1):
            y = i / numribs
            x1 = self.cut_front["left"] + y * (self.cut_front["right"] -
                                               self.cut_front["left"])
            front = get_x_value(xvalues, x1)

            x2 = self.cut_back["left"] + y * (self.cut_back["right"] -
                                              self.cut_back["left"])
            back = get_x_value(xvalues, x2)
            ribs.append(cell.midrib(y).get(front, back))
            # todo: return polygon-data
        return ribs

    def mirror(self):
        left, right = self.cut_front["left"], self.cut_front["right"]
        self.cut_front["left"], self.cut_front["right"] = right, left

        left, right = self.cut_back["left"], self.cut_back["right"]
        self.cut_back["left"], self.cut_back["right"] = right, left









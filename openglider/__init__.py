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
__version__ = '0.01dev3'
__author__ = 'Booya'
from openglider.config import config
import numpy


# Monkey-patch numpy cross for pypy
try:
    import __pypy__
    def cross(a,b):
        return numpy.array([a[1]*b[2]-a[2]*b[1],
                            -a[0]*b[2]+a[2]*b[0],
                            a[0]*b[1]-a[1]*b[0]
                            ])
    numpy.cross = cross
except ImportError:
    pass
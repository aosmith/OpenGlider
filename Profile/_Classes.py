import math
import os  # for xfoil execution

import numpy  # array spec
from ._XFoilCalc import XValues, Calcfile, Impresults
from ._Functions import Point
#import _XFoilCalc
import Vector


class BasicProfile2D(object):
    """Basic Profile Class, not to do much, but just """
    ####rootprof gleich mitspeichern!!
    def __init__(self, profile):
        self._SetProfile(profile)

    def __repr__(self):
        return self.data.__str__()

    def copy(self):
        return self.__class__(self.data.copy())

    def __mul__(self, other):
        fakt = numpy.array([1, float(other)])
        return self.__class__(self.Profile * fakt)

    def Point(self, xval, h=-1):
        """Get Profile Point for x-value (<0:upper side) optional: height (-1:lower,1:upper), possibly mapped"""
        if isinstance(xval, (list, tuple, numpy.ndarray)):
            ##if so, treat as a common list instead...
            (i, k) = xval
            return Point(self.data, i, k)
        else:
            return Point(self.data, xval, h)

    def Points(self, xvalues):
        """Map a list of XValues onto the Profile"""
        ####kontrollstruktur einfuegen
        ##xvalues fuer xvalues alle groesser 0 aufloesen
        ####mit point zusammenhaengen
        return numpy.array([self.Point(x) for x in xvalues])

    def Normalize(self):
        p1 = self.data[0]
        dmax = 0.
        nose = 0
        for i in self.data:
            temp = Vector.norm(i - p1)
            if temp > dmax:
                dmax = temp
                nose = i
            #to normalize do: put nose to (0,0), rotate to fit (1,0), normalize to (1,0)
        #use: a.b=|a|*|b|*cos(alpha)->
        diff = p1 - nose
        sin = (diff / dmax).dot([0, -1])  # equal to cross product of (x1,y1,0),(x2,y2,0)
        cos = numpy.sqrt(1 - sin ** 2)
        matrix = numpy.array([[cos, -sin], [sin, cos]]) / dmax
        self.data = numpy.array([matrix.dot(i - nose) for i in self.data])

    def _SetProfile(self, profile):
        ####kontrolle: tiefe, laenge jeweils
        self.data = numpy.array(profile)
        i=0
        while profile[i+1][0] < profile[i][0] and i < len(profile):
            i += 1
        self.noseindex = i

    def _GetProfile(self):
        return self.data

    Profile = property(_GetProfile, _SetProfile)


class Profile2D(BasicProfile2D):
    """Profile2D: 2 Dimensional Standard Profile representative in OpenGlider"""
    #############Initialisation###################
    def __init__(self,
                 profile=[[1.00000000e+00,  -1.77114326e-16],
                          [5.00000000e-01,   1.73720187e-02],
                          [1.33974596e-01,   6.44897990e-02],
                          [0.00000000e+00,   0.00000000e+00],
                          [1.33974596e-01,  -4.74705844e-02],
                          [5.00000000e-01,  -6.58261348e-02],
                          [1.00000000e+00,  -2.63677968e-16]],
                 name="Profile"):
        self.Name = name
        if not profile == []:
            if len(profile) == 0:
                return
            elif isinstance(profile[0][0], str):
                self.Name = profile[0][0]
                i = 1
            else:
                i = 0
            self._rootprof = BasicProfile2D(profile[i:])
            self._rootprof.Normalize()
            BasicProfile2D._SetProfile(self, self._rootprof.Profile)

    def __str__(self):
        return self.Name

    def __add__(self, other):
        if other.__class__ == self.__class__:
            #use the one with more points
            if self.Numpoints > other.Numpoints:
                first = other.copy()
                second = self
            else:
                first = self.copy()
                second = other
            if not numpy.array_equal(first.XValues, second.XValues):
                first.XValues = second.XValues
            first.Profile = first.Profile + second.Profile * numpy.array([0, 1])
            return first

    def __eq__(self, other):
        return numpy.array_equal(self.Profile, other.Profile)

    def Import(self, pfad):
        if os.path.isfile(pfad):
            tempfile = []
            pfile = open(pfad, "r")
            for line in pfile:
                line = line.strip()
                ###tab-seperated values except first line->name
                if "\t" in line:
                    line = line.split("\t")
                else:
                    line = line.split(" ")
                while "" in line:
                    line.remove("")
                if len(line) == 2:
                    line = [float(i) for i in line]
                elif len(line) == 1:
                    self.Name = line
                tempfile += [line]
            self.__init__(tempfile)
            pfile.close()
        else:
            raise Exception("Profile not found in"+pfad+"!")

    def Export(self, pfad):
        """Export Profile in .dat Format"""
        out = open(pfad, "w")
        out.write(self.Name)
        for i in self.Profile:
            out.write("\n" + str(i[0]) + "\t" + str(i[1]))
        return pfad

    def RootPoint(self, xval, h=-1):
        """Get Profile Point for x-value (<0:upper side) optional: height (-1:lower,1:upper);
        use root-profile (highest res)"""
        return self._rootprof.Point(xval, h)

    def Reset(self):
        """Reset Profile To Root-Values"""
        self.Profile = self._rootprof.Profile

    def _GetXValues(self):
        """Get XValues of Profile. upper side neg, lower positive"""
        i = self.noseindex
        return numpy.concatenate((self.data[:i, 0]*-1., self.data[i:, 0]))

    def _SetXValues(self, xval):
        """Set X-Values of profile to defined points."""
        ###standard-value: root-prof xvalues
        self.Profile = self._rootprof.Points(xval)[:, 1]

    def _GetLen(self):
        return len(self.data)

    def _SetLen(self, num):
        """Set Profile to cosinus-Distributed XValues"""
        i = num - num % 2
        xtemp = lambda x: cmp(x, 0.5)*(1-math.sin(math.pi*x))
        self.XValues = [xtemp(j * 1. / i) for j in range(i + 1)]

    def _GetThick(self, *xvals):
        """with no arg the max thick is returned"""
        if not xvals:
            xvals = set(map(abs, self.XValues))
        return numpy.array([[i, self.Point(-i)[1][1]-self.Point(i)[1][1]] for i in xvals])

    def _SetThick(self, newthick):
        factor = float(newthick/max(self.Thickness[:,1]))
        new = self.Profile*[1., factor]
        self.__init__(new, self.Name+ "_" + str(newthick*100)+"%")

    def _getcamber(self, *xvals):
        """return the camber of the profile for certain x-values or if nothing supplied, camber-line"""
        if not xvals:
            xvals = sorted(set(map(abs, self.XValues)))
        return numpy.array([self.Point(i, 0.) for i in xvals])

    def _setcamber(self, newcamber):
        """Set maximal camber to the new value"""
        now = self.Camber
        factor = newcamber/max(now[:,1])-1
        now = dict(now)
        self.__init__([i+[0, now[i[0]]*factor] for i in self.Profile])

    Thickness = property(_GetThick, _SetThick)
    Numpoints = property(_GetLen, _SetLen)
    XValues = property(_GetXValues, _SetXValues)
    Camber = property(_getcamber, _setcamber)

class XFoil(Profile2D):
    """XFoil Calculation Profile based on Profile2D"""

    def __init__(self, profile=""):
        Profile2D.__init__(self, profile)
        self._xvalues = self.XValues
        self._calcvalues = []


    def _Change(self):
        """Check if something changed in coordinates"""
        checkval = self._xvalues == self.XValues
        if not isinstance(checkval, bool):
            checkval = checkval.all()
        return checkval

    def _Calc(self, angles):

        resfile = "/tmp/result.dat"
        pfile = "/tmp/calc_pfile.dat"
        cfile = Calcfile(angles, resfile)

        self.Export(pfile)
        status = os.system("xfoil " + pfile + " <" + cfile + " > /tmp/log.dat")
        if status == 0:
            result = Impresults(resfile)
            for i in result:
                self._calcvalues[i] = result[i]
            os.system("rm " + resfile)
        os.system("rm " + pfile + " " + cfile)

    def _Get(self, angle, exact=1):
        if self._Change():
            self._calcvalues = {}
            self._xvalues = self.XValues[:]
        print(self._calcvalues)
        calcangles = XValues(angle, self._calcvalues)
        print("ho!" + str(calcangles))
        if len(calcangles) > 0:
            erg = self._Calc(calcangles)
            print("soso")
            ##self._calcvalues=[1,2]
        return erg


#debug
#ab=Profile2D()
#ab.Import("/home/simon/Dropbox/para-lorenz/paragleiter/profile/test.dat")
#neu=ab.Point(0.1)
#print(neu)
#print(ab.Point(neu[0]))
#print("schas")
class Profile3D(Vector.List):
    def __init__(self, profile="", name="Profile3d"):
        #Vector.List.__init__(profile)
        self.SetProfile(profile)
        self.Name = name

    def SetProfile(self, profile):
        if not isinstance(profile, str):
            self.data = numpy.array(profile)

    def Flatten(self):
        ##local func:
        ##front vector
        p1 = self.data[0]
        nose = max(self.data, key=lambda x: numpy.linalg.norm(x - p1))
        diff = [nose - i for i in self.data]

        xvekt = Vector.normalize(diff[0])
        yvekt = numpy.array([0, 0, 0])

        for i in diff:
            temp = i - xvekt * xvekt.dot(i)
            yvekt = max([yvekt + temp, yvekt - temp], key=lambda x: numpy.linalg.norm(x))

        yvekt = Vector.normalize(yvekt)

        return Profile2D([[xvekt.dot(i), yvekt.dot(i)] for i in diff], name=self.Name + "flattened")
        ###find x-y projection-layer first


if __name__ == "__main__":
    p1e = Profile2D()
    p1e.Import("/home/simon/test.dat")
    p2 = p1e * 0.2
    print("hoho")

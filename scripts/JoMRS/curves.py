# Copyright (c) 2018 Johannes Wolz

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission
# notice shall be included in all.
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Author:     Johannes Wolz / Rigging TD
# Date:       2019 / 01 / 14

"""
JoMRS nurbsCurve modification module.
"""
##########################################################
# GLOBALS
##########################################################

import pymel.core as pmc
import mayautils as utils
import strings
import logging
import logger

moduleLogger = logging.getLogger(__name__ + '.py')


class ControlCurves(object):
    """
    Create control curve class.
    """

    def create_curve(self, name='M_control_0_CON', match=None, scale=None,
                     colorIndex=17, bufferGRP=True, child=None):
        """
        Create curve method.
        Args:
            name(str): The control name. You should follow the
            JoMRS naming convention. If not it will throw some
            warnings.
            match(dagnode): The node for transform match.
            scale(list): The scale values.
            colorIndex(integer): The color of the control.
            Valid is:
             0:GREY,1:BLACK,2:DARKGREY,3:BRIGHTGREY,4:RED,5:DARKBLUE,
             6:BRIGHTBLUE,7:GREEN,8:DARKLILA,9:MAGENTA,10:BRIGHTBROWN,
             11:BROWN,12:DIRTRED,13:BRIGHTRED,14:BRIGHTGREEN,15:BLUE,
             16:WHITE,17:BRIGHTYELLOW,18:CYAN,19:TURQUOISE,20:LIGHTRED,
             21:LIGHTORANGE,22:LIGHTYELLOW,23:DIRTGREEN,24:LIGHTBROWN,
             25:DIRTYELLOW,26:LIGHTGREEN,27:LIGHTGREEN2,28:LIGHTBLUE
            bufferGRP(bool): Create bufferGRP for the control.
            child(dagnode): The child of the control.
        Return:
                list: The buffer group, the control curve node.
        """
        result = []
        name = strings.string_checkup(name, moduleLogger)
        self.control = self.get_curve(name)
        shapes = self.control.getShapes()
        for shape in shapes:
            pmc.rename(shape, name + 'Shape')
        if scale:
            for shape_ in shapes:
                pmc.scale(shape_.cv[0:], scale[0], scale[1], scale[2])
        if match:
            pmc.delete(pmc.parentConstraint(match, self.control, mo=False))
        if colorIndex:
            for shape__ in shapes:
                shape__.overrideEnabled.set(1)
                shape__.overrideColor.set(colorIndex)
        if bufferGRP:
            buffer_ = utils.create_bufferGRP(node=self.control)
            result.append(buffer_)
        if child:
            self.control.addChild(child)
        result.append(self.control)
        return result

    def get_curve(self):
        raise NotImplemented


class BoxControl(ControlCurves):
    """
    Create box control curve.
    """
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((0.5, 0.5, 0.5),
                                      (0.5, 0.5, -0.5),
                                      (-0.5, 0.5, -0.5),
                                      (-0.5, -0.5, -0.5),
                                      (0.5, -0.5, -0.5),
                                      (0.5, 0.5, -0.5),
                                      (-0.5, 0.5, -0.5),
                                      (-0.5, 0.5, 0.5),
                                      (0.5, 0.5, 0.5),
                                      (0.5, -0.5, 0.5),
                                      (0.5, -0.5, -0.5),
                                      (-0.5, -0.5, -0.5),
                                      (-0.5, -0.5, 0.5),
                                      (0.5, -0.5, 0.5),
                                      (-0.5, -0.5, 0.5),
                                      (-0.5, 0.5, 0.5)),
                         k=(0, 1, 2, 3, 4, 5, 6, 7, 8,
                            9, 10, 11, 12, 13, 14, 15),
                         n=name)


class PyramideControl(ControlCurves):
    """
    Create pyramide control curve.
    """
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((0, 2, 0),
                                      (1, 0, -1),
                                      (-1, 0, -1),
                                      (0, 2, 0),
                                      (-1, 0, 1),
                                      (1, 0, 1),
                                      (0, 2, 0),
                                      (1, 0, -1),
                                      (1, 0, 1),
                                      (-1, 0, 1),
                                      (-1, 0, -1)),
                         k=(0, 1, 2, 3, 4, 5, 6, 7,
                            8, 9, 10),
                         n=name)


class QuaderControl(ControlCurves):
    """
    Create quader control curve.
    """
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((0.5, 3.5, 0.5),
                                      (0.5, 3.5, -0.5),
                                      (-0.5, 3.5, -0.5),
                                      (-0.5, -3.5, -0.5),
                                      (0.5, -3.5, -0.5),
                                      (0.5, 3.5, -0.5),
                                      (-0.5, 3.5, -0.5),
                                      (-0.5, 3.5, 0.5),
                                      (0.5, 3.5, 0.5),
                                      (0.5, -3.5, 0.5),
                                      (0.5, -3.5, -0.5),
                                      (-0.5, -3.5, -0.5),
                                      (-0.5, -3.5, 0.5),
                                      (0.5, -3.5, 0.5),
                                      (-0.5, -3.5, 0.5),
                                      (-0.5, 3.5, 0.5)),
                         k=(0, 1, 2, 3, 4, 5, 6, 7, 8,
                            9, 10, 11, 12, 13, 14, 15),
                         n=name)


class SphereControl(ControlCurves):
    """
    Create sphere control curve.
    """
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((0, 0, 1),
                                      (0, 0.5, 0.866025),
                                      (0, 0.866025, 0.5),
                                      (0, 1, 0),
                                      (0, 0.866025, -0.5),
                                      (0, 0.5, -0.866025),
                                      (0, 0, -1),
                                      (0, -0.5, -0.866025),
                                      (0, -0.866025, -0.5),
                                      (0, -1, 0),
                                      (0, -0.866025, 0.5),
                                      (0, -0.5, 0.866025),
                                      (0, 0, 1),
                                      (0.707107, 0, 0.707107),
                                      (1, 0, 0),
                                      (0.707107, 0, -0.707107),
                                      (0, 0, -1),
                                      (-0.707107, 0, -0.707107),
                                      (-1, 0, 0),
                                      (-0.866025, 0.5, 0),
                                      (-0.5, 0.866025, 0),
                                      (0, 1, 0),
                                      (0.5, 0.866025, 0),
                                      (0.866025, 0.5, 0),
                                      (1, 0, 0),
                                      (0.866025, -0.5, 0),
                                      (0.5, -0.866025, 0),
                                      (0, -1, 0),
                                      (-0.5, -0.866025, 0),
                                      (-0.866025, -0.5, 0),
                                      (-1, 0, 0),
                                      (-0.707107, 0, 0.707107),
                                      (0, 0, 1)),
                         k=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                            12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
                            22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
                            32),
                         n=name)


class SquareControl(ControlCurves):
    """
    Create square control curve.
    """
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((1, 0, -1),
                                      (-1, 0, -1),
                                      (-1, 0, 1),
                                      (1, 0, 1),
                                      (1, 0, -1)),
                         k=(0, 1, 2, 3, 4),
                         n=name)


class CircleControl(ControlCurves):
    """
    Create circle control.
    """
    def get_curve(self, name):
        return pmc.circle(c=(0, 0, 0),
                          nr=(0, 1, 0),
                          sw=360,
                          r=1,
                          d=3,
                          ut=0,
                          tol=0.01,
                          s=8,
                          ch=0,
                          n=name)[0]


class DoubleCircleControl(ControlCurves):
    """
    Create a double circle control.
    """
    def get_curve(self, name):
        circle0 = pmc.circle(c=(0, 0, 0),
                             nr=(0, 1, 0),
                             sw=360,
                             r=1,
                             d=3,
                             ut=0,
                             tol=0.01,
                             s=8,
                             ch=0,
                             n=name)[0]
        circle1 = pmc.circle(c=(0, 0, 0),
                             nr=(0, 1, 0),
                             sw=360,
                             r=1,
                             d=3,
                             ut=0,
                             tol=0.01,
                             s=8,
                             ch=0,
                             n=name)[0]
        for cv in range(8):
            circle1.getShape().controlPoints[cv].yValue.set(0.5)
        pmc.parent(circle1.getShape(), circle0, r=True, shape=True)
        pmc.delete(circle1)
        return circle0


class HexagonControl(ControlCurves):
    """
    Create a Hexagon Control.
    """
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((-0.5, 1, 0.866025),
                                      (0.5, 1, 0.866025),
                                      (0.5, -1, 0.866025),
                                      (1, -1, 0),
                                      (1, 1, 0),
                                      (0.5, 1, -0.866025),
                                      (0.5, -1, -0.866025),
                                      (-0.5, -1, -0.866026),
                                      (-0.5, 1, -0.866026),
                                      (-1, 1, -1.5885e-007),
                                      (-1, -1, -1.5885e-007),
                                      (-0.5, -1, 0.866025),
                                      (-0.5, 1, 0.866025),
                                      (-1, 1, -1.5885e-007),
                                      (-0.5, 1, -0.866026),
                                      (0.5, 1, -0.866025),
                                      (1, 1, 0),
                                      (0.5, 1, 0.866025),
                                      (0.5, -1, 0.866025),
                                      (-0.5, -1, 0.866025),
                                      (-1, -1, -1.5885e-007),
                                      (-0.5, -1, -0.866026),
                                      (0.5, -1, -0.866025),
                                      (1, -1, 0)),
                         k=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                            12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
                            22, 23),
                         n=name)


class SingleArrowControl(ControlCurves):
    """
    Create single arrow curve.
    """
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((0, 0, -1.32),
                                      (-0.99, 0, 0),
                                      (-0.33, 0, 0),
                                      (-0.33, 0, 0.99),
                                      (0.33, 0, 0.99),
                                      (0.33, 0, 0),
                                      (0.99, 0, 0),
                                      (0, 0, -1.32)),
                         k=(0, 1, 2, 3, 4, 5, 6, 7),
                         n=name)


class ArrowsOnBallControl(ControlCurves):
    """
    Create arrows on ball control curve.
    """
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((0, 0.35, -1.001567),
                                      (-0.336638, 0.677886, -0.751175),
                                      (-0.0959835, 0.677886, -0.751175),
                                      (-0.0959835, 0.850458, -0.500783),
                                      (-0.0959835, 0.954001, -0.0987656),
                                      (-0.500783, 0.850458, -0.0987656),
                                      (-0.751175, 0.677886, -0.0987656),
                                      (-0.751175, 0.677886, -0.336638),
                                      (-1.001567, 0.35, 0),
                                      (-0.751175, 0.677886, 0.336638),
                                      (-0.751175, 0.677886, 0.0987656),
                                      (-0.500783, 0.850458, 0.0987656),
                                      (-0.0959835, 0.954001, 0.0987656),
                                      (-0.0959835, 0.850458, 0.500783),
                                      (-0.0959835, 0.677886, 0.751175),
                                      (-0.336638, 0.677886, 0.751175),
                                      (0, 0.35, 1.001567),
                                      (0.336638, 0.677886, 0.751175),
                                      (0.0959835, 0.677886, 0.751175),
                                      (0.0959835, 0.850458, 0.500783),
                                      (0.0959835, 0.954001, 0.0987656),
                                      (0.500783, 0.850458, 0.0987656),
                                      (0.751175, 0.677886, 0.0987656),
                                      (0.751175, 0.677886, 0.336638),
                                      (1.001567, 0.35, 0),
                                      (0.751175, 0.677886, -0.336638),
                                      (0.751175, 0.677886, -0.0987656),
                                      (0.500783, 0.850458, -0.0987656),
                                      (0.0959835, 0.954001, -0.0987656),
                                      (0.0959835, 0.850458, -0.500783),
                                      (0.0959835, 0.677886, -0.751175),
                                      (0.336638, 0.677886, -0.751175),
                                      (0, 0.35, -1.001567)),
                         k=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
                            14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,
                            27, 28, 29, 30, 31, 32),
                         n=name)


class SingleArrowThinControl(ControlCurves):
    """
    Create a Single Arrow Thin Control.
    """
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((0, 0, 1),
                                      (0, 0, -1),
                                      (-1, 0, 0),
                                      (0, 0, -1),
                                      (1, 0, 0)),
                         k=(0, 1, 2, 3, 4),
                         n=name)


class SingleArrowNormalControl(ControlCurves):
    """
    Create a Single Arrow Normal Control.
    """
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((0, 0, -1.32),
                                      (-0.99, 0, 0),
                                      (-0.33, 0, 0),
                                      (-0.33, 0, 0.99),
                                      (0.33, 0, 0.99),
                                      (0.33, 0, 0),
                                      (0.99, 0, 0),
                                      (0, 0, -1.32)),
                         k=(0, 1, 2, 3, 4, 5, 6, 7),
                         n=name)


class SingleArrowFatControl(ControlCurves):
    """
    Create a Single Arrow Fat Control.
    """
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((0, 0, -0.99),
                                      (-0.66, 0, 0),
                                      (-0.33, 0, 0),
                                      (-0.33, 0, 0.66),
                                      (0.33, 0, 0.66),
                                      (0.33, 0, 0),
                                      (0.66, 0, 0),
                                      (0, 0, -0.99)),
                         k=(0, 1, 2, 3, 4, 5, 6, 7),
                         n=name)


class DoubleArrowThinControl(ControlCurves):
    """
    Create a Double Arrow Thin Control.
    """
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((1, 0, 1),
                                      (0, 0, 2),
                                      (-1, 0, 1),
                                      (0, 0, 2),
                                      (0, 0, -2),
                                      (-1, 0, -1),
                                      (0, 0, -2),
                                      (1, 0, -1)),
                         k=(0, 1, 2, 3, 4, 5, 6, 7),
                         n=name)


class DoubleArrowNormalControl(ControlCurves):
    """
    Create double arrow normal curve.
    """
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((0, 0, -2.31),
                                      (-0.99, 0, -0.99),
                                      (-0.33, 0, -0.99),
                                      (-0.33, 0, 0.99),
                                      (-0.99, 0, 0.99),
                                      (0, 0, 2.31),
                                      (0.99, 0, 0.99),
                                      (0.33, 0, 0.99),
                                      (0.33, 0, -0.99),
                                      (0.99, 0, -0.99),
                                      (0, 0, -2.31)),
                         k=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
                         n=name)


class DoubleArrowFatControl(ControlCurves):
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((0, 0, -1.35),
                                      (-0.66, 0, -0.36),
                                      (-0.33, 0, -0.36),
                                      (-0.33, 0, 0.36),
                                      (-0.66, 0, 0.36),
                                      (0, 0, 1.35),
                                      (0.66, 0, 0.36),
                                      (0.33, 0, 0.36),
                                      (0.33, 0, -0.36),
                                      (0.66, 0, -0.36),
                                      (0, 0, -1.35)),
                         k=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
                         n=name)


class FourArrowThinControl(ControlCurves):
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((1.25, 0, -0.5),
                                      (1.75, 0, 0),
                                      (1.25, 0, 0.5),
                                      (1.75, 0, 0),
                                      (-1.75, 0, 0),
                                      (-1.25, 0, -0.5),
                                      (-1.75, 0, 0),
                                      (-1.25, 0, 0.5),
                                      (-1.75, 0, 0),
                                      (0, 0, 0),
                                      (0, 0, 1.75),
                                      (-0.5, 0, 1.25),
                                      (0, 0, 1.75),
                                      (0.5, 0, 1.25),
                                      (0, 0, 1.75),
                                      (0, 0, -1.75),
                                      (0.5, 0, -1.25),
                                      (0, 0, -1.75),
                                      (-0.5, 0, -1.25),
                                      (0, 0, -1.75)),
                         k=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                            11, 12, 13, 14, 15, 16, 17, 18, 19),
                         n=name)


class FourArrowNormalControl(ControlCurves):
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((0, 0, -1.98),
                                      (-0.495, 0, -1.32),
                                      (-0.165, 0, -1.32),
                                      (-0.165, 0, -0.165),
                                      (-1.32, 0, -0.165),
                                      (-1.32, 0, -0.495),
                                      (-1.98, 0, 0),
                                      (-1.32, 0, 0.495),
                                      (-1.32, 0, 0.165),
                                      (-0.165, 0, 0.165),
                                      (-0.165, 0, 1.32),
                                      (-0.495, 0, 1.32),
                                      (0, 0, 1.98),
                                      (0.495, 0, 1.32),
                                      (0.165, 0, 1.32),
                                      (0.165, 0, 0.165),
                                      (1.32, 0, 0.165),
                                      (1.32, 0, 0.495),
                                      (1.98, 0, 0),
                                      (1.32, 0, -0.495),
                                      (1.32, 0, -0.165),
                                      (0.165, 0, -0.165),
                                      (0.165, 0, -1.32),
                                      (0.495, 0, -1.32),
                                      (0, 0, -1.98)),
                         k=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                            11, 12, 13, 14, 15, 16, 17, 18,
                            19, 20, 21, 22, 23, 24),
                         n=name)


class FourArrowFatControl(ControlCurves):
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((0, 0, -1.98),
                                      (-0.495, 0, -1.32),
                                      (-0.165, 0, -1.32),
                                      (-0.165, 0, -0.165),
                                      (-1.32, 0, -0.165),
                                      (-1.32, 0, -0.495),
                                      (-1.98, 0, 0),
                                      (-1.32, 0, 0.495),
                                      (-1.32, 0, 0.165),
                                      (-0.165, 0, 0.165),
                                      (-0.165, 0, 1.32),
                                      (-0.495, 0, 1.32),
                                      (0, 0, 1.98),
                                      (0.495, 0, 1.32),
                                      (0.165, 0, 1.32),
                                      (0.165, 0, 0.165),
                                      (1.32, 0, 0.165),
                                      (1.32, 0, 0.495),
                                      (1.98, 0, 0),
                                      (1.32, 0, -0.495),
                                      (1.32, 0, -0.165),
                                      (0.165, 0, -0.165),
                                      (0.165, 0, -1.32),
                                      (0.495, 0, -1.32),
                                      (0, 0, -1.98)),
                         k=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                            11, 12, 13, 14, 15, 16, 17, 18,
                            19, 20, 21, 22, 23, 24),
                         n=name)


class Rot180ArrowThinControl(ControlCurves):
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((-0.446514, 0, -1.351664),
                                      (0.0107043, 0, -1.001418),
                                      (-0.339542, 0, -0.5442),
                                      (0.0107043, 0, -1.001418),
                                      (-0.13006, 0, -1),
                                      (-0.393028, 0, -0.947932),
                                      (-0.725413, 0, -0.725516),
                                      (-0.947961, 0, -0.392646),
                                      (-1.026019, 0, 0),
                                      (-0.947961, 0, 0.392646),
                                      (-0.725413, 0, 0.725516),
                                      (-0.393028, 0, 0.947932),
                                      (-0.13006, 0, 1),
                                      (0, 0, 1),
                                      (-0.339542, 0, 0.5442),
                                      (0, 0, 1),
                                      (-0.446514, 0, 1.351664)),
                         k=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                            10, 11, 12, 13, 14, 15, 16),
                         n=name)


class Rot180ArrowNormalControl(ControlCurves):
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((-0.251045, 0, -1.015808),
                                      (-0.761834, 0, -0.979696),
                                      (-0.486547, 0, -0.930468),
                                      (-0.570736, 0, -0.886448),
                                      (-0.72786, 0, -0.774834),
                                      (-0.909301, 0, -0.550655),
                                      (-1.023899, 0, -0.285854),
                                      (-1.063053, 0, 9.80765e-009),
                                      (-1.023899, 0, 0.285854),
                                      (-0.909301, 0, 0.550655),
                                      (-0.72786, 0, 0.774834),
                                      (-0.570736, 0, 0.886448),
                                      (-0.486547, 0, 0.930468),
                                      (-0.761834, 0, 0.979696),
                                      (-0.251045, 0, 1.015808),
                                      (-0.498915, 0, 0.567734),
                                      (-0.440202, 0, 0.841857),
                                      (-0.516355, 0, 0.802034),
                                      (-0.658578, 0, 0.701014),
                                      (-0.822676, 0, 0.498232),
                                      (-0.926399, 0, 0.258619),
                                      (-0.961797, 0, 8.87346e-009),
                                      (-0.926399, 0, -0.258619),
                                      (-0.822676, 0, -0.498232),
                                      (-0.658578, 0, -0.701014),
                                      (-0.516355, 0, -0.802034),
                                      (-0.440202, 0, -0.841857),
                                      (-0.498915, 0, -0.567734),
                                      (-0.251045, 0, -1.015808)),
                         k=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
                            14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,
                            25, 26, 27, 28),
                         n=name)


class Rot180ArrowFatControl(ControlCurves):
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((-0.124602, 0, -1.096506),
                                      (-0.975917, 0, -1.036319),
                                      (-0.559059, 0, -0.944259),
                                      (-0.798049, 0, -0.798033),
                                      (-1.042702, 0, -0.431934),
                                      (-1.128672, 0, 0),
                                      (-1.042702, 0, 0.431934),
                                      (-0.798049, 0, 0.798033),
                                      (-0.560906, 0, 0.946236),
                                      (-0.975917, 0, 1.036319),
                                      (-0.124602, 0, 1.096506),
                                      (-0.537718, 0, 0.349716),
                                      (-0.440781, 0, 0.788659),
                                      (-0.652776, 0, 0.652998),
                                      (-0.853221, 0, 0.353358),
                                      (-0.923366, 0, 0),
                                      (-0.853221, 0, -0.353358),
                                      (-0.652776, 0, -0.652998),
                                      (-0.439199, 0, -0.785581),
                                      (-0.537718, 0, -0.349716),
                                      (-0.124602, 0, -1.096506)),
                         k=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                            12, 13, 14, 15, 16, 17, 18, 19, 20),
                         n=name)


class ConeControl(ControlCurves):
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((0.5, -1, 0.866025),
                                      (-0.5, -1, 0.866025),
                                      (0, 1, 0),
                                      (0.5, -1, 0.866025),
                                      (1, -1, 0),
                                      (0, 1, 0),
                                      (0.5, -1, -0.866025),
                                      (1, -1, 0),
                                      (0, 1, 0),
                                      (-0.5, -1, -0.866026),
                                      (0.5, -1, -0.866025),
                                      (0, 1, 0),
                                      (-1, -1, -1.5885e-007),
                                      (-0.5, -1, -0.866026),
                                      (0, 1, 0),
                                      (-0.5, -1, 0.866025),
                                      (-1, -1, -1.5885e-007)),
                         k=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                            11, 12, 13, 14, 15, 16),
                         n=name)


class EightArrowControl(ControlCurves):
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((-1.8975, 0, 0),
                                      (-1.4025, 0, 0.37125),
                                      (-1.4025, 0, 0.12375),
                                      (-0.380966, 0, 0.157801),
                                      (-1.079222, 0, 0.904213),
                                      (-1.254231, 0, 0.729204),
                                      (-1.341735, 0, 1.341735),
                                      (-0.729204, 0, 1.254231),
                                      (-0.904213, 0, 1.079222),
                                      (-0.157801, 0, 0.380966),
                                      (-0.12375, 0, 1.4025),
                                      (-0.37125, 0, 1.4025),
                                      (0, 0, 1.8975),
                                      (0.37125, 0, 1.4025),
                                      (0.12375, 0, 1.4025),
                                      (0.157801, 0, 0.380966),
                                      (0.904213, 0, 1.079222),
                                      (0.729204, 0, 1.254231),
                                      (1.341735, 0, 1.341735),
                                      (1.254231, 0, 0.729204),
                                      (1.079222, 0, 0.904213),
                                      (0.380966, 0, 0.157801),
                                      (1.4025, 0, 0.12375),
                                      (1.4025, 0, 0.37125),
                                      (1.8975, 0, 0),
                                      (1.4025, 0, -0.37125),
                                      (1.4025, 0, -0.12375),
                                      (0.380966, 0, -0.157801),
                                      (1.079222, 0, -0.904213),
                                      (1.254231, 0, -0.729204),
                                      (1.341735, 0, -1.341735),
                                      (0.729204, 0, -1.254231),
                                      (0.904213, 0, -1.079222),
                                      (0.157801, 0, -0.380966),
                                      (0.12375, 0, -1.4025),
                                      (0.37125, 0, -1.4025),
                                      (0, 0, -1.8975),
                                      (-0.37125, 0, -1.4025),
                                      (-0.12375, 0, -1.4025),
                                      (-0.157801, 0, -0.380966),
                                      (-0.904213, 0, -1.079222),
                                      (-0.729204, 0, -1.254231),
                                      (-1.341735, 0, -1.341735),
                                      (-1.254231, 0, -0.729204),
                                      (-1.079222, 0, -0.904213),
                                      (-0.380966, 0, -0.157801),
                                      (-1.4025, 0, -0.12375),
                                      (-1.4025, 0, -0.37125),
                                      (-1.8975, 0, 0)),
                         k=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                            12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
                            22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
                            32, 33, 34, 35, 36, 37, 38, 39, 40, 41,
                            42, 43, 44, 45, 46, 47, 48),
                         n=name)


class SpiralControl(ControlCurves):
    def get_curve(self, name):
        return pmc.curve(degree=3, p=((0.474561, 0, -1.241626),
                                      (0.171579, 0, -1.214307),
                                      (-0.434384, 0, -1.159672),
                                      (-1.124061, 0, -0.419971),
                                      (-1.169741, 0, 0.305922),
                                      (-0.792507, 0, 1.018176),
                                      (-0.0412486, 0, 1.262687),
                                      (0.915809, 0, 1.006098),
                                      (1.258635, 0, 0.364883),
                                      (1.032378, 0, -0.461231),
                                      (0.352527, 0, -0.810017),
                                      (-0.451954, 0, -0.43765),
                                      (-0.634527, 0, 0.208919),
                                      (-0.0751226, 0, 0.696326),
                                      (0.292338, 0, 0.414161),
                                      (0.476068, 0, 0.273078)),
                         k=(0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8,
                            9, 10, 11, 12, 13, 13, 13),
                         n=name)


class CrossControl(ControlCurves):
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((0.4, 0, -0.4),
                                      (0.4, 0, -2),
                                      (-0.4, 0, -2),
                                      (-0.4, 0, -0.4),
                                      (-2, 0, -0.4),
                                      (-2, 0, 0.4),
                                      (-0.4, 0, 0.4),
                                      (-0.4, 0, 2),
                                      (0.4, 0, 2),
                                      (0.4, 0, 0.4),
                                      (2, 0, 0.4),
                                      (2, 0, -0.4),
                                      (0.4, 0, -0.4)),
                         k=(0, 1, 2, 3, 4, 5, 6, 7,
                            8, 9, 10, 11, 12),
                         n=name)


class FatCrossControl(ControlCurves):
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((2, 0, 1),
                                      (2, 0, -1),
                                      (1, 0, -1),
                                      (1, 0, -2),
                                      (-1, 0, -2),
                                      (-1, 0, -1),
                                      (-2, 0, -1),
                                      (-2, 0, 1),
                                      (-1, 0, 1),
                                      (-1, 0, 2),
                                      (1, 0, 2),
                                      (1, 0, 1),
                                      (2, 0, 1)),
                         k=(0, 1, 2, 3, 4, 5, 6, 7,
                            8, 9, 10, 11, 12),
                         n=name)


class SpearControl(ControlCurves):
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((0, 2, 0),
                                      (0, 0, 2),
                                      (0, 0, -2),
                                      (0, 2, 0),
                                      (-2, 0, 0),
                                      (2, 0, 0),
                                      (0, 2, 0)),
                         k=(0, 1, 2, 3, 4, 5, 6),
                         n=name)


class SpearControl1(ControlCurves):
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((0, 2, 0),
                                      (0, 0, 2),
                                      (0, -2, 0),
                                      (0, 0, -2),
                                      (0, 2, 0),
                                      (0, -2, 0),
                                      (0, 0, 0),
                                      (0, 0, 2),
                                      (0, 0, -2),
                                      (2, 0, 0),
                                      (0, 0, 2),
                                      (-2, 0, 0),
                                      (0, 0, -2),
                                      (0, 0, 2),
                                      (0, 0, 0),
                                      (-2, 0, 0),
                                      (2, 0, 0)),
                         k=(0, 1, 2, 3, 4, 5, 6, 7,
                            8, 9, 10, 11, 12, 13,
                            14, 15, 16),
                         n=name)


class TransformControl(ControlCurves):
    def get_curve(self, name):
        circle = pmc.circle(c=(0, 0, 0),
                            nr=(0, 1, 0),
                            sw=360,
                            r=1.5,
                            d=3,
                            ut=0,
                            tol=0.01,
                            s=8,
                            ch=0,
                            n=name)[0]
        arrow0 = pmc.curve(d=1, p=((1.75625, 0, 0.115973),
                                   (1.75625, 0, -0.170979),
                                   (2.114939, 0, -0.170979),
                                   (2.114939, 0, -0.314454),
                                   (2.473628, 0, -0.0275029),
                                   (2.114939, 0, 0.259448),
                                   (2.114939, 0, 0.115973),
                                   (1.75625, 0, 0.115973)),
                           k=(0, 1, 2, 3, 4, 5, 6, 7),
                           n=name)
        arrow1 = pmc.curve(d=1, p=((0.143476, 0, -1.783753),
                                   (0.143476, 0, -2.142442),
                                   (0.286951, 0, -2.142442),
                                   (0, 0, -2.501131),
                                   (-0.286951, 0, -2.142442),
                                   (-0.143476, 0, -2.142442),
                                   (-0.143476, 0, -1.783753),
                                   (0.143476, 0, -1.783753)),
                           k=(0, 1, 2, 3, 4, 5, 6, 7),
                           n=name)
        arrow2 = pmc.curve(d=1, p=((-1.75625, 0, -0.170979),
                                   (-2.114939, 0, -0.170979),
                                   (-2.114939, 0, -0.314454),
                                   (-2.473628, 0, -0.0275029),
                                   (-2.114939, 0, 0.259448),
                                   (-2.114939, 0, 0.115973),
                                   (-1.75625, 0, 0.115973),
                                   (-1.75625, 0, -0.170979)),
                           k=(0, 1, 2, 3, 4, 5, 6, 7),
                           n=name)
        arrow3 = pmc.curve(d=1, p=((-0.143476, 0, 1.728747),
                                   (-0.143476, 0, 2.087436),
                                   (-0.286951, 0, 2.087436),
                                   (0, 0, 2.446125),
                                   (0.286951, 0, 2.087436),
                                   (0.143476, 0, 2.087436),
                                   (0.143476, 0, 1.728747),
                                   (-0.143476, 0, 1.728747)),
                           k=(0, 1, 2, 3, 4, 5, 6, 7),
                           n=name)
        pmc.parent(arrow0.getShape(), circle, r=True, shape=True)
        pmc.parent(arrow1.getShape(), circle, r=True, shape=True)
        pmc.parent(arrow2.getShape(), circle, r=True, shape=True)
        pmc.parent(arrow3.getShape(), circle, r=True, shape=True)
        pmc.delete(arrow0, arrow1, arrow2, arrow3)
        return circle


class FootPrintControl(ControlCurves):
    def get_curve(self, name):
        return pmc.curve(d=1, p=((-0.081122, 0, -1.11758),
                                 (0.390719, 0, -0.921584),
                                 (0.514124, 0, -0.616704),
                                 (0.412496, 0, 0.0293557),
                                 (0.86256, 0, 0.552008),
                                 (0.920632, 0, 1.161772),
                                 (0.775452, 0, 1.669908),
                                 (0.38346, 0, 2.011088),
                                 (-0.131936, 0, 2.330484),
                                 (-0.552964, 0, 2.308708),
                                 (-0.654588, 0, 1.691688),
                                 (-0.57474, 0, 0.63912),
                                 (-0.364226, 0, 0.109206),
                                 (-0.531184, 0, -0.39893),
                                 (-0.465852, 0, -0.841736),
                                 (-0.081122, 0, -1.11758)),
                         k=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                            10, 11, 12, 13, 14, 15),
                         n=name)


class CurvedCircleControl(ControlCurves):
    def get_curve(self, name):
        values = [{'cv': 0, 'value': [0.466, -0.235, -0.784]},
                  {'cv': 1, 'value': [0, 0.235, -1.108]},
                  {'cv': 2, 'value': [-0.466, -0.235, -0.784]},
                  {'cv': 3, 'value': [-1.108, 0.109, 0]},
                  {'cv': 4, 'value': [-0.466, -0.235, 0.784]},
                  {'cv': 5, 'value': [0, 0.235, 1.108]},
                  {'cv': 6, 'value': [0.466, -0.235, 0.784]},
                  {'cv': 7, 'value': [1.108, 0.109, 0]}]
        circle = pmc.circle(c=(0, 0, 0),
                            nr=(0, 1, 0),
                            sw=360,
                            r=1,
                            d=3,
                            ut=0,
                            tol=0.01,
                            s=8,
                            ch=0,
                            n=name)[0]
        for v in values:
            circle.getShape().controlPoints[v['cv']].xValue.set(v['value'][0])
            circle.getShape().controlPoints[v['cv']].yValue.set(v['value'][1])
            circle.getShape().controlPoints[v['cv']].zValue.set(v['value'][2])
        return circle


class DoubleCurvedCircleControl(ControlCurves):
    def get_curve(self, name):
        values0 = [{'cv': 0, 'value': [0.466, -0.235, -0.784]},
                   {'cv': 1, 'value': [0, 0.235, -1.108]},
                   {'cv': 2, 'value': [-0.466, -0.235, -0.784]},
                   {'cv': 3, 'value': [-1.108, 0.109, 0]},
                   {'cv': 4, 'value': [-0.466, -0.235, 0.784]},
                   {'cv': 5, 'value': [0, 0.235, 1.108]},
                   {'cv': 6, 'value': [0.466, -0.235, 0.784]},
                   {'cv': 7, 'value': [1.108, 0.109, 0]}]
        values1 = [{'cv': 0, 'value': [0.466, -0.176, -0.784]},
                   {'cv': 1, 'value': [0, 0.294, -1.108]},
                   {'cv': 2, 'value': [-0.466, -0.176, -0.784]},
                   {'cv': 3, 'value': [-1.108, 0.168, 0]},
                   {'cv': 4, 'value': [-0.466, -0.176, 0.784]},
                   {'cv': 5, 'value': [0, 0.294, 1.108]},
                   {'cv': 6, 'value': [0.466, -0.176, 0.784]},
                   {'cv': 7, 'value': [1.108, 0.168, 0]}]
        circle0 = pmc.circle(c=(0, 0, 0),
                             nr=(0, 1, 0),
                             sw=360,
                             r=1,
                             d=3,
                             ut=0,
                             tol=0.01,
                             s=8,
                             ch=0,
                             n=name)[0]
        circle1 = pmc.circle(c=(0, 0, 0),
                             nr=(0, 1, 0),
                             sw=360,
                             r=1,
                             d=3,
                             ut=0,
                             tol=0.01,
                             s=8,
                             ch=0,
                             n=name)[0]
        for v in values0:
            circle0.getShape().controlPoints[v['cv']].xValue.set(v['value'][0])
            circle0.getShape().controlPoints[v['cv']].yValue.set(v['value'][1])
            circle0.getShape().controlPoints[v['cv']].zValue.set(v['value'][2])
        for v in values1:
            circle1.getShape().controlPoints[v['cv']].xValue.set(v['value'][0])
            circle1.getShape().controlPoints[v['cv']].yValue.set(v['value'][1])
            circle1.getShape().controlPoints[v['cv']].zValue.set(v['value'][2])
        pmc.parent(circle1.getShape(), circle0, r=True, shape=True)
        pmc.delete(circle1)
        return circle0


class LocatorControl(ControlCurves):
    def get_curve(self, name):
        line0 = pmc.curve(d=1, p=((5, 0, 0), (-5, 0, 0)), k=(0, 1), n=name)
        line1 = pmc.curve(d=1, p=((0, 5, 0), (0, -5, 0)), k=(0, 1), n=name)
        line2 = pmc.curve(d=1, p=((0, 0, 5), (0, 0, -5)), k=(0, 1), n=name)
        pmc.parent(line1.getShape(), line0, r=True, shape=True)
        pmc.parent(line2.getShape(), line0, r=True, shape=True)
        pmc.delete(line1, line2)
        return line0


class JointControl(ControlCurves):
    def get_curve(self, name):
        locator = LocatorControl().get_curve(name)
        sphere = SphereControl().get_curve(name)
        for shape in sphere.getShapes():
            pmc.scale(shape.cv[0:], 3, 3, 3)
            pmc.parent(shape, locator, r=True, shape=True)
            pmc.delete(sphere)
        return locator


class RotateAxesControl():
    def create_curve(self, name='M_control_0_CON', scale=None):
        arrowValue0 = [{'cv':0, 'value':[0 ,0 ,0]},
                       {'cv':1, 'value':[3.804 ,0 ,0]},
                       {'cv':2, 'value':[2.282 ,-0.761 ,0]},
                       {'cv':3, 'value':[3.804 ,0 ,0]},
                       {'cv':4, 'value':[2.282 ,0.761 ,0]}]
        # pyramide = PyramideControl().create_curve(name=name, scale=scale)
        arrow0 = SingleArrowThinControl().create_curve(name=name, scale=scale)
        arrow1 = SingleArrowThinControl().create_curve(name=name, scale=scale)
        arrow2 = SingleArrowThinControl().create_curve(name=name, scale=scale)
        for v in arrowValue0:
            arrow0.getShape().cv[v['cv']].xValue.set(v['value'][0])
            arrow0.getShape().cv[v['cv']].yValue.set(v['value'][1])
            arrow0.getShape().cv[v['cv']].zValue.set(v['value'][2])
















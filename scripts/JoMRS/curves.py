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
# Date:       2019 / 01 / 03

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

    def create_curve(self, name, match=None, scale=None, colorIndex=17,
                     bufferGRP=True, child=None):
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
        if scale:
            for shape in shapes:
                pmc.scale(shape.cv[0:], scale[0], scale[1], scale[2])
        if match:
            pmc.delete(pmc.parentConstraint(match, self.control, mo=False))
        if colorIndex:
            for shape in shapes:
                shape.overrideEnabled.set(1)
                shape.overrideColor.set(colorIndex)
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


class FatCrossControl(ControlCurves):
    """
    Create fat cross control curve.
    """
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((2, 0, 1,),
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
                         k=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12),
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


class FourArrowNormalControl(ControlCurves):
    """
    Create four arrow normal curve.
    """
    def get_curve(self, name):
        return pmc.curve(degree=1, p=((0, 0, -1.1025),
                                      (-0.33, 0, -0.6075),
                                      (-0.165, 0, -0.6075),
                                      (-0.165, 0, -0.165),
                                      (-0.6075, 0, -0.165),
                                      (-0.6075, 0, -0.33),
                                      (-1.1025, 0, 0),
                                      (-0.6075, 0, 0.33),
                                      (-0.6075, 0, 0.165),
                                      (-0.165, 0, 0.165),
                                      (-0.165, 0, 0.6075),
                                      (-0.33, 0, 0.6075),
                                      (0, 0, 1.1025),
                                      (0.33, 0, 0.6075),
                                      (0.165, 0, 0.6075),
                                      (0.165, 0, 0.165),
                                      (0.6075, 0, 0.165),
                                      (0.6075, 0, 0.33),
                                      (1.1025, 0, 0),
                                      (0.6075, 0, -0.33),
                                      (0.6075, 0, -0.165),
                                      (0.165, 0, -0.165),
                                      (0.165, 0, -0.6075),
                                      (0.33, 0, -0.6075),
                                      (0, 0, -1.1025)),
                         k=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                            11, 12, 13, 14, 15, 16, 17, 18, 19,
                            20, 21, 22, 23, 24),
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


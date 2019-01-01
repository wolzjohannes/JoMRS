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
# Date:       2019 / 01 / 01

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


class controls(object):

    def box(self, name, match=None, scale=None, colorIndex=17,
            bufferGRP=True, child=None):
        """
        Create box control curve. By default with a colorIndex
        of 17(BRIGHTYELLOW).
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
            bufferGRP(bool): Enable bufferGRP for the control.
            child(dagnode): The child of the control.
        Return:
                list: The buffer group, the control curve node.
        """
        result = []
        name = strings.string_checkup(name, moduleLogger)
        self.control = pmc.curve(degree=1, p=((0.5, 0.5, 0.5),
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
        if scale:
            pmc.scale(self.control.cv[0:], scale[0], scale[1], scale[2])
        if match:
            pmc.delete(pmc.parentConstraint(match, self.control, mo=False))
        if colorIndex:
            self.control.getShape().overrideEnabled.set(1)
            self.control.getShape().overrideColor.set(colorIndex)
        if bufferGRP:
            buffer_ = utils.create_bufferGRP(node=self.control)
            result.append(buffer_)
        if child:
            self.control.addChild(child)
        result.append(self.control)
        return result

    def pyramide(self, name, match=None, scale=None, colorIndex=17,
                 bufferGRP=True, child=None):
        """
        Create pyramide control curve. By default with a colorIndex
        of 17(BRIGHTYELLOW).
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
            bufferGRP(bool): Enable bufferGRP for the control.
            child(dagnode): The child of the control.
        Return:
                list: The buffer group, the control curve node.
        """
        result = []
        name = strings.string_checkup(name, moduleLogger)
        self.control = pmc.curve(degree=1, p=((0, 2, 0),
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
        if scale:
            pmc.scale(self.control.cv[0:], scale[0], scale[1], scale[2])
        if match:
            pmc.delete(pmc.parentConstraint(match, self.control, mo=False))
        if colorIndex:
            self.control.getShape().overrideEnabled.set(1)
            self.control.getShape().overrideColor.set(colorIndex)
        if bufferGRP:
            buffer_ = utils.create_bufferGRP(node=self.control)
            result.append(buffer_)
        if child:
            self.control.addChild(child)
        result.append(self.control)
        return result

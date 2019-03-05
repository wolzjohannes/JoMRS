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
# Date:       2019 / 03 / 03

"""
JoMRS main guide module.
"""

import pymel.core as pmc
import mayautils as utils
import strings
import logging
import logger
import attributes
import curves
reload(attributes)

##########################################################
# GLOBALS
##########################################################

moduleLogger = logging.getLogger(__name__ + '.py')
OPROOTNAME = 'M_MAIN_operators_0_GRP'
MAINOPROOTNODENAME = 'M_control_0_CON'

##########################################################
# CLASSES
##########################################################


class OperatorsRootNode(object):

    def __init__(self):
        self.attributesList = []
        self.mainop = {'name': 'root_operator', 'attrType': 'bool',
                       'keyable': False, 'defaultValue': 1}
        self.rigname = {'name': 'rig_name', 'attrType': 'string',
                        'keyable': False}
        self.l_ik_rig_color = {'name': 'l_ik_rig_color', 'attrType': 'long',
                               'keyable': False, 'defaultValue': 13,
                               'minValue': 0, 'maxValue': 31}

        self.l_ik_rig_sub_color = {'name': 'l_ik_rig_sub_color',
                                   'attrType': 'long',
                                   'keyable': False, 'defaultValue': 18,
                                   'minValue': 0, 'maxValue': 31}
        self.r_ik_rig_color = {'name': 'r_ik_rig_color',
                               'attrType': 'long',
                               'keyable': False, 'defaultValue': 6,
                               'minValue': 0, 'maxValue': 31}
        self.r_ik_rig_sub_color = {'name': 'r_ik_rig_sub_color',
                                   'attrType': 'long',
                                   'keyable': False, 'defaultValue': 9,
                                   'minValue': 0, 'maxValue': 31}
        self.m_ik_rig_color = {'name': 'm_ik_rig_color',
                               'attrType': 'long',
                               'keyable': False, 'defaultValue': 17,
                               'minValue': 0, 'maxValue': 31}
        self.m_ik_rig_sub_color = {'name': 'm_ik_rig_sub_color',
                                   'attrType': 'long',
                                   'keyable': False, 'defaultValue': 11,
                                   'minValue': 0, 'maxValue': 31}
        self.attributesList.append(self.mainop)
        self.attributesList.append(self.rigname)
        self.attributesList.append(self.l_ik_rig_color)
        self.attributesList.append(self.l_ik_rig_sub_color)
        self.attributesList.append(self.r_ik_rig_color)
        self.attributesList.append(self.r_ik_rig_sub_color)
        self.attributesList.append(self.m_ik_rig_color)
        self.attributesList.append(self.m_ik_rig_sub_color)

    def createNode(self):
        self.rootNode = pmc.createNode('transform', n=OPROOTNAME)
        attributes.lockAndHideAttributes(node=self.rootNode)
        for attr_ in self.attributesList:
            attributes.addAttr(node=self.rootNode, **attr_)


class mainOperatorNode(OperatorsRootNode):

    def __init__(self):
        super(mainOperatorNode, self).__init__()
        self.opRootND = self.createNode()
        self.attributesList = []
        self.mainop = {'name': 'main_operator', 'attrType': 'bool',
                       'keyable': False, 'defaultValue': 1}
        self.compName = {'name': 'component_name', 'attrType': 'string',
                         'keyable': False, 'channelBox': False}
        self.attributesList.append(self.mainop)
        self.attributesList.append(self.compName)

    def createNode(self, colorIndex=9, name=MAINOPROOTNODENAME):
        self.mainOpND = curves.DiamondControl.createCurve(colorIndex=colorIndex,
                                                          name=name)
        for attr_ in self.attributesList:
            attributes.addAttr(node=self.mainOpND, **attr_)
        self.opRootND.addChild(self.mainOpND)

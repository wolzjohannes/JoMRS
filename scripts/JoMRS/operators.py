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
# Date:       2019 / 03 / 05

"""
JoMRS main operator module. Handles the compon
"""

import pymel.core as pmc
import mayautils as utils
import strings
import logging
import logger
import attributes
import curves
reload(attributes)
reload(curves)

##########################################################
# GLOBALS
##########################################################

moduleLogger = logging.getLogger(__name__ + '.py')
OPROOTNAME = 'M_MAIN_operators_0_GRP'
MAINOPROOTNODENAME = 'M_MAIN_op_0_CON'
SUBOPROOTNODENAME = 'M_SUB_op_0_CON'
DEFAULTCOMPNAME = 'component'
DEFAULTSIDE = 'M'
DEFAULTINDEX = 0
DEFAULTSUBOPERATORSCOUNT = 1

##########################################################
# CLASSES
##########################################################


class OperatorsRootNode(object):

    def __init__(self):
        self.attributesList = []
        self.mainop_attr = {'name': 'JOMRS_op_root', 'attrType': 'bool',
                            'keyable': False, 'defaultValue': 1}

        self.rigname_attr = {'name': 'rig_name', 'attrType': 'string',
                             'keyable': False}

        self.l_ik_rig_color_attr = {'name': 'l_ik_rig_color',
                                    'attrType': 'long',
                                    'keyable': False, 'defaultValue': 13,
                                    'minValue': 0, 'maxValue': 31}

        self.l_ik_rig_sub_color_attr = {'name': 'l_ik_rig_sub_color',
                                        'attrType': 'long',
                                        'keyable': False, 'defaultValue': 18,
                                        'minValue': 0, 'maxValue': 31}

        self.r_ik_rig_color_attr = {'name': 'r_ik_rig_color',
                                    'attrType': 'long',
                                    'keyable': False, 'defaultValue': 6,
                                    'minValue': 0, 'maxValue': 31}

        self.r_ik_rig_sub_color_attr = {'name': 'r_ik_rig_sub_color',
                                        'attrType': 'long',
                                        'keyable': False, 'defaultValue': 9,
                                        'minValue': 0, 'maxValue': 31}

        self.m_ik_rig_color_attr = {'name': 'm_ik_rig_color',
                                    'attrType': 'long',
                                    'keyable': False, 'defaultValue': 17,
                                    'minValue': 0, 'maxValue': 31}

        self.m_ik_rig_sub_color_attr = {'name': 'm_ik_rig_sub_color',
                                        'attrType': 'long',
                                        'keyable': False, 'defaultValue': 11,
                                        'minValue': 0, 'maxValue': 31}

        self.attributesList.append(self.mainop_attr)
        self.attributesList.append(self.rigname_attr)
        self.attributesList.append(self.l_ik_rig_color_attr)
        self.attributesList.append(self.l_ik_rig_sub_color_attr)
        self.attributesList.append(self.r_ik_rig_color_attr)
        self.attributesList.append(self.r_ik_rig_sub_color_attr)
        self.attributesList.append(self.m_ik_rig_color_attr)
        self.attributesList.append(self.m_ik_rig_sub_color_attr)

    def create_node(self):
        self.rootNode = pmc.createNode('transform', n=OPROOTNAME)
        attributes.lockAndHideAttributes(node=self.rootNode)
        for attr_ in self.attributesList:
            attributes.addAttr(node=self.rootNode, **attr_)
        return self.rootNode


class mainOperatorNode(OperatorsRootNode):
    def __init__(self):
        super(mainOperatorNode, self).__init__()
        self.mainOP = self
        self.attributesList = []

        self.mainop_attr = {'name': 'JOMRS_op_main', 'attrType': 'bool',
                            'keyable': False, 'defaultValue': 1}

        self.compName_attr = {'name': 'component_name', 'attrType': 'string',
                              'keyable': False, 'channelBox': False}

        self.compType_attr = {'name': 'component_type', 'attrType': 'string',
                              'keyable': False, 'channelBox': False}

        self.compSide_attr = {'name': 'component_side', 'attrType': 'string',
                              'keyable': False, 'channelBox': False}

        self.compIndex_attr = {'name': 'component_index', 'attrType': 'long',
                               'keyable': False, 'channelBox': False,
                               'defaultValue': 0}

        temp = [self.mainop_attr, self.compName_attr, self.compType_attr,
                self.compSide_attr, self.compIndex_attr]
        for attr_ in temp:
            self.attributesList.append(attr_)

    def createNode(self, colorIndex=18, name=MAINOPROOTNODENAME,
                   defaultSide=DEFAULTSIDE, defaultIndex=DEFAULTINDEX):
        self.opRootND = self.mainOP.create_node()
        self.mainOpCurve = curves.DiamondControl()
        self.mainOpND = self.mainOpCurve.create_curve(colorIndex=colorIndex,
                                                      name=name)
        for attr_ in self.attributesList:
            attributes.addAttr(node=self.mainOpND[-1], **attr_)
        self.opRootND.addChild(self.mainOpND[0])
        self.mainOpND[1].component_side.set(defaultSide)
        self.mainOpND[1].component_index.set(defaultIndex)
        return self.mainOpND


class create_component_operator(mainOperatorNode):
    def __init__(self, subOperatorsCount=DEFAULTSUBOPERATORSCOUNT,
                 componentName=DEFAULTCOMPNAME, defaultSide=DEFAULTSIDE,
                 mainOperatorNodeName=MAINOPROOTNODENAME,
                 supOperatorNodeName=SUBOPROOTNODENAME):
        super(create_component_operator, self).__init__()
        self.jointControl = curves.JointControl()
        self.result = []
        self.mainOperatorNodeName = mainOperatorNodeName.replace('M_',
                                                                 defaultSide +
                                                                 '_')
        self.mainOperatorNodeName = self.mainOperatorNodeName.replace('_op_',
                                                                      '_op_' +
                                                                      componentName +
                                                                      '_')
        self.mainOperatorNode = self
        self.mainOperatorNode = self.createNode(defaultSide=defaultSide,
                                                name=self.mainOperatorNodeName)
        self.result.append(self.mainOperatorNode)
        for sub in range(subOperatorsCount):
            instance = '_op_{}_{}'.format(componentName, str(sub))
            self.subOperatorNodeName = supOperatorNodeName.replace('M_',
                                                                   defaultSide +
                                                                   '_')
            self.subOperatorNodeName = self.subOperatorNodeName.replace('_op_0',
                                                                        instance)
            subOpNode = self.jointControl.create_curve(name=self.subOperatorNodeName)








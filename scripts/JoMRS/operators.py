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
OPROOTTAGNAME = 'JOMRS_op_root'
OPMAINTAGNAME = 'JOMRS_op_main'
OPSUBTAGNAME = 'JOMRS_op_sub'
OPROOTNAME = 'M_MAIN_operators_0_GRP'
MAINOPROOTNODENAME = 'M_MAIN_op_0_CON'
SUBOPROOTNODENAME = 'M_SUB_op_0_CON'
LINEARCURVENAME = 'M_linear_op_0_CRV'
DEFAULTCOMPNAME = 'component'
DEFAULTSIDE = 'M'
DEFAULTINDEX = 0
DEFAULTSUBOPERATORSCOUNT = 1
DEFAULTAXES = 'X'
DEFAULTSPACING = 10
DEFAULTSUBOPERATORSSCALE = [0.25, 0.25, 0.25]
ERRORMESSAGE = {'selection': 'More then one parent not allowed',
                'selection1': 'Parent of main operator is no JoMRS'
                ' operator node or operators root node'}

##########################################################
# CLASSES
##########################################################


class OperatorsRootNode(object):

    def __init__(self, opRootTagName=OPROOTTAGNAME):
        self.param_list = []
        self.mainop_attr = {'name': opRootTagName, 'attrType': 'bool',
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

        self.param_list.append(self.mainop_attr)
        self.param_list.append(self.rigname_attr)
        self.param_list.append(self.l_ik_rig_color_attr)
        self.param_list.append(self.l_ik_rig_sub_color_attr)
        self.param_list.append(self.r_ik_rig_color_attr)
        self.param_list.append(self.r_ik_rig_sub_color_attr)
        self.param_list.append(self.m_ik_rig_color_attr)
        self.param_list.append(self.m_ik_rig_sub_color_attr)

    def create_node(self, opRootName=OPROOTNAME):
        self.rootNode = pmc.createNode('transform', n=opRootName)
        attributes.lockAndHideAttributes(node=self.rootNode)
        for attr_ in self.param_list:
            attributes.addAttr(node=self.rootNode, **attr_)
        return self.rootNode


class mainOperatorNode(OperatorsRootNode):
    def __init__(self, opMainTagName=OPMAINTAGNAME,
                 opRootTagName=OPROOTTAGNAME,
                 errorMessage=ERRORMESSAGE['selection1']):
        super(mainOperatorNode, self).__init__()

        self.selection = pmc.ls(sl=True, typ='transform')

        for node in self.selection:
            if node.hasAttr(opRootTagName) or node.hasAttr(opMainTagName):
                continue
            else:
                logger.log(level='error', message=errorMessage,
                           logger=moduleLogger)

        self.attribute_list = []

        self.mainop_attr = {'name': opMainTagName, 'attrType': 'bool',
                            'keyable': False, 'defaultValue': 1}

        self.compName_attr = {'name': 'component_name',
                              'attrType': 'string', 'keyable': False,
                              'channelBox': False}

        self.compType_attr = {'name': 'component_type',
                              'attrType': 'string', 'keyable': False,
                              'channelBox': False}

        self.compSide_attr = {'name': 'component_side',
                              'attrType': 'string', 'keyable': False,
                              'channelBox': False}

        self.compIndex_attr = {'name': 'component_index',
                               'attrType': 'long', 'keyable': False,
                               'channelBox': False, 'defaultValue': 0}

        temp = [self.mainop_attr, self.compName_attr, self.compType_attr,
                self.compSide_attr, self.compIndex_attr]
        for attr_ in temp:
            self.attribute_list.append(attr_)

    def createNode(self, colorIndex=18, name=MAINOPROOTNODENAME,
                   side=DEFAULTSIDE, index=DEFAULTINDEX,
                   errorMessage=ERRORMESSAGE):
        if not self.selection:
            self.opRootND = self.create_node()
        else:
            self.opRootND = self.selection[0]
        self.mainOpCurve = curves.DiamondControl()
        self.mainOpND = self.mainOpCurve.create_curve(colorIndex=colorIndex,
                                                      name=name,
                                                      match=self.opRootND)
        for attr_ in self.attribute_list:
            attributes.addAttr(node=self.mainOpND[-1], **attr_)
        self.opRootND.addChild(self.mainOpND[0])
        self.mainOpND[1].component_side.set(side)
        self.mainOpND[1].component_index.set(index)
        return self.mainOpND


class create_component_operator(mainOperatorNode):
    def __init__(self, subOperatorsCount=DEFAULTSUBOPERATORSCOUNT,
                 componentName=DEFAULTCOMPNAME, side=DEFAULTSIDE,
                 mainOperatorNodeName=MAINOPROOTNODENAME,
                 subOperatorsNodeName=SUBOPROOTNODENAME,
                 axes=DEFAULTAXES, spaceing=DEFAULTSPACING,
                 subOperatorsScale=DEFAULTSUBOPERATORSSCALE,
                 linearCurveName=LINEARCURVENAME,
                 subTagName=SUBOPROOTNODENAME):
        super(create_component_operator, self).__init__()
        self.result = []
        self.jointControl = curves.JointControl()
        self.mainOperatorNodeName = mainOperatorNodeName.replace('M_',
                                                                 side +
                                                                 '_')
        self.mainOperatorNodeName = self.mainOperatorNodeName.replace('_op_',
                                                                      '_op_' +
                                                                      componentName +
                                                                      '_')
        self.mainOperatorNode = self
        self.mainOperatorNode = self.createNode(side=side,
                                                name=self.mainOperatorNodeName)
        self.result.append(self.mainOperatorNode[1])
        for sub in range(subOperatorsCount):
            instance = '_op_{}_{}'.format(componentName, str(sub))
            self.subOperatorNodeName = subOperatorsNodeName.replace('M_',
                                                                   side +
                                                                   '_')
            self.subOperatorNodeName = self.subOperatorNodeName.replace('_op_0',
                                                                        instance)
            subOpNode = self.jointControl.create_curve(name=self.subOperatorNodeName,
                                                       match=self.result[-1],
                                                       scale=subOperatorsScale,
                                                       bufferGRP=False,
                                                       colorIndex=21)
            self.result[-1].addChild(subOpNode[0])
            attributes.addAttr(node=subOpNode[0], name=subTagName,
                               attrType='bool',
                               value=1, defaultValue=1)
            if axes == '-X' or axes == '-Y' or axes == '-Z':
                spaceing = spaceing * -1
            if axes == '-X':
                axes = 'X'
            elif axes == '-Y':
                axes = 'Y'
            elif axes == '-Z':
                axes = 'Z'
            subOpNode[0].attr('translate' + axes).set(spaceing)
            self.result.append(subOpNode[-1])
        self.linearCurveName = linearCurveName.replace('M_',
                                                       side +
                                                       '_')
        self.linearCurveName = self.linearCurveName.replace('_op_',
                                                            '_op_' +
                                                            componentName +
                                                            '_')
        linear_curve = curves.linear_curve(driverNodes=self.result,
                                           name=self.linearCurveName)
        linear_curve.inheritsTransform.set(0)
        self.mainOperatorNode[0].addChild(linear_curve)

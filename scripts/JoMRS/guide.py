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
OPROOTNAME='M_RIG_operators_0_GRP'

##########################################################
# CLASSES
##########################################################


class OperatorsRootNode(object):

    def __init__(self):
        self.attributesList = []
        self.mainop = {'name': 'main_operator', 'attrType': 'bool',
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
# class MainGuide(object):

#     def __init__(self):

#         self.attributesList = []

#         def addAttributesToMainGuide(self, node):

#             for attr_ in self.attributesList:
#                 if attr_['attrType'] == 'enum':
#                     logger.log(level='error',
#                                message='Enum attribute not allowed',
#                                logger=moduleLogger)
#                 elif attr_['attrType'] == 'float3':
#                     logger.log(level='error',
#                                message='ArrayAttribute not allowed',
#                                logger=moduleLogger)
#                 else:
#                     attributes.addAttr(node=node, attrType=attr_['attrType'],
#                                        value=attr_['value'],
#                                        defaultValue=attr_['defaultValue'],
#                                        minValue=attr_['minValue'],
#                                        maxValue=attr_['maxValue'],
#                                        keyable=attr_['keyable'],
#                                        hidden=True, channelBox=False)

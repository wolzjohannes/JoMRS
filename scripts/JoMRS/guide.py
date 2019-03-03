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
        self.mainop = {'name': 'mainoperator', 'attrType': 'bool',
                       'keyable': False, 'defaultValue': 1}
        self.attributesList.append(self.mainop)

    def createNode(self):
        try:
            self.rootNode = pmc.PyNode(OPROOTNAME)
        else:
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

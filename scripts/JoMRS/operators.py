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
# Date:       2019 / 05 / 26

"""
JoMRS main operator module. Handles the compon
"""

import pymel.core as pmc
import strings
import logging
import logger
import attributes
import curves
import mayautils

reload(attributes)
reload(curves)

##########################################################
# GLOBALS
##########################################################

moduleLogger = logging.getLogger(__name__ + ".py")
OPROOTTAGNAME = "JOMRS_op_root"
OPMAINTAGNAME = "JOMRS_op_main"
OPSUBTAGNAME = "JOMRS_op_sub"
OPROOTNAME = "M_MAIN_operators_0_GRP"
MAINOPROOTNODENAME = "M_MAIN_op_0_CON"
MAINMETANODENAME = "M_MAIN_op_0_METAND"
SUBOPROOTNODENAME = "M_SUB_op_0_CON"
SUBMETANODENAME = "SUB_op_0_METAND"
MAINMETANODEATTRNAME = "main_node"
SUBMETANODEATTRNAME = "sub_node"
LINEARCURVENAME = "M_linear_op_0_CRV"
DEFAULTCOMPNAME = "component"
DEFAULTSIDE = "M"
DEFAULTINDEX = 0
DEFAULTSUBOPERATORSCOUNT = 1
DEFAULTAXES = "X"
DEFAULTSPACING = 10
DEFAULTSUBOPERATORSSCALE = [0.25, 0.25, 0.25]
ERRORMESSAGE = {
    "selection": "More then one parent not allowed",
    "selection1": "Parent of main operator is no JoMRS"
    " operator main/sub node or operators root node",
}

##########################################################
# CLASSES
# To Do:
# - change use of lists.
# - code optimization
# - give methods. for example: give all sub nodes or
#   all main nodes. Give all attributes.
# - docstrinngs
# - increase performance
##########################################################


class OperatorsRootNode(object):
    def __init__(self, opRootTagName=OPROOTTAGNAME):

        self.mainop_attr = {
            "name": opRootTagName,
            "attrType": "bool",
            "keyable": False,
            "defaultValue": 1,
        }

        self.rigname_attr = {
            "name": "rig_name",
            "attrType": "string",
            "keyable": False,
        }

        self.l_ik_rig_color_attr = {
            "name": "l_ik_rig_color",
            "attrType": "long",
            "keyable": False,
            "defaultValue": 13,
            "minValue": 0,
            "maxValue": 31,
        }

        self.l_ik_rig_sub_color_attr = {
            "name": "l_ik_rig_sub_color",
            "attrType": "long",
            "keyable": False,
            "defaultValue": 18,
            "minValue": 0,
            "maxValue": 31,
        }

        self.r_ik_rig_color_attr = {
            "name": "r_ik_rig_color",
            "attrType": "long",
            "keyable": False,
            "defaultValue": 6,
            "minValue": 0,
            "maxValue": 31,
        }

        self.r_ik_rig_sub_color_attr = {
            "name": "r_ik_rig_sub_color",
            "attrType": "long",
            "keyable": False,
            "defaultValue": 9,
            "minValue": 0,
            "maxValue": 31,
        }

        self.m_ik_rig_color_attr = {
            "name": "m_ik_rig_color",
            "attrType": "long",
            "keyable": False,
            "defaultValue": 17,
            "minValue": 0,
            "maxValue": 31,
        }

        self.m_ik_rig_sub_color_attr = {
            "name": "m_ik_rig_sub_color",
            "attrType": "long",
            "keyable": False,
            "defaultValue": 11,
            "minValue": 0,
            "maxValue": 31,
        }

        self.main_op_nodes_attr = {
            "name": "main_op_nodes",
            "attrType": "message",
            "keyable": False,
            "channelBox": False,
        }

        self.param_list = [
            self.mainop_attr,
            self.rigname_attr,
            self.l_ik_rig_color_attr,
            self.l_ik_rig_sub_color_attr,
            self.r_ik_rig_color_attr,
            self.r_ik_rig_sub_color_attr,
            self.m_ik_rig_color_attr,
            self.m_ik_rig_sub_color_attr,
            self.main_op_nodes_attr,
        ]

    def create_node(
        self, opRootName=OPROOTNAME, mainMetaNdName=MAINMETANODENAME
    ):
        self.rootNode = pmc.createNode("transform", n=opRootName)
        attributes.lockAndHideAttributes(node=self.rootNode)
        for attr_ in self.param_list:
            attributes.addAttr(node=self.rootNode, **attr_)
        self.main_op_meta_nd = pmc.createNode("network", n=mainMetaNdName)
        self.main_op_meta_nd.message.connect(self.rootNode.main_op_nodes)
        return self.rootNode


class mainOperatorNode(OperatorsRootNode):
    def __init__(
        self,
        opMainTagName=OPMAINTAGNAME,
        opRootTagName=OPROOTTAGNAME,
        subTagName=OPSUBTAGNAME,
        errorMessage=ERRORMESSAGE["selection1"],
    ):
        super(mainOperatorNode, self).__init__()

        self.selection = pmc.ls(sl=True, typ="transform")

        for node in self.selection:
            if (
                node.hasAttr(opRootTagName)
                or node.hasAttr(opMainTagName)
                or node.hasAttr(subTagName)
            ):

                continue
            else:
                logger.log(
                    level="error", message=errorMessage, logger=moduleLogger
                )

        self.mainop_attr = {
            "name": opMainTagName,
            "attrType": "bool",
            "keyable": False,
            "defaultValue": 1,
        }

        self.compName_attr = {
            "name": "component_name",
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
        }

        self.compType_attr = {
            "name": "component_type",
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
        }

        self.compSide_attr = {
            "name": "component_side",
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
        }

        self.compIndex_attr = {
            "name": "component_index",
            "attrType": "long",
            "keyable": False,
            "channelBox": False,
            "defaultValue": 0,
        }

        self.subOperators_attr = {
            "name": "sub_operators",
            "attrType": "message",
            "keyable": False,
            "channelBox": False,
        }

        self.connector_attr = {
            "name": "connector",
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
        }

        self.attribute_list = [
            self.mainop_attr,
            self.compName_attr,
            self.compType_attr,
            self.compSide_attr,
            self.compIndex_attr,
            self.subOperators_attr,
            self.connector_attr,
        ]

    def createNode(
        self,
        colorIndex=18,
        name=MAINOPROOTNODENAME,
        sub_meta_nd_name=SUBMETANODENAME,
        side=DEFAULTSIDE,
        index=DEFAULTINDEX,
        errorMessage=ERRORMESSAGE,
        compName=DEFAULTCOMPNAME,
    ):
        if not self.selection:
            self.opRootND = self.create_node()
        else:
            self.opRootND = self.selection[0]
        self.mainOpCurve = curves.DiamondControl()
        self.mainOpND = self.mainOpCurve.create_curve(
            colorIndex=colorIndex, name=name, match=self.opRootND
        )
        for attr_ in self.attribute_list:
            attributes.addAttr(node=self.mainOpND[-1], **attr_)
        self.opRootND.addChild(self.mainOpND[0])
        self.mainOpND[1].component_side.set(side)
        self.mainOpND[1].component_index.set(index)
        self.sub_meta_nd_name = "{}_{}".format(side, sub_meta_nd_name)
        self.sub_meta_nd_name = self.sub_meta_nd_name.replace(
            "_op_", "_op_" + compName + "_"
        )
        self.sub_op_meta_node = pmc.createNode(
            "network", n=self.sub_meta_nd_name
        )
        self.sub_op_meta_node.message.connect(self.mainOpND[-1].sub_operators)
        self.mainOpND.append(self.sub_op_meta_node)
        return self.mainOpND


class create_component_operator(mainOperatorNode):
    def __init__(
        self,
        subOperatorsCount=DEFAULTSUBOPERATORSCOUNT,
        compName=DEFAULTCOMPNAME,
        side=DEFAULTSIDE,
        mainOperatorNodeName=MAINOPROOTNODENAME,
        subOperatorsNodeName=SUBOPROOTNODENAME,
        axes=DEFAULTAXES,
        spaceing=DEFAULTSPACING,
        subOperatorsScale=DEFAULTSUBOPERATORSSCALE,
        linearCurveName=LINEARCURVENAME,
        subTagName=OPSUBTAGNAME,
        sub_meta_node_attr_name=SUBMETANODEATTRNAME,
        main_meta_node_attr_name=MAINMETANODEATTRNAME,
    ):
        super(create_component_operator, self).__init__()

        self.connector_attr = {
            "name": "connector",
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
        }
        self.sub_tag_attr = {
            "name": subTagName,
            "attrType": "bool",
            "keyable": False,
            "defaultValue": 1,
        }

        self.para_list = [self.sub_tag_attr, self.connector_attr]

        self.result = []
        self.subOperators = []
        self.jointControl = curves.JointControl()
        self.mainOperatorNodeName = mainOperatorNodeName.replace(
            "M_", side + "_"
        )
        self.mainOperatorNodeName = self.mainOperatorNodeName.replace(
            "_op_", "_op_" + compName + "_"
        )
        self.mainOperatorNode = self.createNode(
            side=side, name=self.mainOperatorNodeName, compName=compName
        )
        self.result.append(self.mainOperatorNode[1])
        for sub in range(subOperatorsCount):
            instance = "_op_{}_{}".format(compName, str(sub))
            self.subOpNDName = subOperatorsNodeName.replace("M_", side + "_")
            self.subOpNDName = self.subOpNDName.replace("_op_0", instance)
            subOpNode = self.jointControl.create_curve(
                name=self.subOpNDName,
                match=self.result[-1],
                scale=subOperatorsScale,
                bufferGRP=False,
                colorIndex=21,
            )
            sub_attr_name = "{}_{}".format(sub_meta_node_attr_name, str(sub))
            attributes.addAttr(
                self.mainOperatorNode[2], sub_attr_name, "message"
            )
            subOpNode[0].message.connect(
                self.mainOperatorNode[2].attr(sub_attr_name)
            )
            self.subOperators.append(subOpNode)
            self.result[-1].addChild(subOpNode[0])
            for attr_ in self.para_list:
                attributes.addAttr(node=subOpNode[0], **attr_)
            if axes == "-X" or axes == "-Y" or axes == "-Z":
                spaceing = spaceing * -1
            if axes == "-X":
                axes = "X"
            elif axes == "-Y":
                axes = "Y"
            elif axes == "-Z":
                axes = "Z"
            subOpNode[0].attr("translate" + axes).set(spaceing)
            self.result.append(subOpNode[-1])
        self.linearCurveName = linearCurveName.replace("M_", side + "_")
        self.linearCurveName = self.linearCurveName.replace(
            "_op_", "_op_" + compName + "_"
        )
        linear_curve = curves.linear_curve(
            driverNodes=self.result, name=self.linearCurveName
        )
        linear_curve.inheritsTransform.set(0)
        self.mainOperatorNode[0].addChild(linear_curve)
        self.opRootND = mayautils.ancestors(self.result[-1])[-1]
        self.main_op_meta_nd = self.opRootND.main_op_nodes.get()
        ud_attr = self.main_op_meta_nd.listAttr(ud=True)
        temp = []
        for attribute in ud_attr:
            if strings.search(main_meta_node_attr_name, str(attribute)):
                temp.append(attribute)
        attr_name = "{}_{}".format(
            main_meta_node_attr_name, str(len(temp))
        )
        attributes.addAttr(
            node=self.main_op_meta_nd, name=attr_name, attrType="message"
        )
        self.result[0].message.connect(
            self.main_op_meta_nd.attr(attr_name)
        )
        # supOpDataStr = ",".join([str(x[0]) for x in self.subOperators])
        # self.result[0].sub_operators.set(supOpDataStr)

    def get_suboperators(self):
        print self.mainOperatorNode[1].sub_operators.get()

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
# Date:       2019 / 06 / 02

"""
JoMRS main operator module. Handles the compon
"""

import pymel.core as pmc
import logging
import logger
import attributes
import curves


##########################################################
# GLOBALS
##########################################################

module_logger = logging.getLogger(__name__ + ".py")
OPROOTTAGNAME = "JOMRS_op_root"
OPMAINTAGNAME = "JOMRS_op_main"
OPSUBTAGNAME = "JOMRS_op_sub"
OPROOTNAME = "M_MAIN_operators_0_GRP"
MAINOPROOTNODENAME = "M_MAIN_op_0_CON"
SUBOPROOTNODENAME = "M_SUB_op_0_CON"
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
##########################################################


class OperatorsRootNode(object):
    def __init__(self, op_root_tag_name=OPROOTTAGNAME):
        self.param_list = []
        self.mainop_attr = {
            "name": op_root_tag_name,
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

        self.param_list = [
            self.mainop_attr,
            self.rigname_attr,
            self.l_ik_rig_color_attr,
            self.l_ik_rig_sub_color_attr,
            self.r_ik_rig_color_attr,
            self.r_ik_rig_sub_color_attr,
            self.m_ik_rig_color_attr,
            self.m_ik_rig_sub_color_attr
        ]

    def create_node(self, op_root_name=OPROOTNAME):
        self.root_node = pmc.construct_node("transform", n=op_root_name)
        attributes.lock_and_hide_attributes(node=self.root_node)
        for attr_ in self.param_list:
            attributes.add_attr(node=self.root_node, **attr_)
        return self.root_node


class MainOperatorNode(OperatorsRootNode):
    def __init__(
        self,
        op_main_tag_name=OPMAINTAGNAME,
        op_root_tag_name=OPROOTTAGNAME,
        sub_tag_name=OPSUBTAGNAME,
        error_message=ERRORMESSAGE["selection1"],
    ):
        super(MainOperatorNode, self).__init__()

        self.selection = pmc.ls(sl=True, typ="transform")

        for node in self.selection:
            if (
                node.hasAttr(op_root_tag_name)
                or node.hasAttr(op_main_tag_name)
                or node.hasAttr(sub_tag_name)
            ):
                continue
            else:
                logger.log(
                    level="error", message=error_message, logger=module_logger
                )

        self.attribute_list = []

        self.mainop_attr = {
            "name": op_main_tag_name,
            "attrType": "bool",
            "keyable": False,
            "defaultValue": 1,
        }

        self.comp_name_attr = {
            "name": "component_name",
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
        }

        self.comp_type_attr = {
            "name": "component_type",
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
        }

        self.comp_side_attr = {
            "name": "component_side",
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
        }

        self.comp_index_attr = {
            "name": "component_index",
            "attrType": "long",
            "keyable": False,
            "channelBox": False,
            "defaultValue": 0,
        }

        self.sub_operators_attr = {
            "name": "sub_operators",
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
        }

        self.connector_attr = {
            "name": "connector",
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
        }

        temp = [
            self.mainop_attr,
            self.comp_name_attr,
            self.comp_type_attr,
            self.comp_side_attr,
            self.comp_index_attr,
            self.sub_operators_attr,
            self.connector_attr,
        ]
        for attr_ in temp:
            self.attribute_list.append(attr_)

    def construct_node(
        self,
        color_index=18,
        name=MAINOPROOTNODENAME,
        side=DEFAULTSIDE,
        index=DEFAULTINDEX,
    ):
        if not self.selection:
            self.op_root_nd = self.create_node()
        else:
            self.op_root_nd = self.selection[0]
        self.main_op_curve = curves.DiamondControl()
        self.main_op_nd = self.main_op_curve.create_curve(
            color_index=color_index, name=name, match=self.op_root_nd
        )
        for attr_ in self.attribute_list:
            attributes.add_attr(node=self.main_op_nd[-1], **attr_)
        self.op_root_nd.addChild(self.main_op_nd[0])
        self.main_op_nd[1].component_side.set(side)
        self.main_op_nd[1].component_index.set(index)
        return self.main_op_nd


class create_component_operator(MainOperatorNode):
    def __init__(
        self,
        sub_operators_count=DEFAULTSUBOPERATORSCOUNT,
        comp_name=DEFAULTCOMPNAME,
        side=DEFAULTSIDE,
        main_operator_node_name=MAINOPROOTNODENAME,
        sub_operators_node_name=SUBOPROOTNODENAME,
        axes=DEFAULTAXES,
        spaceing=DEFAULTSPACING,
        sub_operators_scale=DEFAULTSUBOPERATORSSCALE,
        linear_curve_name=LINEARCURVENAME,
        sub_tag_name=OPSUBTAGNAME,
    ):
        super(create_component_operator, self).__init__()

        self.connector_attr = {
            "name": "connector",
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
        }
        self.sub_tag_attr = {
            "name": sub_tag_name,
            "attrType": "bool",
            "keyable": False,
            "defaultValue": 1,
        }

        temp = [self.sub_tag_attr, self.connector_attr]

        self.result = []
        self.subOperators = []
        self.jointControl = curves.JointControl()
        self.main_operator_node_name = main_operator_node_name.replace(
            "M_", side + "_"
        )
        self.main_operator_node_name = self.main_operator_node_name.replace(
            "_op_", "_op_" + comp_name + "_"
        )
        self.mainOperatorNode = self
        self.mainOperatorNode = self.construct_node(
            side=side, name=self.main_operator_node_name
        )
        self.result.append(self.mainOperatorNode[1])
        for sub in range(sub_operators_count):
            instance = "_op_{}_{}".format(comp_name, str(sub))
            self.subOpNDName = sub_operators_node_name.replace("M_", side + "_")
            self.subOpNDName = self.subOpNDName.replace("_op_0", instance)
            subOpNode = self.jointControl.create_curve(
                name=self.subOpNDName,
                match=self.result[-1],
                scale=sub_operators_scale,
                buffer_grp=False,
                color_index=21,
            )
            self.subOperators.append(subOpNode)
            self.result[-1].addChild(subOpNode[0])
            for attr_ in temp:
                attributes.add_attr(node=subOpNode[0], **attr_)
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
        self.linear_curve_name = linear_curve_name.replace("M_", side + "_")
        self.linear_curve_name = self.linear_curve_name.replace(
            "_op_", "_op_" + comp_name + "_"
        )
        linear_curve = curves.linear_curve(
            driver_nodes=self.result, name=self.linear_curve_name
        )
        linear_curve.inheritsTransform.set(0)
        self.mainOperatorNode[0].addChild(linear_curve)
        supOpDataStr = ",".join([str(x[0]) for x in self.subOperators])
        self.result[0].sub_operators.set(supOpDataStr)

    def get_suboperators(self):
        print self.mainOperatorNode[1].sub_operators.get()

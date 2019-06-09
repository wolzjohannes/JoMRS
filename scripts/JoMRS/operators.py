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
# Date:       2019 / 06 / 09

"""
JoMRS main operator module. Handles the operator creation.
"""

import pymel.core as pmc
import strings
import logging
import logger
import attributes
import curves
import mayautils

##########################################################
# GLOBALS
##########################################################

module_logger = logging.getLogger(__name__ + ".py")
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
DEFAULTOPERATORNAME = "component"
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
    def __init__(self, op_root_tag_name=OPROOTTAGNAME):

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
        self, op_root_name=OPROOTNAME, main_meta_nd_name=MAINMETANODENAME
    ):
        self.root_node = pmc.createNode("transform", n=op_root_name)
        attributes.lock_and_hide_attributes(node=self.root_node)
        for attr_ in self.param_list:
            attributes.add_attr(node=self.root_node, **attr_)
        self.main_op_meta_nd = pmc.createNode("network", n=main_meta_nd_name)
        self.main_op_meta_nd.message.connect(self.root_node.main_op_nodes)
        return self.root_node


class mainOperatorNode(OperatorsRootNode):
    def __init__(
        self,
        op_main_tag_name=OPMAINTAGNAME,
        op_root_tag_name=OPROOTTAGNAME,
        sub_tag_name=OPSUBTAGNAME,
        error_message=ERRORMESSAGE["selection1"],
    ):
        super(mainOperatorNode, self).__init__()

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

    def createNode(
        self,
        color_index=18,
        name=MAINOPROOTNODENAME,
        sub_meta_nd_name=SUBMETANODENAME,
        side=DEFAULTSIDE,
        index=DEFAULTINDEX,
        comp_name=DEFAULTOPERATORNAME,
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
        self.sub_meta_nd_name = "{}_{}".format(side, sub_meta_nd_name)
        self.sub_meta_nd_name = self.sub_meta_nd_name.replace(
            "_op_", "_op_{}_".format(comp_name)
        )
        self.sub_op_meta_node = pmc.createNode(
            "network", n=self.sub_meta_nd_name
        )
        self.sub_op_meta_node.message.connect(
            self.main_op_nd[-1].sub_operators
        )
        self.main_op_nd.append(self.sub_op_meta_node)
        return self.main_op_nd


class create_component_operator(mainOperatorNode):
    def __init__(
        self,
        sub_operators_count=DEFAULTSUBOPERATORSCOUNT,
        operator_name=DEFAULTOPERATORNAME,
        side=DEFAULTSIDE,
        main_operator_node_name=MAINOPROOTNODENAME,
        sub_operators_node_name=SUBOPROOTNODENAME,
        axes=DEFAULTAXES,
        spaceing=DEFAULTSPACING,
        sub_operators_scale=DEFAULTSUBOPERATORSSCALE,
        linear_curve_name=LINEARCURVENAME,
        sub_tag_name=OPSUBTAGNAME,
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
            "name": sub_tag_name,
            "attrType": "bool",
            "keyable": False,
            "defaultValue": 1,
        }

        temp = [self.sub_tag_attr, self.connector_attr]

        self.result = []
        self.sub_operators = []
        self.joint_control = curves.JointControl()
        self.main_operator_node_name = main_operator_node_name.replace(
            "M_", "{}_".format(side)
        )
        self.main_operator_node_name = self.main_operator_node_name.replace(
            "_op_", "_op_{}_".format(operator_name)
        )
        self.main_operator_node = self.createNode(
            side=side,
            name=self.main_operator_node_name,
            comp_name=operator_name,
        )
        self.result.append(self.main_operator_node[1])
        for sub in range(sub_operators_count):
            instance = "_op_{}_{}".format(operator_name, str(sub))
            self.sub_op_nd_name = sub_operators_node_name.replace(
                "M_", "{}_".format(side)
            )
            self.sub_op_nd_name = self.sub_op_nd_name.replace(
                "_op_0", instance
            )
            sub_op_node = self.joint_control.create_curve(
                name=self.sub_op_nd_name,
                match=self.result[-1],
                scale=sub_operators_scale,
                buffer_grp=False,
                color_index=21,
            )
            sub_attr_name = "{}_{}".format(sub_meta_node_attr_name, str(sub))
            attributes.add_attr(
                self.main_operator_node[2], sub_attr_name, "message"
            )
            sub_op_node[0].message.connect(
                self.main_operator_node[2].attr(sub_attr_name)
            )
            self.sub_operators.append(sub_op_node)
            self.result[-1].addChild(sub_op_node[0])
            for attr_ in temp:
                attributes.add_attr(node=sub_op_node[0], **attr_)
            if axes == "-X" or axes == "-Y" or axes == "-Z":
                spaceing = spaceing * -1
            if axes == "-X":
                axes = "X"
            elif axes == "-Y":
                axes = "Y"
            elif axes == "-Z":
                axes = "Z"
            sub_op_node[0].attr("translate" + axes).set(spaceing)
            self.result.append(sub_op_node[-1])
        self.linear_curve_name = linear_curve_name.replace(
            "M_", "{}_".format(side)
        )
        self.linear_curve_name = self.linear_curve_name.replace(
            "_op_", "_op_{}_".format(operator_name)
        )
        linear_curve = curves.linear_curve(
            driver_nodes=self.result, name=self.linear_curve_name
        )
        linear_curve.inheritsTransform.set(0)
        self.main_operator_node[0].addChild(linear_curve)
        self.op_root_nd = mayautils.ancestors(self.result[-1])[-1]
        self.main_op_meta_nd = self.op_root_nd.main_op_nodes.get()
        ud_attr = self.main_op_meta_nd.listAttr(ud=True)
        temp = []
        for attribute in ud_attr:
            if strings.search(main_meta_node_attr_name, str(attribute)):
                temp.append(attribute)
        attr_name = "{}_{}".format(main_meta_node_attr_name, str(len(temp)))
        attributes.add_attr(
            node=self.main_op_meta_nd, name=attr_name, attrType="message"
        )
        self.result[0].message.connect(self.main_op_meta_nd.attr(attr_name))

    def get_suboperators(self):
        print self.main_operator_node[1].sub_operators.get()

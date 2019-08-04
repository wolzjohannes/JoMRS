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
# Date:       2019 / 08 / 04

"""
JoMRS main operator module. Handles the operators creation.
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
DEFAULTCONNECTIONTYPES = "translate;rotate;scale"
ERRORMESSAGE = {
    "selection": "More then one parent not allowed",
    "selection1": "Parent of main operator is no JoMRS"
    " operator main/sub node or operators root node",
    "get_attr": "attribute from main param list not on node.",
    "get_comp_side": "Registered component side not valid",
    "set_comp_side": "Selected side not valid",
}

##########################################################
# CLASSES
# To Do:
# - Refactor to make it more pythonic.
# - Add aim constraint to LRA control.
##########################################################


class OperatorsRootNode(object):
    """
    Create operators root node/god node.
    """

    def __init__(self, op_root_tag_name=OPROOTTAGNAME):
        """
        Init the user defined attributes.
        Args:
                op_root_tag_name(str): Tag name.
        """
        self.root_op_attr = {
            "name": op_root_tag_name,
            "attrType": "bool",
            "keyable": False,
            "defaultValue": 1,
        }

        self.root_op_meta_nd= {
            "name": 'root_op_meta_nd',
            "attrType": "message",
            "keyable": False,
            "channelBox": False,
        }

        self.root_node_param_list = [
            self.root_op_attr,
            self.root_op_meta_nd,
        ]

    def create_node(
        self, op_root_name=OPROOTNAME,
    ):
        """
        Execute the operators root/god node creation.
        Args:
                op_root_name(str): Tag name.
        Return:
                dagnode: The created dagnode.
        """
        self.root_node = pmc.createNode("transform", n=op_root_name)
        attributes.lock_and_hide_attributes(node=self.root_node)
        for attr_ in self.root_node_param_list:
            attributes.add_attr(node=self.root_node, **attr_)
        return self.root_node


class mainOperatorNode(OperatorsRootNode):
    """
    Create a main operator node.
    """

    def __init__(
        self,
        op_main_tag_name=OPMAINTAGNAME,
        op_root_tag_name=OPROOTTAGNAME,
        sub_tag_name=OPSUBTAGNAME,
        error_message=ERRORMESSAGE["selection1"],
    ):
        """
        Init the user defined attributes
        Args:
                op_main_tag_name(str): Tag name.
                op_root_tag_name(str): Tag name.
                sub_tag_name(str): Tag name.
                error_message(str): User feedback message.
        """
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

        self.main_op_attr = {
            "name": op_main_tag_name,
            "attrType": "bool",
            "keyable": False,
            "defaultValue": 1,
        }

        self.main_op_meta_nd = {
            "name": 'main_op_meta_nd',
            "attrType": "message",
            "keyable": False,
            "channelBox": False,
        }

        self.main_node_param_list = [
            self.main_op_attr,
            self.main_op_meta_nd,
        ]

    def construct_node(
        self,
        color_index=18,
        name=MAINOPROOTNODENAME,
        side=DEFAULTSIDE,
        index=DEFAULTINDEX,
        local_rotate_axes=True,
    ):
        """
        Execute the main operator node creation.
        Args:
                color_index(int): Viewport color.
                name(str): Operator name.
                side(str): Operators side. Valid are M,L,R.
                index(int): Operators index number.
                local_rotate_axes(bool): Enabel local rotate axes.
        Return:
                dagnode: The created main operator node.
        """
        if not self.selection:
            self.op_root_nd = self.create_node()
        else:
            self.op_root_nd = self.selection[0]
        self.main_op_curve = curves.DiamondControl()
        self.main_op_nd = self.main_op_curve.create_curve(
            color_index=color_index,
            name=name,
            match=self.op_root_nd,
            local_rotate_axes=local_rotate_axes,
        )
        for attr_ in self.main_node_param_list:
            attributes.add_attr(node=self.main_op_nd[-1], **attr_)
        self.op_root_nd.addChild(self.main_op_nd[0])
        self.main_op_nd[1].component_side.set(side)
        self.main_op_nd[1].component_index.set(index)
        self.main_op_nd.append(self.sub_op_meta_node)
        return self.main_op_nd


class create_component_operator(mainOperatorNode):
    """
    Create the whole component operator.
    Args:
            sub_tag_name(str): Tag name.
            connection_types(str): Connection type attr default value.
    """

    def __init__(self):
        super(create_component_operator, self).__init__()

    def build_node(
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
        sub_meta_node_attr_name=SUBMETANODEATTRNAME,
        main_meta_node_attr_name=MAINMETANODEATTRNAME,
        local_rotate_axes=True,
    ):
        """
        Init the operators creation.
        Args:
                sub_operators_count(int): Sub operators count.
                operator_name(str): Operators name.
                side(str): Operators side. Valid are M,L,R
                main_operator_node_name: Main Operators node name.
                sub_operators_node_name: Sub Operators node name.
                axes(str): Operators creation axe. Valid are X,Y,Z-X,-Y,-Z
                spaceing(int): Space between main and sub op nodes
                sub_operators_scale(int): Sub operators node scale factor.
                linear_curve_name(str): Operators visualisation curve name.
                sub_meta_node_attr_name(str): User defined message attribute
                name.
                main_meta_node_attr_name(str): User defined message attribute
                name.
                local_rotate_axes(bool): Enabel local rotate axes.
        """
        self.result = []
        self.sub_operators = []
        self.joint_control = curves.JointControl()
        self.main_operator_node_name = main_operator_node_name.replace(
            "M_", "{}_".format(side)
        )
        self.main_operator_node_name = self.main_operator_node_name.replace(
            "_op_", "_op_{}_".format(operator_name)
        )
        self.main_operator_node = self.construct_node(
            side=side,
            name=self.main_operator_node_name,
            operator_name=operator_name,
            local_rotate_axes=local_rotate_axes,
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
            for attr_ in self.sub_node_param_list:
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

    # def get_sub_operators(
    #     self, main_node=None, sub_metand_attr=SUBMETANODEATTRNAME
    # ):
    #     """
    #     Get the sub operators of a main operator. Return empty list if no
    #     sub operator nodes exist.
    #     Args:
    #             main_node(dagnode): If none will take the latest main op in
    #             memory.
    #             sub_metand_attr(str): Attribute name to search for meta
    #             node.
    #     Return:
    #             List: Dagnodes of found sub operators.
    #     """
    #     if main_node:
    #         metand = main_node.sub_operators.get()
    #     else:
    #         metand = self.main_operator_node[1].sub_operators.get()
    #     sub_node_attr = [
    #         ud
    #         for ud in metand.listAttr(ud=True)
    #         if strings.search(sub_metand_attr, str(ud))
    #     ]
    #     result = [pmc.PyNode(attr_.get()) for attr_ in sub_node_attr]
    #     return result
    #
    # def get_main_operators(
    #     self, root_node=None, main_metand_attr=MAINMETANODEATTRNAME
    # ):
    #     """
    #     Get the main operators of a operators root node. Return empty
    #     list if no main operators node exist.
    #     Args:
    #           root_node(dagnode): If none will take the latest root
    #           node in memory.
    #           main_metand_attr(str): Attribute name to search for meta
    #           node.
    #     Return:
    #           List: Dagnodes of found main operator nodes.
    #     """
    #     if root_node:
    #         metand = root_node.main_op_nodes.get()
    #     else:
    #         metand = self.op_root_nd.main_op_nodes.get()
    #     main_node_attr = [
    #         ud
    #         for ud in metand.listAttr(ud=True)
    #         if strings.search(main_metand_attr, str(ud))
    #     ]
    #     result = [pmc.PyNode(attr_.get()) for attr_ in main_node_attr]
    #     return result
    #
    # def get_root_node_attributes(
    #     self, root_node=None, error_message=ERRORMESSAGE["get_attr"]
    # ):
    #     """
    #     Get the rig attributes from operators root node.
    #     Args:
    #             root_node(dagnode): If none will take the latest root
    #             node in memory.
    #     Return:
    #             List: Filled with dictonaries. Example:
    #             [{'attribute':attribute;'value':value}]
    #     """
    #     result = []
    #     if root_node is None:
    #         root_node = self.op_root_nd
    #     param_list = self.root_node_param_list
    #     for param in param_list:
    #         try:
    #             dic = {}
    #             dic["attribute"] = root_node.attr(param["name"])
    #             dic["value"] = root_node.attr(param["name"]).get()
    #             result.append(dic)
    #         except:
    #             logger.log(
    #                 level="error",
    #                 message="{} {}".format(param["name"], error_message),
    #             )
    #     return result
    #
    # def get_main_node_attributes(
    #     self, main_node=None, error_message=ERRORMESSAGE["get_attr"]
    # ):
    #     """
    #     Get the rig attributes from operators root node.
    #     Args:
    #             main_node(dagnode): If none will take the latest main
    #             node in memory.
    #     Return:
    #             List: Filled with dictonaries. Example:
    #             [{'attribute':attribute;'value':value}]
    #     """
    #     result = []
    #     if main_node is None:
    #         main_node = self.main_operator_node[1]
    #     param_list = self.main_node_param_list
    #     for param in param_list:
    #         dic = {}
    #         try:
    #             dic["attribute"] = main_node.attr(param["name"])
    #             dic["value"] = main_node.attr(param["name"]).get()
    #             result.append(dic)
    #         except:
    #             logger.log(
    #                 level="error",
    #                 message="{} {}".format(param["name"], error_message),
    #             )
    #     return result
    #
    # def get_rig_name(self, root_node=None):
    #     """
    #     Get the rig name from root_node.
    #     Args:
    #             root_node(dagnode): The operators root node.
    #     Return:
    #             string: The rig name / if empty None.
    #     """
    #     if root_node is None:
    #         root_node = self.op_root_nd
    #     return root_node.attr(self.rigname_attr["name"]).get()
    #
    # def get_op_root_tag(self, root_node=None):
    #     """
    #     Get the rig name from root_node.
    #     Args:
    #             root_node(dagnode): The operators root node.
    #     Return:
    #             True or False.
    #     """
    #     if root_node is None:
    #         root_node = self.op_root_nd
    #     return root_node.attr(self.root_op_attr["name"]).get()
    #
    # def get_rig_control_colors(self, root_node=None):
    #     """
    #     Get the rig name from root_node.
    #     Args:
    #             root_node(dagnode): The operators root node.
    #     Return:
    #             list: Filled with dictonaries.
    #             [{'attribute':attribute;'value':value}]
    #     """
    #     result = []
    #     temp = [
    #         self.l_ik_rig_color_attr,
    #         self.l_ik_rig_sub_color_attr,
    #         self.r_ik_rig_color_attr,
    #         self.r_ik_rig_sub_color_attr,
    #         self.m_ik_rig_color_attr,
    #         self.m_ik_rig_sub_color_attr,
    #     ]
    #     if root_node is None:
    #         root_node = self.op_root_nd
    #     for attr_ in temp:
    #         dic = {}
    #         dic["name"] = attr_["name"]
    #         dic["value"] = root_node.attr(attr_["name"]).get()
    #         result.append(dic)
    #     return result
    #
    # def get_op_main_tag(self, main_node=None):
    #     """
    #     Get the op main tag value.
    #     Args:
    #             main_node(dagnode): Operators main node.
    #     Return:
    #             True or False.
    #     """
    #     if main_node is None:
    #         main_node = self.main_operator_node[1]
    #     return main_node.attr(self.main_op_attr["name"]).get()
    #
    # def get_component_name(self, main_node=None):
    #     """
    #     Get component name.
    #     Args:
    #             main_node(dagnode): Operators main node.
    #     Return:
    #             String or None.
    #     """
    #     if main_node is None:
    #         main_node = self.main_operator_node[1]
    #     return main_node.attr(self.comp_name_attr["name"]).get()
    #
    # def get_component_type(self, main_node=None):
    #     """
    #     Get component type.
    #     Args:
    #             main_node(dagnode): Operators main node.
    #     Return:
    #             String or None.
    #     """
    #     if main_node is None:
    #         main_node = self.main_operator_node[1]
    #     return main_node.attr(self.comp_type_attr["name"]).get()
    #
    # def get_component_side(
    #     self, main_node=None, error_message=ERRORMESSAGE["get_comp_side"]
    # ):
    #     """
    #     Get component side.
    #     Args:
    #             main_node(dagnode): Operators main node.
    #             error_message(str): Error if entry is not valid.
    #     Return:
    #             String or None.
    #     """
    #     if main_node is None:
    #         main_node = self.main_operator_node[1]
    #     value = main_node.attr(self.comp_side_attr["name"]).get()
    #     valid = ["L", "R", "M"]
    #     if value in valid:
    #         return value
    #     else:
    #         logger.log(
    #             level="error", message=error_message, logger=module_logger
    #         )
    #         return
    #
    # def get_component_index(self, main_node=None):
    #     """
    #     Get component index.
    #     Args:
    #             main_node(dagnode): Operators main node.
    #     Return:
    #             Integer.
    #     """
    #     if main_node is None:
    #         main_node = self.main_operator_node[1]
    #     return int(main_node.attr(self.comp_index_attr["name"]).get())
    #
    # def get_main_operator_connection_type(self, main_node=None):
    #     """
    #     Get component index.
    #     Args:
    #             main_node(dagnode): Operators main node.
    #     Return:
    #             String or None.
    #     """
    #     if main_node is None:
    #         main_node = self.main_operator_node[1]
    #     return main_node.attr(self.connection_type_attr["name"]).get()
    #
    # def get_sub_operators_connection_type(self, main_node=None,
    #                                   sub_operators=None):
    #     """
    #     Get connection type form sub operators.
    #     Args:
    #             main_node(dagnode): Operators main node.
    #             sub_operators(list): Filled with dagnodes.
    #     Return:
    #             list: Filled with dictonaries.
    #             [{'dagnode':suboperator;'connector':string or none}]
    #     """
    #     result = []
    #     if main_node is None:
    #         main_node = self.main_operator_node[1]
    #     if sub_operators is None:
    #         sub_operators = self.get_sub_operators(main_node=main_node)
    #     for sub in sub_operators:
    #         dic = {}
    #         dic["dagnode"] = sub
    #         dic["connector"] = sub.attr(self.connection_type_attr["name"]).get()
    #         result.append(dic)
    #     return result
    #
    # def set_rig_name(self, name, root_node=None):
    #     """
    #     Get the rig name from root_node.
    #     Args:
    #             name(str): The rig name.
    #             root_node(dagnode): The operators root node.
    #     """
    #     if root_node is None:
    #         root_node = self.op_root_nd
    #     root_node.attr(self.rigname_attr["name"]).set(name)
    #
    # def set_op_root_tag(self, value, root_node=None):
    #     """
    #     Enabel / Disable op root tag.
    #     Args:
    #             value(bool): Enable / Disable.
    #             root_node(dagnode): The operators root node.
    #     """
    #     if root_node is None:
    #         root_node = self.op_root_nd
    #     root_node.attr(self.root_op_attr["name"]).set(value)
    #
    # def set_rig_control_colors(
    #     self,
    #     l_ik_rig=None,
    #     l_ik_rig_sub=None,
    #     r_ik_rig=None,
    #     r_ik_rig_sub=None,
    #     m_ik_rig=None,
    #     m_ik_rig_sub=None,
    #     root_node=None,
    # ):
    #     """
    #     Set rig control colors.
    #     Valid is:
    #     0:GREY,1:BLACK,2:DARKGREY,3:BRIGHTGREY,4:RED,5:DARKBLUE,
    #     6:BRIGHTBLUE,7:GREEN,8:DARKLILA,9:MAGENTA,10:BRIGHTBROWN,
    #     11:BROWN,12:DIRTRED,13:BRIGHTRED,14:BRIGHTGREEN,15:BLUE,
    #     16:WHITE,17:BRIGHTYELLOW,18:CYAN,19:TURQUOISE,20:LIGHTRED,
    #     21:LIGHTORANGE,22:LIGHTYELLOW,23:DIRTGREEN,24:LIGHTBROWN,
    #     25:DIRTYELLOW,26:LIGHTGREEN,27:LIGHTGREEN2,28:LIGHTBLUE
    #     Args:
    #             l_ik_rig(int): Value.
    #             l_ik_rig_sub(int): Value.
    #             r_ik_rig(int): Value.
    #             r_ik_rig_sub(int): Value.
    #             m_ik_rig(int): Value.
    #             m_ik_rig_sub(int): Value.
    #             root_node(dagnode): The operators root node.
    #     """
    #     if root_node is None:
    #         root_node = self.op_root_nd
    #     if l_ik_rig:
    #         root_node.attr(self.l_ik_rig_color_attr["name"]).set(l_ik_rig)
    #     if l_ik_rig_sub:
    #         root_node.attr(self.l_ik_rig_sub_color_attr["name"]).set(
    #             l_ik_rig_sub
    #         )
    #     if r_ik_rig:
    #         root_node.attr(self.r_ik_rig_color_attr["name"]).set(r_ik_rig)
    #     if r_ik_rig_sub:
    #         root_node.attr(self.r_ik_rig_sub_color_attr["name"]).set(
    #             r_ik_rig_sub
    #         )
    #     if m_ik_rig:
    #         root_node.attr(self.m_ik_rig_color_attr["name"]).set(m_ik_rig)
    #     if m_ik_rig_sub:
    #         root_node.attr(self.m_ik_rig_sub_color_attr["name"]).set(
    #             m_ik_rig_sub
    #         )
    #
    # def set_op_main_tag(self, value, main_node=None):
    #     """
    #     Disable / Enable the op main tag.
    #     Args:
    #             value(bool): Enable/Disable.
    #             main_node(dagnode): Operators main node.
    #     """
    #     if main_node is None:
    #         main_node = self.main_operator_node[1]
    #     main_node.attr(self.main_op_attr["name"]).set(value)
    #
    # def set_component_name(self, name, main_node=None):
    #     """
    #     Set component name.
    #     Args:
    #             name(str): Component name.
    #             main_node(dagnode): Operators main node.
    #     """
    #     if main_node is None:
    #         main_node = self.main_operator_node[1]
    #     main_node.attr(self.comp_name_attr["name"]).set(name)
    #
    # def set_component_type(self, type, main_node=None):
    #     """
    #     Set component type.
    #     Args:
    #             type(str): Specifie the component.
    #             main_node(dagnode): Operators main node.
    #     """
    #     if main_node is None:
    #         main_node = self.main_operator_node[1]
    #     main_node.attr(self.comp_type_attr["name"]).set(type)
    #
    # def set_component_side(
    #     self, side, main_node=None, error_message=ERRORMESSAGE["set_comp_side"]
    # ):
    #     """
    #     Set component side.
    #     Args:
    #             side(str): Valid is L,R,M.
    #             main_node(dagnode): Operators main node.
    #             error_message(str): Error if side is not valid.
    #     """
    #     valid = ["L", "R", "M"]
    #     if main_node is None:
    #         main_node = self.main_operator_node[1]
    #     if side in valid:
    #         main_node.attr(self.comp_side_attr["name"]).set(side)
    #     else:
    #         logger.log(
    #             level="error", message=error_message, logger=module_logger
    #         )
    #         return
    #
    # def set_component_index(self, index, main_node=None):
    #     """
    #     Set component index.
    #     Args:
    #             index(int): The index.
    #             main_node(dagnode): Operators main node.
    #     """
    #     if main_node is None:
    #         main_node = self.main_operator_node[1]
    #     main_node.attr(self.comp_index_attr["name"]).set(index)
    #
    # def set_connection_type(self, type, main_node=None):
    #     """
    #     Set component index.
    #     Args:
    #             type(str): Connection type.
    #             main_node(dagnode): Operators main node.
    #     """
    #     if main_node is None:
    #         main_node = self.main_operator_node[1]
    #     main_node.attr(self.connection_type_attr["name"]).set(type)
    #
    # def set_sub_operators_connection_type(self, type, sub_operators=None):
    #     """
    #     Set connection type for sub operator.
    #     Args:
    #             type(str): The connection type for the sub_operators.
    #             sub_operators(list): Sub operators dagnode list.
    #     """
    #     for sub in sub_operators:
    #         sub.attr(self.connection_type_attr["name"]).set(type)

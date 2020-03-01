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
# Date:       2020 / 02 / 20

"""
JoMRS main operator module. Handles the operators creation.
"""

import pymel.core as pmc
import logging
import logger
import attributes
import curves
import mayautils
import meta

reload(meta)

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
ROOTOPMETANODENAME = "M_ROOT_op_0"
ROOTOPMETANDATTRNAME = "root_op_meta_nd"
MAINOPMETANDATTRNAME = "main_op_meta_nd"
SUBOPMETANDATTRNAME = "sub_op_meta_nd"
MAINOPMESSAGEATTRNAME = "main_operator_nd"
LINEARCURVENAME = "M_linear_op_0_CRV"
DEFAULTOPERATORNAME = "component"
DEFAULTSIDE = "M"
DEFAULTINDEX = 0
DEFAULTSUBOPERATORSCOUNT = 0
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
MAINOPMETAPARAMS = meta.MAINOPMETAPARAMS

##########################################################
# CLASSES
# To Do:
# - Add aim constraint to LRA control.
# - Parent operator curve under main control.
# - Delete first buffer group. Be able to delete the whole component.
# - All methods to be able to create a full operartor and set
#   all meta datas.
# - Able to get back the meta node and its data.
##########################################################


class OperatorsRootNode(object):
    """
    Create operators root node/god node.
    """

    def __init__(
        self,
        op_root_tag_name=OPROOTTAGNAME,
        root_op_meta_nd_attr_name=ROOTOPMETANDATTRNAME,
    ):
        """
        Init the user defined attributes.
        Args:
                op_root_tag_name(str): Tag name.
                root_op_meta_nd_attr_name(str): Message attr to root op meta nd.
        """
        self.root_op_attr = {
            "name": op_root_tag_name,
            "attrType": "bool",
            "keyable": False,
            "defaultValue": 1,
        }

        self.root_op_meta_nd = {
            "name": root_op_meta_nd_attr_name,
            "attrType": "message",
            "keyable": False,
            "channelBox": False,
        }

        self.root_node_param_list = [self.root_op_attr, self.root_op_meta_nd]

    def create_node(
        self,
        op_root_name=OPROOTNAME,
        root_op_meta_nd_attr_name=ROOTOPMETANDATTRNAME,
        root_op_meta_nd_name=ROOTOPMETANODENAME,
    ):
        """
        Execute the operators root/god node creation.
        Args:
                op_root_name(str): Tag name.
                root_op_meta_nd_attr_name(str): Message attr to root op meta nd.
                root_op_meta_nd_name(str): Root meta node name.
        Return:
                dagnode: The created dagnode.
        """
        self.root_node = pmc.createNode("transform", n=op_root_name)
        attributes.lock_and_hide_attributes(node=self.root_node)
        for attr_ in self.root_node_param_list:
            attributes.add_attr(node=self.root_node, **attr_)
        self.meta_nd = meta.RootOpMetaNode(n=root_op_meta_nd_name)
        self.meta_nd.message.connect(
            self.root_node.attr(root_op_meta_nd_attr_name)
        )
        return self.root_node


class mainOperatorNode(OperatorsRootNode):
    """
    Create a main operator node.
    """

    def __init__(
        self,
        op_main_tag_name=OPMAINTAGNAME,
        op_root_tag_name=OPROOTTAGNAME,
        op_sub_tag_name=OPSUBTAGNAME,
        error_message=ERRORMESSAGE["selection1"],
        root_op_meta_nd_attr_name=ROOTOPMETANDATTRNAME,
        main_op_meta_nd_attr_name=MAINOPMETANDATTRNAME,
    ):
        """
        Init the user defined attributes
        Args:
                op_main_tag_name(str): Tag name.
                op_root_tag_name(str): Tag name.
                op_sub_tag_name(str): Tag name.
                error_message(str): User feedback message.
                root_op_meta_nd_attr_name(str): Message attr to root op meta nd.
                main_op_meta_nd_attr_name(str): Message attr to main op nd.
        """
        super(mainOperatorNode, self).__init__()

        self.selection = pmc.ls(sl=True, typ="transform")

        for node in self.selection:
            if (
                node.hasAttr(op_root_tag_name)
                or node.hasAttr(op_main_tag_name)
                or node.hasAttr(op_sub_tag_name)
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
            "name": main_op_meta_nd_attr_name,
            "attrType": "message",
            "keyable": False,
            "channelBox": False,
        }

        self.root_op_meta_nd = {
            "name": root_op_meta_nd_attr_name,
            "attrType": "message",
            "keyable": False,
            "channelBox": False,
        }

        self.main_node_param_list = [
            self.main_op_attr,
            self.main_op_meta_nd,
            self.root_op_meta_nd,
        ]

    def construct_node(
        self,
        color_index=18,
        name=MAINOPROOTNODENAME,
        local_rotate_axes=True,
        root_op_meta_nd_attr_name=ROOTOPMETANDATTRNAME,
    ):
        """
        Execute the main operator node creation.
        Args:
                color_index(int): Viewport color.
                name(str): Operator name.
                side(str): Operators side. Valid are M,L,R.
                index(int): Operators index number.
                local_rotate_axes(bool): Enabel local rotate axes.
                root_op_meta_nd_attr_name(str): Message attr to root op meta nd.
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
        meta_name = name.replace("_CON", "")
        self.main_meta_nd = meta.MainOpMetaNode(n=meta_name)
        self.main_meta_nd.message.connect(self.main_op_nd[1].main_op_meta_nd)
        self.main_op_nd[1].message.connect(self.main_meta_nd.main_operator_nd)
        self.root_meta_nd = self.op_root_nd.attr(
            root_op_meta_nd_attr_name
        ).get()
        self.root_meta_nd.message.connect(
            self.main_op_nd[1].attr(root_op_meta_nd_attr_name)
        )
        self.root_meta_nd.add_main_meta_node(node=self.main_meta_nd)
        return self.main_op_nd


class create_component_operator(mainOperatorNode):
    """
    Create the whole component operator.
    """
    def __init__(self, operator_root_nd=None):
        """ Init all important data.
        Args:
                operator_root_nd(pmc.PyNode(), optional): The
                operators_root_node.
        """
        super(create_component_operator, self).__init__()
        self.op_root_nd = operator_root_nd
        self.result = []
        self.sub_operators = []
        self.joint_control = None
        self.main_operator_node_name = None
        self.main_operator_node = None
        self.root_meta_nd = None
        self.main_meta_nd = self.get_main_meta_node()
        self.sub_op_nd_name = None
        self.sub_meta_nd = None
        self.linear_curve_name = None
        self.main_operator_node = None

    def init_operator(
        self,
        sub_operators_count=DEFAULTSUBOPERATORSCOUNT,
        operator_name=DEFAULTOPERATORNAME,
        side=DEFAULTSIDE,
        main_operator_node_name=MAINOPROOTNODENAME,
        sub_operators_node_name=SUBOPROOTNODENAME,
        axes=DEFAULTAXES,
        spacing=DEFAULTSPACING,
        sub_operators_scale=DEFAULTSUBOPERATORSSCALE,
        linear_curve_name=LINEARCURVENAME,
        local_rotate_axes=True,
        op_sub_tag_name=OPSUBTAGNAME,
        root_op_meta_nd_attr_name=ROOTOPMETANDATTRNAME,
        sub_op_meta_nd_attr_name=SUBOPMETANDATTRNAME,
        main_op_meta_nd_attr_name=MAINOPMETANDATTRNAME,
        main_op_message_attr_name=MAINOPMESSAGEATTRNAME,
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
                spacing(int): Space between main and sub op nodes
                sub_operators_scale(int): Sub operators node scale factor.
                linear_curve_name(str): Operators visualisation curve name.
                local_rotate_axes(bool): Enabel local rotate axes.
                op_sub_tag_name(str): Tag name.
                root_op_meta_nd_attr_name(str): Message attr to root op meta nd.
                sub_op_meta_nd_attr_name(str): Message attr to sub op meta nd.
                main_op_meta_nd_attr_name(str): Message attr to main op meta nd.
        Returns:
                List: The operators root node.
        """
        if not sub_operators_count:
            sub_operators_count = DEFAULTSUBOPERATORSCOUNT
        if not operator_name:
            operator_name = DEFAULTOPERATORNAME
        if not side:
            side = DEFAULTSIDE
        if not axes:
            axes = DEFAULTAXES
        if not spacing:
            spacing = DEFAULTSPACING
        if not sub_operators_scale:
            sub_operators_scale = DEFAULTSUBOPERATORSSCALE
        self.joint_control = curves.JointControl()
        self.main_operator_node_name = main_operator_node_name.replace(
            "M_", "{}_".format(side)
        )
        self.main_operator_node_name = self.main_operator_node_name.replace(
            "_op_", "_op_{}_".format(operator_name)
        )
        self.main_operator_node = self.construct_node(
            name=self.main_operator_node_name,
            local_rotate_axes=local_rotate_axes,
        )
        self.result.append(self.main_operator_node[1])
        self.root_meta_nd = (
            self.main_operator_node[1].attr(root_op_meta_nd_attr_name).get()
        )
        self.main_meta_nd = (
            self.main_operator_node[1].attr(main_op_meta_nd_attr_name).get()
        )
        self.main_meta_nd.component_side.set(side)
        for sub in range(sub_operators_count):
            instance = "_op_{}_{}".format(operator_name, str(sub))
            self.sub_op_nd_name = sub_operators_node_name.replace(
                "M_", "{}_".format(side)
            )
            self.sub_op_nd_name = self.sub_op_nd_name.replace("_op_0", instance)
            self.sub_meta_nd = meta.SubOpMetaNode(
                n=self.sub_op_nd_name.replace("_CON", "")
            )
            self.main_meta_nd.add_sub_meta_node(node=self.sub_meta_nd)
            sub_op_node = self.joint_control.create_curve(
                name=self.sub_op_nd_name,
                match=self.result[-1],
                scale=sub_operators_scale,
                buffer_grp=False,
                color_index=21,
            )

            attributes.add_attr(
                node=sub_op_node[0],
                name=op_sub_tag_name,
                attrType="bool",
                keyable=False,
                channelBox=False,
                defaultValue=1,
            )

            attributes.add_attr(
                node=sub_op_node[0],
                name=sub_op_meta_nd_attr_name,
                attrType="message",
                keyable=False,
                channelBox=False,
                input=self.sub_meta_nd.message,
            )

            attributes.add_attr(
                node=sub_op_node[0],
                name=root_op_meta_nd_attr_name,
                attrType="message",
                keyable=False,
                channelBox=False,
                input=self.root_meta_nd.message,
            )

            attributes.add_attr(
                node=sub_op_node[0],
                name=main_op_message_attr_name,
                attrType="message",
                keyable=False,
                channelBox=False,
                input=self.main_operator_node[1].message,
            )

            sub_op_node[0].message.connect(self.sub_meta_nd.sub_operator_nd)
            self.sub_operators.append(sub_op_node)
            self.result[-1].addChild(sub_op_node[0])
            if axes == "-X" or axes == "-Y" or axes == "-Z":
                spacing = spacing * -1
            if axes == "-X":
                axes = "X"
            elif axes == "-Y":
                axes = "Y"
            elif axes == "-Z":
                axes = "Z"
            sub_op_node[0].attr("translate" + axes).set(spacing)
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
        return self.op_root_nd

    def set_component_type(self, type, plug=MAINOPMETAPARAMS[1]):
        """
        Set the component type.
        Args:
                type(str): The component type.
        """
        self.main_meta_nd.attr(plug).set(type)

    def set_component_name(self, name, plug=MAINOPMETAPARAMS[0]):
        """
        Set the component name.
        Args:
                name(str): The component name.
        """
        self.main_meta_nd.attr(plug).set(name)

    def set_component_side(self, side, plug=MAINOPMETAPARAMS[2]):
        """
        Set the component side.
        Args:
                side(str): The component side.
        """
        self.main_meta_nd.attr(plug).set(side)

    def set_component_index(self, index, plug=MAINOPMETAPARAMS[3]):
        """
        Set the compnent indes.
        Args:
                index(int): The component index.
        """
        self.main_meta_nd.attr(plug).set(index)

    def set_ik_spaces_ref(self, spaces, plug=MAINOPMETAPARAMS[5]):
        """
        Set the ik_spaces_reference nodes.
        Args:
                spaces(list): The references for the ik spaces.
        """
        if not isinstance(spaces, list):
            logger.log(
                level="error",
                message="Argument is no list",
                func=self.set_ik_spaces_ref,
                logger=module_logger,
            )
            return
        self.main_meta_nd.attr(plug).set(";".join(spaces))

    def set_connect_nd(self, node, plug=MAINOPMETAPARAMS[9]):
        """
        Set the element connect node for build process.
        """
        self.main_meta_nd.attr(plug).set(node)

    def get_main_meta_node(self):
        """
        Get main meta node from operator root node.
        Return:
                pmc.PyNode(): The meta main node.
        """
        if self.op_root_nd:
            return self.op_root_nd.main_op_meta_nd.get()

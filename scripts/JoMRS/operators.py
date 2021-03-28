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
# Date:       2021 / 03 / 14

"""
JoMRS main operator module. Handles the operators creation.
"""

import pymel.core as pmc
import constants
import logging
import logger
import attributes
import curves
import mayautils
import meta
import os
import strings
import re
import uuid

##########################################################
# GLOBALS
##########################################################

_LOGGER = logging.getLogger(__name__ + ".py")

##########################################################
# FUNCTIONS
##########################################################


def valid_node(node, typ):
    """
    Valid node check

    Args:
        node(pmc.PyNode()): Check if node is a valid JoMRS node.
        typ(str): JoMRS node typ. Valid values are ['JoMRS_root',
        'JoMRS_main', 'JoMRS_sub']

    Return:
        True if successful. False if not.

    """
    tag = None
    error_message = None
    if (
        (
            node.hasAttr(constants.OP_ROOT_TAG_NAME)
            and node.attr(constants.OP_ROOT_TAG_NAME).get() is True
        )
        or (
            node.hasAttr(constants.OP_MAIN_TAG_NAME)
            and node.attr(constants.OP_MAIN_TAG_NAME).get() is True
        )
        or (
            node.hasAttr(constants.OP_SUB_TAG_NAME)
            and node.attr(constants.OP_SUB_TAG_NAME).get() is True
        )
    ):
        error_message = True
    if typ is "JoMRS_root":
        tag = constants.OP_ROOT_TAG_NAME
    elif typ is "JoMRS_main":
        tag = constants.OP_MAIN_TAG_NAME
    elif typ is "JoMRS_sub":
        tag = constants.OP_SUB_TAG_NAME
    if node.hasAttr(tag) and node.attr(tag).get() is True:
        return True
    else:
        if not error_message:
            logger.log(
                level="error",
                message="{} is no JoMRS root operator, main operator or sub "
                "operator node.".format(str(node)),
                logger=_LOGGER,
            )
        return False


def parent_operator_node(child, parent):
    """
    Parent a JoMRS main_op_nd to a JoMRS root_op_nd, main_op_nd or sub_op_nd.
    It always add the child node to the correct container and sets all needed
    meta data as well.

    Args:
        parent(pmc.PyNode()): The parent node.
        child(pmc.PyNode()): The child node.

    """
    child_instance = ComponentOperator(child, child, child)
    parent_instance = ComponentOperator(parent, parent, parent)
    parent_instance.add_node(child_instance.main_op_nd)
    if parent_instance.op_root_nd is not parent:
        parent.addChild(child)
        child_instance.set_parent_ws_output_index(parent)
        child_instance.set_parent_nd(parent_instance.main_op_nd)


##########################################################
# CLASSES
##########################################################


class OperatorsRootNode(object):
    """
    Create operators root node/god node.
    """

    def __init__(self, operators_root_node=None):
        """
        Init the OperatorsRootNode.

        Args:
            operators_root_node(pmc.PyNode()): The operators root node.

        Return:
            None if given operators_root_node is not valid.

        """
        self.god_meta_nd = None
        self.root_meta_nd = None
        self.op_root_nd = operators_root_node
        # Check if node is a valid root node.
        if self.op_root_nd:
            if not valid_node(self.op_root_nd, typ="JoMRS_root"):
                self.op_root_nd = None
            else:
                self.get_root_meta_nd_from_op_root_nd()
        self.root_op_attr = {
            "name": constants.OP_ROOT_TAG_NAME,
            "attrType": "bool",
            "keyable": False,
            "defaultValue": 1,
        }

        self.root_op_meta_nd_attr = {
            "name": constants.ROOT_OP_META_ND_ATTR_NAME,
            "attrType": "message",
            "keyable": False,
            "channelBox": False,
        }

        self.op_root_nd_param_list = [
            self.root_op_attr,
            self.root_op_meta_nd_attr,
        ]

    def create_root_op_node(self):
        """
        Execute the operators root/god node creation.

        Return:
                pmc.PyNode(): The created dagnode.

        """
        # Create a asset container as root node.
        icon = os.path.normpath(
            "{}/root_operator_logo.png".format(constants.ICONS_PATH)
        )
        container_node = mayautils.ContainerNode(constants.OP_ROOT_NAME, icon)
        container_node.create_container(meta_nd=False)
        self.op_root_nd = container_node.container
        self.op_root_nd.rename(
            strings.normalize_suffix_1(self.op_root_nd.name(), _LOGGER)
        )
        for attr_ in self.op_root_nd_param_list:
            attributes.add_attr(node=self.op_root_nd, **attr_)
        # Create the meta node for the root node.
        self.root_meta_nd = meta.RootOpMetaNode(
            n=constants.ROOT_OP_META_NODE_NAME
        )
        self.root_meta_nd.rename(
            strings.normalize_suffix_1(self.root_meta_nd.name(), _LOGGER)
        )
        # add root meta nd to container node.
        self.op_root_nd.addNode(self.root_meta_nd)
        # Connect root meta node with root node and visa versa.
        self.root_meta_nd.message.connect(
            self.op_root_nd.attr(constants.ROOT_OP_META_ND_ATTR_NAME)
        )
        self.root_meta_nd.set_root_op_nd(self.op_root_nd)
        self.root_meta_nd.set_uuid(
            "{}-{}".format(str(uuid.uuid4()), constants.OP_ROOT_ND_UUID_SUFFIX)
        )

    def add_node(self, node):
        """
        Add node to root operator node.

        Args:
            node(pmc.PyNode()): Node to add.

        """
        self.op_root_nd.addNode(node, ish=True, ihb=True, iha=True, inc=True)

    def add_node_to_god_meta_nd(self, node):
        """
        Add a node to the operators root node. And add it to the god meta node.
        Will raise an error and return False if node is not a valid JoMRS
        main operator node.

        Args:
            node(pmc.PyNode()): The main operator node to add.

        Return: True if successful.

        """
        if (
            not node.hasAttr(constants.OP_MAIN_TAG_NAME)
            or node.attr(constants.OP_MAIN_TAG_NAME).get() is False
        ):
            logger.log(
                level="error",
                message="{} is no JoMRS main operator "
                "node".format(str(node)),
                logger=_LOGGER,
            )
            return False
        main_meta_nd = node.attr(constants.MAIN_OP_META_ND_ATTR_NAME).get()
        self.root_meta_nd.add_main_meta_node(node=main_meta_nd)
        return True

    def get_root_meta_nd_from_op_root_nd(self):
        """
        Gives the root meta node from operators root node.

        Return:
            pmc.PyNode(): The meta network node.

        """
        self.root_meta_nd = self.op_root_nd.attr(
            constants.ROOT_OP_META_ND_ATTR_NAME
        ).get()
        return self.root_meta_nd

    def get_root_nd_from_root_meta_nd(self):
        """
        Gives the root operator node form root meta node.

        Return:
             pmc.PyNode(): The meta network node.

        """
        self.op_root_nd = self.root_meta_nd.attr(
            constants.ROOT_OP_MESSAGE_ATTR_NAME
        ).get()
        return self.op_root_nd

    def set_rig_name(self, name):
        """
        Set rig name

        Attr:
            name(str)

        """
        self.root_meta_nd.attr(constants.META_ROOT_RIG_NAME).set(name)

    def set_l_control_rig_color(self, color_index):
        """
        Set left rig control color index.

        Args:
            color_index(int): Maya color index range.

        """
        self.root_meta_nd.attr(constants.META_LEFT_RIG_COLOR).set(color_index)

    def set_l_sub_control_rig_color(self, color_index):
        """
        Set left sub rig control color index.

        Args:
            color_index(int): Maya color index range.

        """
        self.root_meta_nd.attr(constants.META_LEFT_RIG_SUB_COLOR).set(
            color_index
        )

    def set_r_control_rig_color(self, color_index):
        """
        Set right rig control color index.

        Args:
            color_index(int): Maya color index range.

        """
        self.root_meta_nd.attr(constants.META_RIGHT_RIG_COLOR).set(color_index)

    def set_r_sub_control_rig_color(self, color_index):
        """
        Set right sub rig control color index.

        Args:
            color_index(int): Maya color index range.

        """
        self.root_meta_nd.attr(constants.META_RIGHT_RIG_SUB_COLOR).set(
            color_index
        )

    def set_m_control_rig_color(self, color_index):
        """
        Set middle rig control color index.

        Args:
            color_index(int): Maya color index range.

        """
        self.root_meta_nd.attr(constants.META_MID_RIG_COLOR).set(color_index)

    def set_m_sub_control_rig_color(self, color_index):
        """
        Set middle sub rig control color index.

        Args:
            color_index(int): Maya color index range.

        """
        self.root_meta_nd.attr(constants.META_MID_RIG_SUB_COLOR).set(
            color_index
        )

    def get_rig_name(self):
        """
        Get rig name

        Return:
            String: Given rig name.

        """
        return self.root_meta_nd.attr(constants.META_ROOT_RIG_NAME).get()

    def get_l_control_rig_color(self):
        """
        Get left rig control color index.

        Return:
            Integer: Maya color index range.

        """
        return self.root_meta_nd.attr(constants.META_LEFT_RIG_COLOR).get()

    def get_l_sub_control_rig_color(self):
        """
        Get left rig sub control color index.

        Return:
            Integer: Maya color index range.

        """
        return self.root_meta_nd.attr(constants.META_LEFT_RIG_SUB_COLOR).get()

    def get_r_control_rig_color(self):
        """
        Get right rig control color index.

        Return:
            Integer: Maya color index range.

        """
        return self.root_meta_nd.attr(constants.META_RIGHT_RIG_COLOR).get()

    def get_r_sub_control_rig_color(self):
        """
        Get right rig sub control color index.

        Return:
            Integer: Maya color index range.

        """
        return self.root_meta_nd.attr(constants.META_RIGHT_RIG_SUB_COLOR).get()

    def get_m_control_rig_color(self):
        """
        Get middle rig control color index.

        Return:
            Integer: Maya color index range.

        """
        return self.root_meta_nd.attr(constants.META_MID_RIG_COLOR).get()

    def get_m_sub_control_rig_color(self):
        """
        Get middle rig sub control color index.

        Return:
            Integer: Maya color index range.

        """
        return self.root_meta_nd.attr(constants.META_MID_RIG_SUB_COLOR).get()


class MainOperatorNode(OperatorsRootNode):
    """
    Create a main operator node.
    """

    COLOR_INDEX = 18

    def __init__(self, operators_root_node=None, main_operator_node=None):
        """
        Init the MainOperatorNode.

        Args:
                operators_root_node(pmc.PyNode(), optional): The operators root
                node.
                main_operator_node(pmc.PyNode(), optional): The
                operators_root_node.

        """
        OperatorsRootNode.__init__(self, operators_root_node)

        self.main_op_nd = main_operator_node
        if self.main_op_nd:
            if not valid_node(self.main_op_nd, typ="JoMRS_main"):
                self.main_op_nd = None
        self.main_meta_nd = []
        self.lra_node_buffer_grp = []
        self.lra_node = []
        self.main_op_nd_name = constants.MAIN_OP_ROOT_NODE_NAME
        self.main_meta_nd_name = constants.MAIN_OP_ROOT_NODE_NAME.replace(
            "_CON", ""
        )
        if self.main_op_nd:
            self.get_main_meta_nd()

        self.main_op_attr = {
            "name": constants.OP_MAIN_TAG_NAME,
            "attrType": "bool",
            "keyable": False,
            "defaultValue": 1,
        }

        self.main_op_meta_nd_attr = {
            "name": constants.MAIN_OP_META_ND_ATTR_NAME,
            "attrType": "message",
            "keyable": False,
            "channelBox": False,
        }

        self.node_list_attr = {
            "name": constants.NODE_LIST_ATTR_NAME,
            "attrType": "message",
            "keyable": False,
            "channelBox": False,
            "multi": True,
        }

        self.lra_op_attr = {
            "name": constants.OP_LRA_TAG_NAME,
            "attrType": "bool",
            "keyable": False,
            "defaultValue": 1,
        }

        self.main_node_param_list = [
            self.main_op_attr,
            self.main_op_meta_nd_attr,
            self.root_op_meta_nd_attr,
            self.node_list_attr,
        ]

    def create_main_op_node(self, local_rotate_axes=True, match=None):
        """
        Execute the main operator node creation.

        Args:
                local_rotate_axes(bool): Enable local rotate axes.
                match(pmc.PyNode): Node to snap for

        Return:

                pmc.PyNode(): The created main operator node.

        """
        main_op_curve = curves.DiamondControl()
        main_op_node = main_op_curve.create_curve(
            color_index=self.COLOR_INDEX,
            name=self.main_op_nd_name,
            local_rotate_axes=local_rotate_axes,
            buffer_grp=False,
            match=match,
        )
        self.main_op_nd = main_op_node[0]
        self.lra_node_buffer_grp = main_op_node[1]
        self.lra_node = main_op_node[2]
        attributes.add_attr(node=self.lra_node, **self.lra_op_attr)
        for attr_ in self.main_node_param_list:
            attributes.add_attr(node=self.main_op_nd, **attr_)
        # Connect main operator node with main meta node.
        self.set_main_meta_nd()
        self.main_meta_nd.set_uuid(
            "{}-{}".format(str(uuid.uuid4()), constants.MAIN_OP_ND_UUID_SUFFIX)
        )

    def set_main_meta_nd(self):
        """
        Set the main meta nd.

        Args:
            name(str): The operator name.

        """
        self.main_meta_nd = meta.MainOpMetaNode(n=self.main_meta_nd_name)
        self.main_meta_nd.message.connect(
            self.main_op_nd.attr(constants.MAIN_OP_META_ND_ATTR_NAME)
        )
        self.main_op_nd.message.connect(
            self.main_meta_nd.attr(constants.MAIN_OP_MESSAGE_ATTR_NAME)
        )

    def get_main_meta_nd(self):
        """
        Get main meta node.

        Return:
            pmc.PyNode(): The meta network node.

        """
        self.main_meta_nd = self.main_op_nd.attr(
            constants.MAIN_OP_META_ND_ATTR_NAME
        ).get()
        return self.main_meta_nd

    def get_root_meta_nd_from_main_op_nd(self, main_op_nd=None):
        """
        Get root meta node from main operator node.

        Args:
            main_op_nd(pmc.PyNode()): The given main_op_nd.

        Return:
            pmc.PyNode(): The meta network node.

        """
        if not main_op_nd:
            main_op_nd = self.main_op_nd
        self.root_meta_nd = main_op_nd.attr(
            constants.ROOT_OP_META_ND_ATTR_NAME
        ).get()
        return self.root_meta_nd

    def set_root_meta_nd(self):
        """
        Set the root meta node.
        """
        self.root_meta_nd.message.connect(
            self.main_op_nd.attr(constants.ROOT_OP_META_ND_ATTR_NAME)
        )


class ComponentOperator(MainOperatorNode):
    """
    Create the whole Component operator.
    """

    SUB_ND_COLOR_INDEX = 21
    NEXT_AVAILABLE_COUNT = 1000

    def __init__(
        self,
        operators_root_node=None,
        main_operator_node=None,
        sub_operator_node=None,
    ):
        """
        Init all important data. Set attributes and check if a
        parent node is passed. Parent node could be operators_root or
        main_operator node.

        Args:
            operators_root_node(pmc.PyNode(), optional): The operators root
            node.
            main_operator_node(pmc.PyNode(), optional): The main operator_node.
            sub_operator_node(pmc.PyNode(), optional)): The sub operator node.

        Example:
            (1)
            Example without selection. Basic creation of a operator.
            Index, side and sub_operators_count are on default.
            >>> import operators
            >>> component_op = operators.ComponentOperator()
            >>> component_op.create_component_op_node('Test')
            (2)
            Example to pass a selected JoMRS Operator object in the operators
            class. So you are able to use all getters and setters.
            >>> import operators
            >>> import components.main as main
            >>> selection = main.selected()
            >>> component_op = operators.ComponentOperator(
            >>> operators_root_node=selection, main_operator_node=selection,
            >>> sub_operator_node=selection)
            (3)
            Example to build a new operator as child of selected JoMRS
            Operator object
            >>> import operators
            >>> import components.main as main
            >>> component_op_test = operators.ComponentOperator()
            >>> component_op_test.create_component_op_node(name='test',
            >>> sub_operators_count=2)
            # Select the created operator container or main operator node or
            the sub operator node. Then store the selection with the
            main.selected() function.
            >>> selection = main.selected()
            >>> component_op_test = operators.ComponentOperator(selection,
            >>> selection, selection)
            >>> component_op_test.create_component_op_node(name='mom',
            >>> sub_operators_count=1, parent=selection)


        """
        MainOperatorNode.__init__(self, operators_root_node, main_operator_node)
        self.all_container_nodes = []
        self.sub_lra_nodes = []
        self.sub_operators = []
        self.sub_operators_lra_buffer = []
        self.cd_attributes = []
        self.joint_control = None
        self.main_op_nd_name = None
        self.sub_op_nd_name = None
        self.sub_meta_nd = None
        self.linear_curve = None
        self.linear_curve_name = None
        self.parent = None
        self.parent_main_op_nd = None
        # Check at init if a root operator/main operator/sub operator node is
        # passed into the class.
        if self.main_op_nd:
            # If a valid main op node is passed get all important meta data.
            self.get_root_meta_nd_from_main_op_nd()
            self.get_root_nd_from_root_meta_nd()
            self.get_sub_op_nodes_from_main_op_nd()
            self.get_node_list()
            self.get_lra_node()
            self.get_sub_lra_nodes()
        if sub_operator_node:
            if valid_node(sub_operator_node, "JoMRS_sub"):
                # If a valid sub op node is passed get the main_op_nd form
                # sub node and get all meta data.
                self.main_op_nd = self.get_main_op_node_from_sub(
                    sub_operator_node
                )
                self.get_root_meta_nd_from_main_op_nd()
                self.get_root_nd_from_root_meta_nd()
                self.get_node_list()
                self.get_lra_node()
                self.get_sub_lra_nodes()

        self.linear_curve_drivers = []

        self.sub_op_attr = {
            "name": constants.OP_SUB_TAG_NAME,
            "attrType": "bool",
            "keyable": False,
            "defaultValue": 1,
        }

        self.sub_op_meta_nd_attr = {
            "name": constants.SUB_OP_META_ND_ATTR_NAME,
            "attrType": "message",
            "keyable": False,
        }

        self.sub_node_param_list = [
            self.sub_op_attr,
            self.sub_op_meta_nd_attr,
            self.root_op_meta_nd_attr,
        ]

    def create_sub_operator(
        self, name, side, index, count, scale, match, local_rotate_axes=False
    ):
        """
        Create the sub operators node.

        Args:
            name(str): Operators name.
            side(str): Side. Valid values are [L, R, M]
            index(int): Operators index.
            count(int): The sub_op_nd count.
            scale(float): Scale value.
            match(pmc.PyNode()): Object to snap for.
            local_rotate_axes(bool): Enable local rotate axes.

        """
        instance = "_op_{}_{}_{}".format(name, str(index), str(count))
        sub_op_nd_name = constants.SUB_OP_ROOT_NODE_NAME.replace(
            "M_", "{}_".format(side)
        )
        sub_op_nd_name = sub_op_nd_name.replace("_op_0", instance)
        self.joint_control = curves.JointControl()
        sub_op_node = self.joint_control.create_curve(
            name=sub_op_nd_name,
            match=match,
            scale=scale,
            buffer_grp=False,
            color_index=self.SUB_ND_COLOR_INDEX,
        )[0]
        for attr_ in self.sub_node_param_list:
            attributes.add_attr(node=sub_op_node, **attr_)
        if local_rotate_axes:
            self.lra_op_attr = {
                "name": constants.SUB_OP_LRA_TAG_NAME,
                "attrType": "bool",
                "keyable": False,
                "defaultValue": 1,
            }
            rotate_axe_control = curves.RotateAxesControl()
            sub_lra_node = rotate_axe_control.create_curve(
                name=sub_op_nd_name.replace("CON", "LRA_CON"),
                match=sub_op_node,
                lock_translate=["tx", "ty", "tz"],
                lock_rotate=["rx", "ry", "rz"],
                lock_scale=["sx", "sy", "sz"],
                buffer_grp=True,
            )
            attributes.add_attr(sub_lra_node[1], **self.lra_op_attr)
            sub_op_node.addChild(sub_lra_node[0])
            self.sub_operators_lra_buffer.append(sub_lra_node[0])
            self.all_container_nodes.append(sub_lra_node[0])
            self.all_container_nodes.append(sub_lra_node[1])
        self.sub_meta_nd = meta.SubOpMetaNode(
            n=sub_op_nd_name.replace("_CON", "")
        )
        self.main_meta_nd.add_sub_meta_node(node=self.sub_meta_nd)
        # Section to set meta data connections.
        self.sub_meta_nd.set_operator_nd(sub_op_node)
        self.sub_meta_nd.message.connect(
            sub_op_node.attr(constants.SUB_OP_META_ND_ATTR_NAME)
        )
        if self.main_op_nd:
            self.sub_meta_nd.set_main_op_nd(self.main_op_nd)
        if self.root_meta_nd:
            self.root_meta_nd.message.connect(
                sub_op_node.attr(constants.ROOT_OP_META_ND_ATTR_NAME)
            )
        self.sub_operators.append(sub_op_node)
        self.linear_curve_drivers.append(sub_op_node)
        self.sub_meta_nd.set_ws_output_index(count + 1)

    def create_component_op_node(
        self,
        name,
        side=constants.DEFAULT_SIDE,
        axes=constants.DEFAULT_AXES,
        index=constants.DEFAULT_INDEX,
        sub_operators_count=constants.DEFAULT_SUB_OPERATORS_COUNT,
        sub_operators_scale=constants.DEFAULT_SUB_OPERATORS_SCALE,
        local_rotate_axes=True,
        parent=None,
        sub_operators_local_rotate_axes=False,
    ):
        """
        Init the operators creation.

        Args:
            name(str): Operators name.
            side(str): Operators side. Valid are M,L,R
            axes(str): Operators creation axe. Valid are X,Y,Z-X,-Y,-Z
            index(int): Operators index.
            sub_operators_count(int): Sub operators count.
            sub_operators_scale(int): Sub operators node scale factor.
            local_rotate_axes(bool): Enable local rotate axes.
            parent(pmc.PyNode()): The parent node.
            sub_operators_local_rotate_axes(bool): Enable the local rotate
            axes for the sub_operators.

        """
        # Check at start if a parent node is passed. If it is not a valid not
        # method will break.
        if parent:
            if valid_node(parent, "JoMRS_root"):
                pass
            elif valid_node(parent, "JoMRS_main"):
                self.parent = parent
                self.parent_main_op_nd = parent
                self.get_root_meta_nd_from_main_op_nd(self.parent_main_op_nd)
                self.get_root_nd_from_root_meta_nd()
            elif valid_node(parent, "JoMRS_sub"):
                self.parent = parent
                self.parent_main_op_nd = self.get_main_op_node_from_sub(parent)
                self.get_root_meta_nd_from_main_op_nd(self.parent_main_op_nd)
                self.get_root_nd_from_root_meta_nd()
            else:
                logger.log(
                    level="error",
                    message="Parent node is not a JoMRS node.",
                    logger=_LOGGER,
                )
                return
        # Bypass axes for later refactoring.
        vec = constants.DEFAULT_SPACING
        axes_ = axes
        aim_vec = None
        up_vec = None
        name = strings.normalize_string(name, _LOGGER)
        self.main_op_nd_name = (
            constants.MAIN_OP_ROOT_NODE_NAME.replace("M_", "{}_".format(side))
            .replace("_op_", "_op_{}_".format(name))
            .replace("_0_", "_{}_".format(str(index)))
        )
        self.main_meta_nd_name = self.main_op_nd_name.replace("_CON", "")
        # Create the actual main operator node.
        self.create_main_op_node(local_rotate_axes=local_rotate_axes)
        # Check if a root operator node is passed and valid.
        # If not create a new root operator node.
        if not self.op_root_nd:
            self.create_root_op_node()
        # Set meta data.
        self.set_root_meta_nd()
        self.set_component_side(side)
        self.set_component_name(name)
        self.set_component_index(index)
        # Add main meta node to god meta node.
        self.add_node_to_god_meta_nd(self.main_op_nd)
        if sub_operators_count:
            # clear self.sub_operators list for safety.
            del self.sub_operators[:]
            # add the main_op_nd as first linear curve driver.
            self.linear_curve_drivers.append(self.main_op_nd)
            # remap the vector to move each sub operator in a minus axes
            if axes == "-X" or axes == "-Y" or axes == "-Z":
                vec = vec * -1
            if axes == "-X":
                axes_ = "X"
            elif axes == "-Y":
                axes_ = "Y"
            elif axes == "-Z":
                axes_ = "Z"
            # create the sub operators by count
            for count in range(sub_operators_count):
                self.create_sub_operator(
                    name,
                    side,
                    index,
                    count,
                    sub_operators_scale,
                    self.main_op_nd,
                    sub_operators_local_rotate_axes,
                )
            # parent the first sub op to the main op because the first sub op is
            # always the master for each sub op.
            self.main_op_nd.addChild(self.sub_operators[0])
            # remap section for aim constraint setup for the lra node.
            if sub_operators_count > 1:
                # create the real sub op hierarchy
                # if more then 1 sub_op_nd needed.
                mayautils.create_hierarchy(self.sub_operators)
            # move each sub op for the same value.
            for sub in self.sub_operators:
                sub.attr("translate" + axes_).set(vec)
            if sub_operators_count:
                if axes == "X":
                    aim_vec = (1, 0, 0)
                    up_vec = (0, 1, 0)
                elif axes == "Y":
                    aim_vec = (0, 1, 0)
                    up_vec = (1, 0, 0)
                elif axes == "Z":
                    aim_vec = (0, 0, 1)
                    up_vec = (0, 1, 0)
                elif axes == "-X":
                    aim_vec = (-1, 0, 0)
                    up_vec = (0, 1, 0)
                elif axes == "-Y":
                    aim_vec = (0, -1, 0)
                    up_vec = (1, 0, 0)
                elif axes == "-Z":
                    aim_vec = (0, 0, -1)
                    up_vec = (0, 1, 0)
                # create the aim constraint name based on the lra node name.
                aim_con_name = "{}_CONST".format(str(self.lra_node_buffer_grp))
                aim_con = pmc.aimConstraint(
                    self.sub_operators[0],
                    self.lra_node_buffer_grp,
                    aim=aim_vec,
                    u=up_vec,
                    wut="object",
                    worldUpObject=self.main_op_nd,
                    mo=True,
                    n=aim_con_name,
                )
                # at the constraint to the container node list
                self.all_container_nodes.append(aim_con)
                # If sub operators local rotate axes enabled create the aim
                # constraint setup.
                if sub_operators_local_rotate_axes:
                    for index, sub_op_nd in enumerate(self.sub_operators):
                        try:
                            sub_aim_con_name = "{}_CONST".format(
                                self.sub_operators_lra_buffer[index].name()
                            )
                            sub_aim_con = pmc.aimConstraint(
                                self.sub_operators[index + 1],
                                self.sub_operators_lra_buffer[index],
                                aim=aim_vec,
                                u=up_vec,
                                wut="object",
                                worldUpObject=self.sub_operators[index],
                                mo=True,
                                n=sub_aim_con_name,
                            )
                            # at the constraint to the container node list
                            self.all_container_nodes.append(sub_aim_con)
                        except:
                            logger.log(
                                level="info",
                                message="Sub operators "
                                "lra node aim "
                                "setup "
                                "created.",
                                logger=_LOGGER,
                            )
            # linear curve section for visualisation purposes.
            linear_curve_name = constants.LINEAR_CURVE_NAME.replace(
                "M_", "{}_".format(side)
            )
            linear_curve_name = linear_curve_name.replace(
                "_op_", "_op_{}_".format(name)
            )
            linear_curve_name = linear_curve_name.replace(
                "_0_", "_{}_".format(str(index))
            )
            self.linear_curve = curves.linear_curve(
                driver_nodes=self.linear_curve_drivers, name=linear_curve_name
            )
            self.linear_curve.inheritsTransform.set(0)
            self.main_op_nd.addChild(self.linear_curve)
        # add the main operator node always to the root operator node.
        self.add_node(self.main_op_nd)
        # if valid parent is passed parent the new operator under the
        # specified parent node.
        if self.parent:
            # Parent new operator under selected JoMRS node.
            self.parent.addChild(self.main_op_nd)
            # Get ws output index and set it as parent ws output index.
            self.set_parent_ws_output_index(self.parent)
            # Set the parent meta nd.
            self.set_parent_nd(self.parent_main_op_nd)
            # move the created main_op_node to parent space.
            self.main_op_nd.translate.set(0, 0, 0)
            self.main_op_nd.rotate.set(0, 0, 0)
            self.main_op_nd.scale.set(1, 1, 1)
        # fill the all_container_nodes list.
        self.set_node_list()
        self.get_node_list()
        # Get sub operators lra nodes if enabled! This only can be done when
        # the node list is set!
        if sub_operators_local_rotate_axes:
            self.get_sub_lra_nodes()

    def set_component_type(self, type):
        """
        Set the Component type.

        Args:
                type(str): The Component type.

        """
        self.main_meta_nd.attr(constants.META_MAIN_COMP_TYPE).set(type)

    def set_component_name(self, name):
        """
        Set the Component name.

        Args:
                name(str): The Component name.

        """
        name = strings.normalize_string(name, _LOGGER)
        self.main_meta_nd.attr(constants.META_MAIN_COMP_NAME).set(name)

    def set_component_side(self, side):
        """
        Set the Component side.

        Args:
                side(str): The Component side.

        """
        self.main_meta_nd.attr(constants.META_MAIN_COMP_SIDE).set(side)

    def set_component_index(self, index):
        """
        Set the Component index.

        Args:
                index(int): The Component index.

        """
        self.main_meta_nd.attr(constants.META_MAIN_COMP_INDEX).set(index)

    def set_ik_spaces_ref(self, spaces):
        """
        Set the ik_spaces_reference nodes. Will fail if spaces attr is not list.

        Args:
                spaces(list): The references for the ik spaces.

        """
        if not isinstance(spaces, list):
            logger.log(
                "error", "Argument is no list", self.set_ik_spaces_ref, _LOGGER
            )
            return False
        self.main_meta_nd.attr(constants.META_MAIN_IK_SPACES).set(
            ";".join(spaces)
        )

    def set_connect_nd(self, node):
        """
        Set the element connect node for build process.

        Args:
                node(str): The connect nodes name.

        """
        self.main_meta_nd.attr(constants.META_MAIN_CONNECT_ND).set(node)

    def set_parent_nd(self, parent_main_operator_node):
        """
        Set the parent for the operator.

        Args:
            parent_main_operator_node(pmc.PyNode()): The main operator node
            of the parent.

        """
        parent_main_meta_nd = parent_main_operator_node.attr(
            constants.MAIN_OP_META_ND_ATTR_NAME
        ).get()
        parent_main_meta_nd.add_child_node(self.main_meta_nd)

    def set_parent_ws_output_index(self, parent_node):
        """
        Set parent ws output index from parent node ws output index.

        Args:
            parent_node(pmc.PyNode()): The parent node.

        """
        try:
            meta_node = parent_node.attr(
                constants.SUB_OP_META_ND_ATTR_NAME
            ).get()
        except:
            meta_node = parent_node.attr(
                constants.MAIN_OP_META_ND_ATTR_NAME
            ).get()
        self.main_meta_nd.set_parent_ws_output_index(
            meta_node.get_ws_output_index()
        )

    def set_node_list(self):
        """
        Connect all corresponding nodes of the main operator to
        the node list of the operator.
        """
        node_list = []
        node_list.extend(self.main_op_nd.getChildren(ad=True, typ="transform"))
        node_list.append(self.main_meta_nd)
        if self.sub_operators:
            for num in range(len(self.sub_operators)):
                node_list.append(
                    self.main_meta_nd.attr(
                        "{}_{}".format(constants.SUB_META_ND_PLUG, str(num))
                    ).get()
                )
        if self.linear_curve:
            node_list.extend(
                self.linear_curve.getShape().controlPoints.connections()
            )
        for node in node_list:
            attributes.connect_next_available(
                node, self.main_op_nd, "message", constants.NODE_LIST_ATTR_NAME
            )

    def set_cd_attributes(self):
        """
        Set the Component defined attributes data on meta node.
        """
        if self.cd_attributes:
            attributes = ";".join(self.cd_attributes)
            self.main_meta_nd.attr(constants.META_COMPONENT_DEFINED_ATTR).set(
                attributes
            )

    def set_connection_type(self, types):
        """
        Set the connection type.

        Args:
            types(list): List of strings.
            Valid values are ['translate', 'rotate', 'scale']

        """
        if not isinstance(types, list):
            logger.log(
                "error",
                "Argument is no list",
                self.set_connection_type,
                _LOGGER,
            )
            return False
        types = ";".join(types)
        self.main_meta_nd.attr(constants.META_MAIN_CONNECTION_TYPES).set(types)

    def get_component_type(self):
        """
        Get Component type.

        Return:
                string: Component type.

        """
        return self.main_meta_nd.attr(constants.META_MAIN_COMP_TYPE).get()

    def get_component_name(self):
        """
        Get Component name.

        Return:
                string: Component name.
        """
        return self.main_meta_nd.attr(constants.META_MAIN_COMP_NAME).get()

    def get_component_side(self):
        """
        Get Component side.

        Return:
                string: Component side.
        """
        return self.main_meta_nd.attr(constants.META_MAIN_COMP_SIDE).get()

    def get_component_index(self):
        """
        Get Component index.

        Return:
                string: Component side.
        """
        return self.main_meta_nd.attr(constants.META_MAIN_COMP_INDEX).get()

    def get_connect_nd(self):
        """
        Get connect node.

        Return:
                string: Component node.
        """
        return self.main_meta_nd.attr(constants.META_MAIN_CONNECT_ND).get()

    def get_ik_spaces_ref(self):
        """
        Get ik spaces.

        Return:
                string: Ik spaces.
        """
        return self.main_meta_nd.attr(constants.META_MAIN_IK_SPACES).get()

    def get_main_meta_node(self):
        """
        Get main meta node from main operator node.

        Return:
                pmc.PyNode(): The meta main node.

        """
        return self.main_op_nd.attr(constants.MAIN_OP_META_ND_ATTR_NAME).get()

    def get_parent_nd(self):
        """
        Get parent node form meta node.

        Return:
            pmc.PyNode(): The parent node.

        """
        return self.main_meta_nd.attr(constants.META_MAIN_PARENT_ND).get()

    def get_child_nd(self):
        """
        Get child node form meta node.

        Return:
            pmc.PyNode(): The child node.

        """
        return self.main_meta_nd.attr(constants.META_MAIN_CHILD_ND).get()

    @staticmethod
    def get_main_op_node_from_sub(sub_op_nd):
        """
        Get main op node from sub op node.

        Args:
            sub_op_nd(pmc.PyNode()):

        Return:
            pmc.PyNode(): The main op node

        """
        return (
            sub_op_nd.attr(constants.SUB_OP_META_ND_ATTR_NAME)
            .get()
            .attr(constants.MAIN_OP_MESSAGE_ATTR_NAME)
            .get()
        )

    def get_sub_op_nodes_from_main_op_nd(self):
        """
        Gives the corresponding sub operators from main_op_nd.
        """
        sub_op_nd = self.main_meta_nd.listAttr(ud=True)
        sub_op_nd = [
            sub_nd
            for sub_nd in sub_op_nd
            if re.search(constants.SUB_META_ND_PLUG, str(sub_nd))
        ]
        if sub_op_nd:
            result = [
                sub.get().attr(constants.SUB_OP_MESSAGE_ATTR_NAME).get()
                for sub in sub_op_nd
            ]
            self.sub_operators = result
            return result

    def get_main_op_ws_matrix(self):
        """
        Get the world matrix of the main_op_nd.

        Return:
            World Matrix object.

        """
        return self.main_op_nd.getMatrix(worldSpace=True)

    def get_lra_nd_ws_matrix(self):
        """
        Get the world matrix of the lra_nd.

        Return:
            World Matrix object.

        """
        return self.lra_node.getMatrix(worldSpace=True)

    def get_sub_op_nodes_ws_matrix(self):
        """
        Gives the world matrix for each sup_op_nd.

        Return:
            List: With the world matrix objects.

        """
        result = []
        if self.sub_operators:
            for sub_op in self.sub_operators:
                result.append(sub_op.getMatrix(worldSpace=True))
        return result

    def get_sub_lra_nd_ws_matrix(self):
        """
        Get the sub lra nodes ws matrix.

        Return:
             List: With the sub lra nd world matrix objects.

        """
        result = []
        if self.sub_lra_nodes:
            for sub_lra_nd in self.sub_lra_nodes:
                result.append(sub_lra_nd.getMatrix(worldSpace=True))
        return result

    def get_node_list(self):
        """
        Get all corresponding nodes from operator

        Return:
             List: All operator nodes.

        """
        self.all_container_nodes = []
        self.all_container_nodes.append(self.main_op_nd)
        self.all_container_nodes.extend(
            self.main_op_nd.attr(constants.NODE_LIST_ATTR_NAME).get()
        )
        return self.all_container_nodes

    def get_connection_types(self):
        """
        Get the connection types.

        Return:
             List: Types as string.
        """
        return (
            self.main_meta_nd.attr(constants.META_MAIN_CONNECTION_TYPES)
            .get()
            .split(";")
        )

    def get_cd_attributes(self):
        """
        Get the Component defined attribute.

        Return:
            List: Dictionary with attributes names and values.
        """
        result = dict()
        cd_attributes = (
            self.main_meta_nd.attr(constants.META_COMPONENT_DEFINED_ATTR)
            .get()
            .split(";")
        )
        for attr_ in cd_attributes:
            result[attr_] = self.main_meta_nd.attr(attr_).get()
        return result

    def get_lra_node(self):
        """
        Get the lra node.
        """
        for node in self.all_container_nodes:
            if (
                node.hasAttr(constants.OP_LRA_TAG_NAME)
                and node.attr(constants.OP_LRA_TAG_NAME).get() is True
            ):
                self.lra_node = node

    def get_sub_lra_nodes(self):
        """
        Get the sub lra nodes.
        """
        for node in self.all_container_nodes:
            if (
                node.hasAttr(constants.SUB_OP_LRA_TAG_NAME)
                and node.attr(constants.SUB_OP_LRA_TAG_NAME).get() is True
            ):
                self.sub_lra_nodes.append(node)

    def rename_operator_nodes(self, name):
        """
        Change operator and Component name. Search string is the Component
        name in the meta data.

        Args:
            name(str): String to replace.

        """
        name = strings.normalize_string(name, _LOGGER)
        component_name = self.get_component_name()
        search = "_{}_".format(component_name)
        replace = "_{}_".format(name)
        if component_name:
            for node in self.all_container_nodes:
                new_name = str(node).replace(search, replace)
                strings.string_checkup(new_name, _LOGGER)
                node.rename(new_name)
        self.set_component_name(name)

    def change_operator_side(self, side):
        """
        Change the operator side.

        Args:
            side(str): String to replace.

        """
        search = "^[MRL]_"
        replace = "{}_".format(side)
        for node in self.all_container_nodes:
            new_name = strings.regex_search_and_replace(
                str(node), search, replace
            )
            strings.string_checkup(new_name, _LOGGER)
            node.rename(new_name)
        self.set_component_side(side)

    def change_operator_index(self, index):
        """
        Change the operator index.

        Args:
            index(int): The index.

        """
        for node in self.all_container_nodes:
            new_name = strings.replace_index_numbers(str(node), index)
            strings.string_checkup(new_name, _LOGGER)
            node.rename(new_name)
        self.set_component_index(index)

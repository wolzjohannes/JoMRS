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
# Date:       2020 / 10 / 17

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

reload(meta)
reload(curves)
reload(strings)
reload(attributes)

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
        self.op_root_nd = operators_root_node
        # Check if node is a valid root node.
        if self.op_root_nd:
            if not valid_node(self.op_root_nd, typ="JoMRS_root"):
                self.op_root_nd = None
        self.god_meta_nd = None
        self.root_meta_nd = None
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
        self.op_root_nd = pmc.createNode("container", n=constants.OP_ROOT_NAME)
        icon = os.path.normpath(
            "{}/root_operator_logo.png".format(constants.ICONS_PATH)
        )
        self.op_root_nd.iconName.set(icon)
        for attr_ in self.op_root_nd_param_list:
            attributes.add_attr(node=self.op_root_nd, **attr_)
        # Create the meta node for the root node.
        self.root_meta_nd = meta.RootOpMetaNode(
            n=constants.ROOT_OP_META_NODE_NAME
        )
        # add root meta nd to container node.
        self.op_root_nd.addNode(self.root_meta_nd)
        # Connect root meta node with root node and visa versa.
        self.root_meta_nd.message.connect(
            self.op_root_nd.attr(constants.ROOT_OP_META_ND_ATTR_NAME)
        )
        self.root_meta_nd.set_root_op_nd(self.op_root_nd)

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
        attributes.add_attr(node=self.lra_node_buffer_grp, **self.lra_op_attr)
        for attr_ in self.main_node_param_list:
            attributes.add_attr(node=self.main_op_nd, **attr_)
        # Connect main operator node with main meta node.
        self.set_main_meta_nd()

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
    Create the whole component operator.
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
            Example without selection.
            >>> import operators
            >>> component_op.create_component_op_node('test', sub_operators_count=2)
            (2)
            Example with selection.
            >>> import pymel.core as pmc
            >>> import operators
            >>> selection = []
            >>> selection.extend(pmc.ls(sl=True, containers=True))
            >>> selection.extend(pmc.ls(sl=True, tr=True))
            >>> component_op = operators.ComponentOperator(selection[0],
            >>> selection[0], selection[0])
            >>> component_op.create_component_op_node('test', sub_operators_count=2)

        """
        MainOperatorNode.__init__(self, operators_root_node, main_operator_node)
        self.all_container_nodes = []
        self.sub_operators = []
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

    def create_sub_operator(self, name, side, index, count, scale, match):
        """
        Create the sub operators node.

        Args:
            name(str): Operators name.
            side(str): Side. Valid values are [L, R, M]
            index(int): Operators index.
            count(int): The sub_op_nd count.
            scale(float): Scale value.
            match(pmc.PyNode()): Object to snap for.

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
            parent(pmc.PyNode): The parent node.

        """
        # Check at start if a parent node is passed. If it is not a valid not
        # method will break.
        if parent:
            if valid_node(parent, "JoMRS_main"):
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
        else:
            self.get_root_meta_nd_from_op_root_nd()
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
            self.parent.addChild(self.main_op_nd)
            self.set_parent_nd(self.parent_main_op_nd)
        # fill the all_container_nodes list.
        self.set_node_list()
        self.get_node_list()

    def set_component_type(self, type):
        """
        Set the component type.

        Args:
                type(str): The component type.

        """
        self.main_meta_nd.attr(constants.META_MAIN_COMP_TYPE).set(type)

    def set_component_name(self, name):
        """
        Set the component name.

        Args:
                name(str): The component name.

        """
        name = strings.normalize_string(name, _LOGGER)
        self.main_meta_nd.attr(constants.META_MAIN_COMP_NAME).set(name)

    def set_component_side(self, side):
        """
        Set the component side.

        Args:
                side(str): The component side.

        """
        self.main_meta_nd.attr(constants.META_MAIN_COMP_SIDE).set(side)

    def set_component_index(self, index):
        """
        Set the component index.

        Args:
                index(int): The component index.

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
        Set the component defined attributes data on meta node.
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
        Get component type.

        Return:
                string: Component type.

        """
        return self.main_meta_nd.attr(constants.META_MAIN_COMP_TYPE).get()

    def get_component_name(self):
        """
        Get component name.

        Return:
                string: Component name.
        """
        return self.main_meta_nd.attr(constants.META_MAIN_COMP_NAME).get()

    def get_component_side(self):
        """
        Get component side.

        Return:
                string: Component side.
        """
        return self.main_meta_nd.attr(constants.META_MAIN_COMP_SIDE).get()

    def get_component_index(self):
        """
        Get component index.

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

    def get_sub_op_nodes_ws_matrix(self):
        """
        Gives the world matrix for each sup_op_nd.

        Return:
            List: With the world matrix objects.

        """
        result = []
        for sub_op in self.sub_operators:
            result.append(sub_op.getMatrix(worldSpace=True))
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
        Get the component defined attribute.

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

    def rename_operator_nodes(self, name):
        """
        Change operator and component name. Search string is the component
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

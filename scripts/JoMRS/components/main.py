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
# Date:       2021 / 01 / 03

"""
Rig components main module. This class is the template to create a rig
Component. Every rig Component should inherit this class as template.
"""
import os
import pymel.core as pmc
import strings
import attributes
import operators
import logger
import logging
import constants
import mayautils


##########################################################
# Methods
# init hierarchy
# input output management
# build process
# build steps. Example: layout rig. orient rig. ref nodes.
# all repedative things in a Component build.
# What are the repedative things:
# Build comp hierarchy and parent it under root hierarchy.
# Set and orient joints.
# Create fk, Drv and ik joints.
# Create rig logic.
# Create ref transforms.
# Create Controls.
# Connect input ud attributes with driven.
# Connect input was matrix with offset node.
# Connect output matrix.
# Connect ud attributes with output node.
# Create BND joints.
# Add entry in ref rig build class attr
##########################################################

##########################################################
# GLOBALS
##########################################################

_LOGGER = logging.getLogger(__name__ + ".py")

##########################################################
# FUNCTIONS
##########################################################


def selected():
    """
    Gets back a selected transform or container node.

    Returns:
       pmc.PyNode if successful. None if fail.

    """
    containers = pmc.ls(sl=True, containers=True)
    transforms = pmc.ls(sl=True, tr=True)
    if containers:
        return containers[0]
    if transforms:
        return transforms[0]
    return None


##########################################################
# CLASSES
##########################################################


class Component(operators.ComponentOperator):
    """
    Component template class.
    """

    def __init__(
        self,
        name=constants.DEFAULT_OPERATOR_NAME,
        component_type=constants.DEFAULT_COMPONENT_TYPE,
        side=constants.DEFAULT_SIDE,
        index=constants.DEFAULT_INDEX,
        operators_root_node=None,
        main_operator_node=None,
        sub_operator_node=None,
    ):
        """
        Init important data.

        Args:
            name(str, optional): Component name.
            component_type(str, optional): Component type.
            side(str, optional): The Component side.
            index(int, optional): The Component index.
            operators_root_node(pmc.PyNode(), optional): The operators root
            node.
            main_operator_node(pmc.PyNode(), optional): The main operator_node.
            sub_operator_node(pmc.PyNode(), optional)): The sub operator node.

        """
        operators.ComponentOperator.__init__(
            self, operators_root_node, main_operator_node, sub_operator_node
        )
        self.name = name
        self.component_type = component_type
        self.side = side
        self.index = index
        self.component_root = []
        self.component_rig_list = []
        self.bnd_output_matrix = []
        self.input_matrix_offset_grp = []
        self.output_matrix_nd_list = []
        self.controls = []
        self.operator_meta_data = {}
        self.rig_meta_data = {}

    def add_component_defined_attributes(self):
        """
        Method to implement extra ud attributes.
        """
        raise NotImplemented()

    def build_operator(
        self,
        axes,
        sub_operators_count,
        parent=None,
        local_rotate_axes=True,
        connect_node=None,
        ik_space_ref=None,
    ):
        """
        Build Component operator.

        Args:
            axes(str): The build axes. Valid is X, -X, Y, -Y, Z, -Z.
            sub_operators_count(int): Sub operators count.
            parent(pmc.PyNode): The parent node.
            connect_node(str): The connect node .
            ik_space_ref(list): Spaces given as nodes in a string
            local_rotate_axes(bool): Enable/Disable.

        """
        if not parent:
            parent = selected()
        self.create_component_op_node(
            name=self.name,
            side=self.side,
            index=self.index,
            axes=axes,
            sub_operators_count=sub_operators_count,
            local_rotate_axes=local_rotate_axes,
            parent=parent,
        )
        self.set_component_name(self.name)
        self.set_component_type(self.component_type)
        self.set_component_side(self.side)
        self.set_component_index(self.index)
        self.add_component_defined_attributes()
        self.set_cd_attributes()
        if connect_node:
            self.set_connect_nd(connect_node)
        if ik_space_ref:
            self.set_ik_spaces_ref(ik_space_ref)
        logger.log(
            level="info",
            message="{} Component operator "
            "build with the name: {}".format(self.component_type, self.name),
            logger=_LOGGER,
        )

    def get_operator_meta_data(self):
        """
        Collect the operators meta data.
        """
        self.operator_meta_data[
            constants.META_MAIN_OP_ND_WS_MATRIX_STR
        ] = self.get_main_op_ws_matrix()
        self.operator_meta_data[
            constants.META_SUB_OP_ND_WS_MATRIX_STR
        ] = self.get_sub_op_nodes_ws_matrix()
        self.operator_meta_data[
            constants.META_MAIN_COMP_NAME
        ] = self.get_component_name()
        self.operator_meta_data[
            constants.META_MAIN_COMP_TYPE
        ] = self.get_component_type()
        self.operator_meta_data[
            constants.META_MAIN_COMP_SIDE
        ] = self.get_component_side()
        self.operator_meta_data[
            constants.META_MAIN_COMP_INDEX
        ] = self.get_component_index()
        self.operator_meta_data[
            constants.META_MAIN_CONNECTION_TYPES
        ] = self.get_connection_types()
        self.operator_meta_data[
            constants.META_MAIN_IK_SPACES
        ] = self.get_ik_spaces_ref()
        self.operator_meta_data[
            constants.META_MAIN_CONNECT_ND
        ] = self.get_connect_nd()
        self.operator_meta_data[
            constants.META_MAIN_PARENT_ND
        ] = self.get_parent_nd()
        self.operator_meta_data[
            constants.META_MAIN_CHILD_ND
        ] = self.get_child_nd()
        self.operator_meta_data[
            constants.UUID_ATTR_NAME
        ] = self.main_meta_nd.get_uuid()
        self.operator_meta_data[
            constants.PARENT_OUTPUT_WS_PORT_INDEX
        ] = self.main_meta_nd.get_parent_ws_output_index()
        self.operator_meta_data.update(self.get_cd_attributes())

    def get_rig_meta_data(self):
        """
        Collect rig meta data.
        """
        self.rig_meta_data[
            constants.UUID_ATTR_NAME
        ] = self.root_meta_nd.get_uuid()
        self.rig_meta_data[constants.META_ROOT_RIG_NAME] = self.get_rig_name()
        self.rig_meta_data[
            constants.META_LEFT_RIG_COLOR
        ] = self.get_l_control_rig_color()
        self.rig_meta_data[
            constants.META_LEFT_RIG_SUB_COLOR
        ] = self.get_l_sub_control_rig_color()
        self.rig_meta_data[
            constants.META_RIGHT_RIG_COLOR
        ] = self.get_r_control_rig_color()
        self.rig_meta_data[
            constants.META_RIGHT_RIG_SUB_COLOR
        ] = self.get_r_sub_control_rig_color()
        self.rig_meta_data[
            constants.META_MID_RIG_COLOR
        ] = self.get_m_control_rig_color()
        self.rig_meta_data[
            constants.META_MID_RIG_SUB_COLOR
        ] = self.get_m_sub_control_rig_color()

    def create_component_container(self):
        """
        Init rig component container its contents..
        """
        self.component_root = CompContainer(
            self.operator_meta_data.get(constants.META_MAIN_COMP_NAME),
            self.operator_meta_data.get(constants.META_MAIN_COMP_SIDE),
            self.operator_meta_data.get(constants.META_MAIN_COMP_INDEX),
        )
        self.component_root.create_comp_container()
        # Refactor Main op uuid to comp uuid
        uuid_ = self.operator_meta_data.get(constants.UUID_ATTR_NAME)
        uuid_ = strings.search_and_replace(
            uuid_,
            constants.MAIN_OP_ND_UUID_SUFFIX,
            constants.COMP_CONTAINER_UUID_SUFFIX,
        )
        self.component_root.set_uuid(uuid_)
        logger.log(
            level="info",
            message="Component hierarchy setted up "
            "for: {} Component".format(
                self.operator_meta_data[constants.META_MAIN_COMP_NAME]
            ),
            logger=_LOGGER,
        )

    def create_input_ws_matrix_port(self, name):
        """
        Create a input port for ws matrix connection.

        Args:
            name(str): Name of the attribute.

        """
        attributes.add_attr(
            self.component_root.container_content.get("input"),
            name="{}_input_ws_matrix".format(name),
            attrType="matrix",
            keyable=False,
            hidden=True,
        )

    def create_input_os_matrix_port(self, name):
        """
        Create a input port for os matrix connection.

        Args:
            name(str): Name of the attribute.

        """
        attributes.add_attr(
            self.component_root.container_content.get("input"),
            name="{}_input_os_matrix".format(name),
            attrType="matrix",
            keyable=False,
            hidden=True,
        )

    def create_output_ws_matrix_port(self, name):
        """
        Create a output port for ws matrix connection.

        Args:
            name(str): Name of the attribute.

        """
        attributes.add_attr(
            self.component_root.container_content.get("output"),
            name="{}_output_ws_matrix".format(name),
            attrType="matrix",
            keyable=False,
            hidden=True,
        )

    def create_output_os_matrix_port(self, name):
        """
        Create a output port for os matrix connection.

        Args:
            name(str): Name of the attribute.

        """
        attributes.add_attr(
            self.component_root.container_content.get("output"),
            name="{}_output_os_matrix".format(name),
            attrType="matrix",
            keyable=False,
            hidden=True,
        )

    def add_ud_port(
        self,
        component_port="input",
        name=None,
        type_="float",
        minValue=0,
        maxValue=1,
        value=1,
    ):
        """
        Add user defined port to the input or output port of a rig Component.
        By Default it add a float value to the input port with a given
        name, with a min value of 0.0 a max value of 1.0 and a value of 1.0.

        Args:
            component_port(str): The rig components port.
            name(str): The port name.
            type_(str): The port typ.
            minValue(float or int): The minimal port value.
            maxValue(float or int): The maximum port value.
            value(float or int or str): The port value.

        """
        valid_ports = ["input", "output"]
        if component_port not in valid_ports:
            raise AttributeError(
                'Chosen port not valid. Valid values are ["input", "output"]'
            )
        node = self.component_root.container_content.get("input")
        if component_port == "output":
            node = self.component_root.container_content.get("output")

        attributes.add_attr(
            node=node,
            name=name,
            attrType=type_,
            minValue=minValue,
            maxValue=maxValue,
            value=value,
        )

    def build_component_logic(self):
        """
        Method for building a Component. Use the list variables
        self.component_rig_list, self.bnd_output_matrix,
        self.input_matrix_offset_grp to define input and output connections
        of the Component.
        """
        # Logger section for proper user feedback.
        logger.log(
            level="info",
            message="Component logic created "
            "for: {} Component".format(
                self.operator_meta_data[constants.META_MAIN_COMP_NAME]
            ),
            logger=_LOGGER,
        )
        return True

    def connect_inner_component_edges(self):
        """
        Method to connect the component rig content with the input and
        outputs of the component.
        """
        # connect every node in the bnd_output_matrix list as BND output in
        # the output node.
        for index, bnd_node in enumerate(self.bnd_output_matrix):
            bnd_node.worldMatrix[0].connect(
                self.component_root.container_content.get("output").attr(
                    "{}[{}]".format(
                        constants.BND_OUTPUT_WS_PORT_NAME, str(index)
                    )
                )
            )
        # connect every node in the input_matrix_offset_grp with the
        # input_ws_matrix_offset_nd attr on the meta nd. For further use to
        # connect the different components.
        if self.input_matrix_offset_grp:
            self.component_root.set_input_ws_matrix_offset_nd(
                self.input_matrix_offset_grp
            )
        # each node in the output_matrix_nd_list will be connected with
        # output_ws_matrix node of the component output nd.
        if self.output_matrix_nd_list:
            for index, output_nd in enumerate(self.output_matrix_nd_list):
                output_nd.worldMatrix[0].connect(
                    self.component_root.container_content.get("output").attr(
                        "{}[{}]".format(
                            constants.constants.OUTPUT_WS_PORT_NAME
                        ),
                        str(index),
                    )
                )
        # every node in the component rig list will be a child of the
        # component node.
        if self.component_rig_list:
            for node in self.component_rig_list:
                self.component_root.add_node_to_container_content(
                    node, "component"
                )
        # Clear lists for reuse!
        del self.bnd_output_matrix[:]
        del self.input_matrix_offset_grp[:]
        del self.component_rig_list[:]
        # Step feedback
        logger.log(
            level="info",
            message="Inner component edges connected "
            "for: {} Component".format(
                self.operator_meta_data[constants.META_MAIN_COMP_NAME]
            ),
            logger=_LOGGER,
        )

    def build_from_operator(self, operator_meta_data=None):
        """
        Build the whole Component rig from operator.
        With initial hierarchy.

        Args:
            operator_meta_data(dict): Operators meta data.

        """
        if not operator_meta_data:
            self.get_operator_meta_data()
        else:
            self.operator_meta_data = operator_meta_data
        self.create_component_container()
        self.build_component_logic()
        self.connect_inner_component_edges()


class CompContainer(mayautils.ContainerNode):
    """
    Create a container node designed for rig components..
    """

    CONTENT_GROUPS = ["input", "output", "component", "spaces"]

    def __init__(
        self,
        comp_name=None,
        comp_side=None,
        comp_index=0,
        component_container=None,
    ):
        """
        Args
            comp_name(str): The rig component name.
            comp_side(str): The component side.
            comp_index(int): The component index.
            component_container(pmc.PyNode()): A component container to pass.
        """
        mayautils.ContainerNode.__init__(self, content_root_node=True)
        self.name = "M_ROOT_name_component_0_GRP"
        self.meta_nd_name = constants.COMP_META_NODE_NAME
        self.icon = os.path.normpath(
            "{}/components_logo.png".format(constants.ICONS_PATH)
        )
        self.container = component_container
        if comp_name and comp_side:
            self.meta_nd_name = self.meta_nd_name.replace("COMP", comp_name)
            self.name = (
                self.name.replace("M", comp_side)
                .replace("name", comp_name)
                .replace("0", str(comp_index))
            )
            self.name = strings.string_checkup(self.name)
            self.container_content_root_name = self.container_content_root_name.replace(
                "M", comp_side
            ).replace(
                "content_root", "{}_content_root".format(comp_name)
            )

    def create_comp_container(self):
        """
        Create the component container.
        """
        self.create_container()
        self.create_container_content_from_list(self.CONTENT_GROUPS)
        attributes.add_attr(
            self.container_content.get("input"),
            name=constants.INPUT_WS_PORT_NAME,
            attrType="matrix",
            multi=True,
            keyable=False,
            hidden=True,
        )
        attributes.add_attr(
            self.container_content.get("output"),
            name=constants.OUTPUT_WS_PORT_NAME,
            attrType="matrix",
            multi=True,
            keyable=False,
            hidden=True,
        )
        attributes.add_attr(
            self.container_content.get("output"),
            name=constants.BND_OUTPUT_WS_PORT_NAME,
            attrType="matrix",
            multi=True,
            keyable=False,
            hidden=True,
        )

    def set_input_ws_matrix_offset_nd(self, offset_nd_list):
        """
        Connect a list of nodes with the input ws matrix nd port on the
        container meta nd

        Args:
            offset_nd_list(list): The node list to connect with the offset nd
            list port.

        """
        for index, node in enumerate(offset_nd_list):
            node.message.connect(
                self.meta_nd.attr(
                    "{}[{}]".format(
                        constants.INPUT_WS_MATRIX_OFFSET_ND, str(index)
                    )
                )
            )

    def get_input_ws_matrix_offset_nd(self):
        """
        Get the input ws matrix offset nd.

        Returns:
            List: All connected offset nodes
            
        """
        return self.meta_nd.attr(constants.INPUT_WS_MATRIX_OFFSET_ND).get()

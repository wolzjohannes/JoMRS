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
# Date:       2020 / 09 / 23

"""
Rig components main module. This class is the template to create a rig
component. Every rig component should inherit this class as template.
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

reload(constants)
reload(mayautils)
reload(operators)
reload(strings)

##########################################################
# Methods
# init hierarchy
# input output management
# build process
# build steps. Example: layout rig. orient rig. ref nodes.
# all repedative things in a component build.
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


class component(operators.ComponentOperator):
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
            side(str, optional): The component side.
            index(int, optional): The component index.
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
        self.input = []
        self.output = []
        self.component = []
        self.spaces = []
        self.component_rig_list = []
        self.bnd_output_matrix = []
        self.input_matrix_offset_grp = []
        self.controls = []
        if self.main_op_nd:
            self.drawn_name = self.get_component_name()
            self.drawn_component_type = self.get_component_type()
            self.drawn_side = self.get_component_side()
            self.drawn_index = self.get_component_index()

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
        Build component operator.

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
            parent=parent
        )
        self.set_component_name(self.name)
        self.set_component_type(self.component_type)
        self.set_component_side(self.side)
        self.set_component_index(self.index)
        if connect_node:
            self.set_connect_nd(connect_node)
        if ik_space_ref:
            self.set_ik_spaces_ref(ik_space_ref)
        logger.log(
            level="info",
            message="{} component operator "
            "build with the name: {}".format(self.component_type, self.name),
            logger=_LOGGER,
        )


    def init_component_hierarchy(self):
        """
        Init rig component base hierarchy.
        """
        component_root_name = "{}_ROOT_{}_component_0_GRP".format(
            self.drawn_side, self.drawn_name
        )
        component_root_name = strings.string_checkup(component_root_name)
        self.component_root = pmc.createNode("container", n=component_root_name)
        icon = os.path.normpath(
            "{}/components_logo.png".format(constants.ICONS_PATH)
        )
        self.component_root.iconName.set(icon)
        self.input = pmc.createNode("transform", n="input")
        self.output = pmc.createNode("transform", n="output")
        self.component = pmc.createNode("transform", n="component")
        self.spaces = pmc.createNode("transform", n="spaces")
        temp = [self.input, self.output, self.component, self.spaces]
        attributes.add_attr(
            self.input,
            name=constants.INPUT_WS_PORT_NAME,
            attrType="matrix",
            multi=True,
            keyable=False,
            hidden=True,
        )
        attributes.add_attr(
            self.output,
            name=constants.OUTPUT_WS_PORT_NAME,
            attrType="matrix",
            multi=True,
            keyable=False,
            hidden=True,
        )
        attributes.add_attr(
            self.output,
            name=constants.BND_OUTPUT_WS_PORT_NAME,
            attrType="matrix",
            multi=True,
            keyable=False,
            hidden=True,
        )
        for node in temp:
            self.component_root.addNode(node)

    def create_input_ws_matrix_port(self, name):
        """
        Create a input port for ws matrix connection.

        Args:
            name(str): Name of the attribute.

        """
        attributes.add_attr(
            self.input,
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
            self.input,
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
            self.output,
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
            self.output,
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
        Add user defined port to the input or output port of a rig component.
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
        node = self.input
        if component_port == "output":
            node = self.output

        attributes.add_attr(
            node=node,
            name=name,
            attrType=type_,
            minValue=minValue,
            maxValue=maxValue,
            value=value,
        )

    def build_component_logic(
        self, main_operator_ws_matrix=None, sub_operator_ws_matrix=None
    ):
        """
        Method for building a component. Use the list variables
        self.component_rig_list, self.bnd_output_matrix,
        self.input_matrix_offset_grp to define input and output connections
        of the component

        Args:
            main_operator_ws_matrix(matrix): World space position of main
            operator.
            sub_operator_ws_matrix(list): List of sub operators world space
            position.

        """
        return True

    def connect_component_edges(self):
        """
        Method to connect the input and output of a component.
        """
        for index, bnd_node in enumerate(self.bnd_output_matrix):
            bnd_node.worldMatrix[0].connect(
                self.output.attr(
                    "{}[{}]".format(
                        constants.BND_OUTPUT_WS_PORT_NAME, str(index)
                    )
                )
            )
        for index, input_node in enumerate(self.input_matrix_offset_grp):
            mayautils.decompose_matrix_constraint(
                source=input_node,
                target=self.input,
                target_plug="{}[{}]".format(
                    constants.INPUT_WS_PORT_NAME, str(index)
                ),
            )
        if self.component_rig_list:
            for node in self.component_rig_list:
                if self.component_root:
                    self.component_root.addNode(
                        node, ish=True, ihb=True, iha=True, inc=True
                    )
                    self.component.addChild(node)

    def build_from_operator(self):
        """
        Build the whole component rig from operator.
        With initial hierarchy.
        """
        self.init_component_hierarchy()
        self.build_component_logic()
        self.connect_component_edges()

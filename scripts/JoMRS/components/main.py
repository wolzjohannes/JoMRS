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
# Date:       2020 / 09 / 01

"""
Rig components main module. This class is the template to create a rig
component. Every rig component should inherit this class as template.
"""
import pymel.core as pmc
import strings
import attributes
import operators
import logger
import logging

reload(operators)

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
# CLASSES
##########################################################

class component(operators.create_component_operator):
    """
    Component template class.
    """

    def __init__(
        self,
        name=None,
        component_type=None,
        side=None,
        index=None,
        operators_root_node=None,
        main_operator_node=None,
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
            main_operator_node(pmc.PyNode(), optional): The
            operators_root_node.

        """
        operators.create_component_operator.__init__(self,
                                                     operators_root_node,
                                                     main_operator_node)
        self.name = name
        self.component_type = component_type
        self.side = side
        self.index = index
        self.component_root = []
        self.input = []
        self.output = []
        self.component = []
        self.spaces = []
        if main_operator_node:
            self.name = self.get_component_name()
            self.component_type = self.get_component_type()
            self.side = self.get_component_side()
            self.index = self.get_component_index()

    def build_operator(
        self,
        axes,
        sub_operators_count,
        local_rotate_axes=True,
        connect_node=None,
        ik_space_ref=None,
    ):
        """Build component operator.

        Args:
                axes(str): The build axes. Valid is X, -X, Y, -Y, Z, -Z.
                sub_operators_count(int): Sub operators count.
                connect_node(str): The connect node .
                ik_space_ref(list): Spaces given as nodes in a string
                local_rotate_axes(bool): Enable/Disable

        """
        self.create_component_op_node(
            name=self.name, side=self.side, axes=axes,
            sub_operators_count=sub_operators_count,
            local_rotate_axes=local_rotate_axes,
        )
        self.set_component_name(self.name)
        self.set_component_type(self.component_type)
        self.set_component_side(self.side)
        self.set_component_index(self.index)
        if connect_node:
            self.set_connect_nd(connect_node)
        if ik_space_ref:
            self.set_ik_spaces_ref(ik_space_ref)
        logger.log(level='info', message='{} component operator '
                                         'build with the name: {}'.format(
            self.component_type, self.name),
                   logger=_LOGGER)

    def init_hierarchy(self, component_root):
        """
        Init rig component base hierarchy.
        Args:
            component_root(dagnode): Component parent node.
        """
        component_root_name = "{}_RIG_{}_component_0_GRP".format(
            self.side, self.name.lower()
        )
        component_root_name = strings.string_checkup(component_root_name)
        self.component_root = pmc.createNode("transform", n=component_root_name)
        attributes.lock_and_hide_attributes(self.component_root)
        self.input = pmc.createNode("transform", n="input")
        self.output = pmc.createNode("transform", n="output")
        self.component = pmc.createNode("transform", n="component")
        self.spaces = pmc.createNode("transform", n="spaces")
        temp = [self.input, self.output, self.component, self.spaces]
        for node in temp:
            self.component_root.addChild(node)
            attributes.lock_and_hide_attributes(node)
        attributes.add_attr(
            self.input,
            name="input_ws_matrix",
            attrType="matrix",
            multi=True,
            keyable=False,
            hidden=True,
        )
        attributes.add_attr(
            self.output,
            name="output_ws_matrix",
            attrType="matrix",
            multi=True,
            keyable=False,
            hidden=True,
        )
        attributes.add_attr(
            self.output,
            name="BND_output_ws_matrix",
            attrType="matrix",
            multi=True,
            keyable=False,
            hidden=True,
        )
        if component_root:
            component_root.addChild(self.component_root)

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
        self,
        main_operator_ws_matrix=None,
        sub_operator_ws_matrix=None,
        joint_count=1,
    ):
        """
        Method for building a component.

        Args:
            main_operator_ws_matrix(matrix): World space position of main
            operator.
            sub_operator_ws_matrix(list): List of sub operators world space
            position.
            joint(int): Count of rig joints.

        Return:
            True

        """
        return True

    def build_from_operator(self, component_root=None):
        """
        Build the whole component rig from operator.
        With initial hierarchy.

        Args:
            component_root(pmc.PyNode()): The component root node.)
        """
        self.init_hierarchy(component_root)
        self.build_component_logic()

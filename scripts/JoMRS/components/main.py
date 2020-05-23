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
# Date:       2020 / 05 / 23

"""
Rig components main module. This class is the template to create a rig
component. Every rig component should inherit this class as template.
"""
import pymel.core as pmc
import logging
import logger
import strings
import attributes
import mayautils
import operators

reload(operators)

##########################################################
# GLOBALS
##########################################################

_LOGGER = logging.getLogger(__name__ + ".py")

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


class component(operators.create_component_operator):
    """
    Handles all component operations.
    """

    def __init__(self, main_operator_node=None):
        """
        Init of important data.

        Args:
                main_operator_node(pmc.PyNode(), optional): Operators main node.
        """
        operators.create_component_operator.__init__(self, main_operator_node)
        self.operator = main_operator_node
        self.component_root = []
        self.input = []
        self.output = []
        self.component = []
        self.spaces = []

    def build_operator(
        self,
        operator_name,
        comp_typ,
        side,
        axes,
        index,
        sub_operators_count,
        local_rotate_axes=True,
        connect_node=None,
        ik_space_ref=None,
    ):
        """Build component operator.

        Args:
                operator_name(str): The operator name.
                comp_typ(str): The component typ.
                side(str): The component side. Valid is L, R, M.
                axes(str): The build axes. Valid is X, -X, Y, -Y, Z, -Z.
                sub_operators_count(int): Sub operators count.
                index(int): The component index.
                connect_node(str): The connect node .
                ik_space_ref(list): Spaces given as nodes in a string
                local_rotate_axes(bool): Enable/Disable

        Return:
                Created component operator

        """
        self.operator = self.init_operator(
            operator_name=operator_name,
            sub_operators_count=sub_operators_count,
            axes=axes,
            local_rotate_axes=local_rotate_axes,
        )
        self.set_component_name(operator_name)
        self.set_component_type(comp_typ)
        self.set_component_side(side)
        self.set_component_index(index)
        if connect_node:
            self.set_connect_nd(connect_node)
        if ik_space_ref:
            self.set_ik_spaces_ref(ik_space_ref)
        return self.operator

    def init_hierarchy(self, component_name, side, parent):
        """
        Init rig component base hierarchy.
        Args:
                component_name(str): The Components name.
                side(str): Component Side.
                parent(dagnode): Component parent node.
        """
        component_root_name = "{}_RIG_{}_component_0_GRP".format(
            side, component_name.lower()
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
        if parent:
            parent.addChild(self.component_root)

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

    def build_from_operator(self, component_name, side, parent):
        """
        Build the component from operator. With initial hierarchy.
        """
        self.init_hierarchy(component_name, side, parent)
        self.build_rig()

    def build_rig(self):
        """
        Create the actual rig.
        """
        return True

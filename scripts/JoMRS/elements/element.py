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
# Date:       2020 / 01 / 10

"""
Rig elements main module. This class is the template to create a rig
element. This class should inherit later from each element main module.
"""
import pymel.core as pmc
import logger
import logging
import operators
import os
import strings
import attributes

##########################################################
# GLOBALS
##########################################################

module_logger = logging.getLogger(__name__ + ".py")
JOMRSVAR = os.environ["JoMRS"]
ELEMENTSPATH = "/scripts/JoMRS/elements"

##########################################################
# Methods
# init hierarchy
# input output management
# build process
# build steps. Example: layout rig. orient rig. ref nodes.
# all repedative things in a element build.
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
##########################################################


class build_rig_element(object):
    """
    Class as rig build template for each rig element.
    """

    def __init__(self):
        self.element_root = []
        self.input = []
        self.output = []
        self.element = []
        self.spaces = []

    def init_hierarchy(self, element_name, side, parent):
        """
        Init rig element base hierarchy.
        Args:
                element_name(str): The Elements name.
                side(str): Element Side.
                parent(dagnode): Element parent node.
        """
        element_root_name = "{}_RIG_{}_element_0_GRP".format(
            side, element_name.lower()
        )
        element_root_name = strings.string_checkup(element_root_name)
        self.element_root = pmc.createNode("transform", n=element_root_name)
        attributes.lock_and_hide_attributes(self.element_root)
        self.input = pmc.createNode("transform", n="input")
        self.output = pmc.createNode("transform", n="output")
        self.element = pmc.createNode("transform", n="element")
        self.spaces = pmc.createNode("transform", n="spaces")
        temp = [self.input, self.output, self.element, self.spaces]
        for node in temp:
            self.element_root.addChild(node)
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
            parent.addChild(self.element_root)

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
        element_port='input',
        name=None,
        typ="float",
        minValue=0,
        maxValue=1,
        value=1,
    ):
        """
        Add userdefinet port the input or output port of rig element.
        By Default it add a float value to the input port with a given
        name, with a 0 min value a 1 max value and 1 as value.
        Args:
                element_port(str): The rig elements port.
                name(str): The port name.
                type(str): The port typ.
                minValue(float or int): The minimal port value.
                max
        """
        if element_port == 'input':
            node = self.input
        elif element_port == 'output':
            node = self.output

        attributes.add_attr(
            node=node,
            name=name,
            attrType=typ,
            minValue=minValue,
            maxValue=maxValue,
            value=value,
        )

    def build_from_operator(self):
        """
        Build the element from operator. wikt all repetative steps.
        """
        pass

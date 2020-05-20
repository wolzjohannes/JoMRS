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
# Date:       2020 / 05 / 09

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
        self.fk_joints = []
        self.ik_joints = []
        self.drv_joints = []
        self.bnd_joints = []
        self.ref_transforms = []

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


# class template for rig component creation.
class build_component_rig(object):
    """
    Class as rig build template for each rig component.
    """

    def __init__(self):
        self.component_root = []
        self.input = []
        self.output = []
        self.component = []
        self.spaces = []
        self.fk_joints = []
        self.ik_joints = []
        self.drv_joints = []
        self.bnd_joints = []
        self.ref_transforms = []

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
        typ="float",
        minValue=0,
        maxValue=1,
        value=1,
    ):
        """
        Add userdefined port to the input or output port of a rig component.
        By Default it add a float value to the input port with a given
        name, with a min value of 0.0 a max value of 1.0 and a value of 1.0.
        Args:
                component_port(str): The rig components port.
                name(str): The port name.
                type(str): The port typ.
                minValue(float or int): The minimal port value.
                maxValue(float or int): The maximum port value.
                value(float or int or str): The port value.
        """
        if component_port == "input":
            node = self.input
        elif component_port == "output":
            node = self.output

        attributes.add_attr(
            node=node,
            name=name,
            attrType=typ,
            minValue=minValue,
            maxValue=maxValue,
            value=value,
        )

    def create_joint_by_data(self, matrix, side, name, typ, index):
        """
        Create a joint by data.
        Args:
                matrix(matrix): Matrix data to match.
                side(str): Joint side. Valid is M, R, L.
                name(str): Joint name.
                typ(str): Joint typ.
                index(int): The index number.
        Return:
                tuple: The create joint.
        """
        name = "{}_{}_{}_{}_JNT".format(side, typ, name, str(index))
        jnt = mayautils.create_joint(name=name, typ=typ, match_matrix=matrix)
        return jnt

    def create_joint_skeleton_by_data_dic(self, data_list):
        """
        Create a joint skeleton by a data dictonary.
        Args:
                data_list(list with dics): A List filled with dictonaries.
                Example: [{'matrix': [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]
                , [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]; 'side': 'M';
                name: 'Test'; 'typ': 'BND; 'index': 0}]
        """
        temp = []
        for data in data_dic:
            jnt = self.create_joint_by_data(
                data["matrix"],
                data["side"],
                data["name"],
                data["typ"],
                data["index"],
            )
            if data["typ"] == "FK":
                self.fk_joints.append(jnt)
            elif data["typ"] == "IK":
                self.ik_joints.append(jnt)
            elif data["typ"] == "DRV":
                self.drv_joints.append(jnt)
            elif data["typ"] == "BND":
                self.bnd_joints.append(jnt)
        mayautils.create_hierarchy(temp)

    def create_ref_transform(self, name, side, index, buffer_grp, match_matrix):
        """
        Create a reference transform.
        Args:
                name(str): Name for the ref node.
                side(str): The side. Valid is M, R, L.
                index(int): The index number.
                buffer_grp(bool): Enable buffer grp.
                match_matrix(matrix): The match matrix.
        Return:
                tuple: The new ref node.
        """
        name = "{}_REF_{}_{}_GRP".format(side, name, str(index))
        name = strings.string_checkup(name, logger_=_LOGGER)
        ref_trs = pmc.createNode("transform", n=name)
        if self.component:
            self.component.addChild(ref_trs)
        if match_matrix:
            ref_trs.setMatrix(match_matrix, worldSpace=True)
        if buffer_grp:
            mayautils.create_buffer_grp(node=ref_trs)
        return ref_trs

    def build_from_operator(self, component_name, side, parent):
        """
        Build the component from operator.
        """
        self.init_hierarchy(component_name, side, parent)
        self.build_rig()

    def build_rig(self):
        """
        Create the actual rig.
        """
        return False

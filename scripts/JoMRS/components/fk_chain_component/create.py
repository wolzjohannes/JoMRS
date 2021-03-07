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
# Date:       2021 / 03 / 07

"""
Build a fk chain component
"""

import pymel.core as pmc
import attributes
import constants
import curves
import components.main
import logging
import logger
import mayautils

reload(mayautils)

##########################################################
# GLOBALS
##########################################################

_LOGGER = logging.getLogger(__name__ + ".py")

##########################################################
# CLASSES
##########################################################


class MainCreate(components.main.Component):
    """
    Build a fk chain component with a optional aim setup.
    """

    COMP_TYPE = "fk_chain_component"
    LOCAL_ROTATION_AXES = True
    PARENT_AIM_ATTR = "parent_aim"
    PARENT_AIM_AXES_ATTR = "parent_aim_axes"

    def __init__(
        self,
        name,
        side=constants.DEFAULT_SIDE,
        axes=constants.DEFAULT_AXES,
        index=constants.DEFAULT_INDEX,
        sub_operators_count=constants.DEFAULT_SUB_OPERATORS_COUNT,
        operators_root_node=None,
        main_operator_node=None,
        sub_operator_node=None,
    ):
        """
        Init function.

        Args:
            name(str): Component name.
            side(str): Component side. Valid Values are:
            ['L', 'R', 'M']
            axes(str): Operators axes.
            index(int, optional): The Component index.
            sub_operators_count(int): Count of chain joints and sub operators.
            operators_root_node(pmc.PyNode(), optional): The operators root
            node.
            main_operator_node(pmc.PyNode(), optional): The main operator_node.
            sub_operator_node(pmc.PyNode(), optional)): The sub operator node.

        """
        components.main.Component.__init__(
            self,
            name,
            self.COMP_TYPE,
            side,
            index,
            operators_root_node,
            main_operator_node,
            sub_operator_node,
        )
        self.axes = axes
        self.sub_operators_count = sub_operators_count
        self.chain_control_name = ""
        self.main_chain_control = None
        self.sub_chain_controls = []

    def add_ud_attributes_to_operators_meta_nd(self):
        """
        Add Component specific attributes to operator.
        And fill the cd_attributes list for meta data.
        """
        parent_aim_attr = {
            "name": self.PARENT_AIM_ATTR,
            "attrType": "bool",
            "keyable": False,
            "channelBox": False,
        }
        parent_aim_axes = {
            "name": self.PARENT_AIM_AXES_ATTR,
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
        }
        # Add the attributes to the main_meta_nd of the operator.
        cd_attributes_list = [parent_aim_attr, parent_aim_axes]
        for attr_ in cd_attributes_list:
            attributes.add_attr(node=self.main_meta_nd, **attr_)
        # It is important to append all user defined attributes to this list.
        # So they are registered as meta data in the meta node.,
        # Please append the attributes name not the the attribute dict.
        cd_attributes_ref_list = [
            self.PARENT_AIM_ATTR,
            self.PARENT_AIM_AXES_ATTR,
        ]
        for reg_attr in cd_attributes_ref_list:
            self.cd_attributes.append(reg_attr)

    def _init_operator(self, parent=None):
        """
        Init the operator creation.
        """
        self.build_operator(
            self.axes,
            self.sub_operators_count,
            parent,
            self.LOCAL_ROTATION_AXES,
        )
        self.set_parent_aim_axes(self.axes)

    def create_aim_setup_(
        self,
        side,
        name,
        index,
        parent_aim_nd,
        aim_nd,
        count_,
        aim_axe,
        parent_nd,
        weight_attr,
    ):
        """
        Create the aim setup based on a angelBetween node setup.

        Args:
            side(str): Component side.
            name(str): Component name.
            index(int): Component index.
            parent_aim_nd(pmc.PyNode()): The parent of the aim node
            aim_nd(pmc.PyNode()): The node to aim for.
            count_(int): The setup count.
            aim_axe(str): The aim axes. Valid values are ['X', 'Y', 'Z']
            parent_nd(pmc.PyNode()): The setup parent node.
            weight_attr(pmc.Attribute()): The attribute which control the
            pairBlend weight.

        Returns:
            List: pmc.PyNode(): The aim ref node. pmc.PyNode(): The parent aim
            ref node.

        """
        aim_ref_nd = mayautils.create_ref_transform(
            name="{}_aim".format(name),
            side=side,
            index=index,
            count=count_,
            match_matrix=aim_nd.getMatrix(worldSpace=True),
        )
        aim_ref_buffer_nd = mayautils.create_ref_transform(
            name="{}_aim_buffer".format(name),
            side=side,
            index=index,
            count=count_,
            match_matrix=aim_nd.getMatrix(worldSpace=True),
        )
        parent_aim_length_ref_nd = mayautils.create_ref_transform(
            name="{}_aim_length_parent".format(name),
            side=side,
            index=index,
            count=count_,
            match_matrix=aim_nd.getMatrix(worldSpace=True),
        )
        parent_aim_ref_nd = mayautils.create_ref_transform(
            name="{}_aim_parent".format(name),
            side=side,
            index=index,
            count=count_,
            match_matrix=parent_aim_nd.getMatrix(worldSpace=True),
        )
        offset_aim_ref_nd = mayautils.create_ref_transform(
            name="{}_aim_offset".format(name),
            side=side,
            index=index,
            count=count_,
            match_matrix=parent_aim_nd.getMatrix(worldSpace=True),
        )
        mayautils.create_hierarchy(
            [offset_aim_ref_nd, parent_aim_ref_nd, parent_aim_length_ref_nd]
        )
        parent_aim_length_ref_nd.rotate.set(0, 0, 0)
        mayautils.create_hierarchy(
            [parent_aim_length_ref_nd, aim_ref_buffer_nd, aim_ref_nd]
        )
        parent_nd.addChild(offset_aim_ref_nd)
        mayautils.create_alternate_aim_constraint(
            aim_nd, parent_aim_ref_nd, aim_axe
        )
        distance_nd_name = (
            parent_aim_nd.name()
            .replace(name, "{}_aim".format(name))
            .replace("_CON", "_DISND")
        )
        distance_shape = pmc.createNode("distanceDimShape")
        distance_shape_trs = distance_shape.getTransform()
        distance_shape_trs.rename(distance_nd_name)
        distance_shape_trs.visibility.set(0)
        parent_nd_decomp_name = parent_aim_nd.name().replace("TRS", "DEMAND")
        parent_nd_decomp_name = parent_nd_decomp_name.replace("CON", "DEMAND")
        aim_nd_decomp_name = aim_nd.name().replace("CON", "DEMAND")
        parent_nd_decomp = pmc.createNode(
            "decomposeMatrix", n=parent_nd_decomp_name
        )
        aim_nd_decomp = pmc.createNode("decomposeMatrix", n=aim_nd_decomp_name)
        parent_nd.worldMatrix[0].connect(parent_nd_decomp.inputMatrix)
        aim_nd.worldMatrix[0].connect(aim_nd_decomp.inputMatrix)
        parent_nd_decomp.outputTranslate.connect(distance_shape.startPoint)
        aim_nd_decomp.outputTranslate.connect(distance_shape.endPoint)
        pair_blend_nd_name = parent_aim_nd.name().replace("TRS", "PABLND")
        pair_blend_nd_name = pair_blend_nd_name.replace("CON", "PABLND")
        pair_blend_nd = pmc.createNode("pairBlend", n=pair_blend_nd_name)
        pair_blend_nd.attr("inTranslate{}2".format(aim_axe)).set(
            distance_shape.distance.get()
        )
        distance_shape.distance.connect(
            pair_blend_nd.attr("inTranslate{}1".format(aim_axe))
        )
        pair_blend_nd.attr("outTranslate{}".format(aim_axe)).connect(
            parent_aim_length_ref_nd.attr("translate{}".format(aim_axe))
        )
        weight_attr.connect(pair_blend_nd.weight)
        return [aim_ref_nd, parent_aim_ref_nd]

    def build_component_logic(self):
        """
        Build Component logic. It is derivative method from parent class.
        """
        # Name reformatting.
        name = self.operator_meta_data.get(constants.META_MAIN_COMP_NAME)
        index = self.operator_meta_data.get(constants.META_MAIN_COMP_INDEX)
        side = self.operator_meta_data.get(constants.META_MAIN_COMP_SIDE)
        aim_axes = self.operator_meta_data.get(self.PARENT_AIM_AXES_ATTR)
        self.chain_control_name = "{}_{}_{}_0_CON".format(side, name, index)
        # Get match matrix from meta data.
        orig_lra_nd_match_matrix = self.operator_meta_data.get(
            constants.META_LRA_ND_WS_MATRIX_STR
        )
        orig_sub_op_match_matrix = self.operator_meta_data.get(
            constants.META_SUB_OP_ND_WS_MATRIX_STR
        )
        # normalize the match matrix in scale.
        lra_nd_tweaked_matrix = mayautils.matrix_normalize_scale(
            orig_lra_nd_match_matrix
        )
        sub_op_tweaked_matrix = [
            mayautils.matrix_normalize_scale(sub_matrix)
            for sub_matrix in orig_sub_op_match_matrix
        ]
        # Get control curve color from rig meta data.
        control_curve_color = self.get_control_curve_color_from_rig_meta_data(
            side, "control"
        )
        # Create the control curves.
        self.main_chain_control = curves.BoxControl().create_curve(
            name=self.chain_control_name,
            match=lra_nd_tweaked_matrix,
            scale=orig_lra_nd_match_matrix.scale * (4, 4, 4),
            color_index=control_curve_color,
            lock_visibility=True,
            lock_scale=True,
        )
        controls_curves_list = [self.main_chain_control[1]]
        # for length in the sup operators matrix generate the sub chain
        for index, sub_op_matrix in enumerate(orig_sub_op_match_matrix):
            sub_chain_control = curves.BoxControl().create_curve(
                name=self.chain_control_name.replace("0", str(index + 1)),
                match=sub_op_tweaked_matrix[index],
                scale=orig_lra_nd_match_matrix.scale * (4, 4, 4),
                color_index=control_curve_color,
                lock_visibility=True,
                lock_scale=True,
            )
            self.sub_chain_controls.append(sub_chain_control[1])
            controls_curves_list.append(sub_chain_control[1])
        # Parent controls as hierarchy.
        mayautils.create_hierarchy(
            nodes=controls_curves_list, include_parent=True
        )
        # Create offset grp.
        offset_grp = pmc.createNode(
            "transform", n="{}_offset_0_GRP".format(self.chain_control_name)
        )
        offset_grp.addChild(self.main_chain_control[0])
        # If parent_aim enabled.
        if self.operator_meta_data.get(self.PARENT_AIM_ATTR):
            parent_aim_attr = {
                "name": self.PARENT_AIM_ATTR,
                "attrType": "float",
                "keyable": True,
                "channelBox": True,
                "minValue": 0,
                "maxValue": 1,
            }
            for sub_control_curve in self.sub_chain_controls:
                attributes.add_attr(sub_control_curve, **parent_aim_attr)
            aim_ref = self.create_aim_setup_(
                side,
                name,
                index,
                self.main_chain_control[1],
                self.sub_chain_controls[0],
                0,
                aim_axes,
                self.main_chain_control[1],
                self.sub_chain_controls[0].attr(self.PARENT_AIM_ATTR),
            )
            self.output_matrix_nd_list.append(aim_ref[1])
            self.bnd_output_matrix.append(aim_ref[1])
            temp = aim_ref[0]
            for count, sub_control_curve in enumerate(self.sub_chain_controls):
                count = count + 1
                try:
                    aim_ref_ = self.create_aim_setup_(
                        side,
                        name,
                        index,
                        sub_control_curve,
                        self.sub_chain_controls[count],
                        count,
                        aim_axes,
                        temp,
                        self.sub_chain_controls[count].attr(
                            self.PARENT_AIM_ATTR
                        ),
                    )
                    self.output_matrix_nd_list.append(aim_ref_[1])
                    self.bnd_output_matrix.append(aim_ref_[1])
                    temp = aim_ref_[0]
                except:
                    logger.log(
                        level="info",
                        message="Component: {} / Name: {"
                        "} / aim setup "
                        "created.".format(self.COMP_TYPE, name),
                        logger=_LOGGER,
                    )
        # At objects to output class lists.
        for control_curve in controls_curves_list:
            self.controls.append(control_curve)
        self.output_matrix_nd_list.append(temp)
        self.bnd_output_matrix.append(temp)
        self.component_rig_list.append(offset_grp)
        self.input_matrix_offset_grp.append(offset_grp)
        logger.log(
            level="info",
            message="Component logic created "
            "for: {} Component".format(
                self.operator_meta_data[constants.META_MAIN_COMP_NAME]
            ),
            logger=_LOGGER,
        )

    def set_parent_aim(self, value):
        """
        Enable/Disable the parent aim setup.

        Args:
            value(bool): Enable/Disable the parent aim setup creation.

        """
        self.main_meta_nd.attr(self.PARENT_AIM_ATTR).set(value)

    def set_parent_aim_axes(self, axe):
        """
        Set parent aim axes.

        Args:
            axe(str): The aim axe.

        """
        self.main_meta_nd.attr(self.PARENT_AIM_AXES_ATTR).set(axe)

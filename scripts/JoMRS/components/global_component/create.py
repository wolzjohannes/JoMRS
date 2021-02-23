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
# Date:       2021 / 02 / 22

"""
Build a global control component
"""

import pymel.core as pmc
import attributes
import constants
import curves
import components.main
import logging
import logger
import mayautils

reload(curves)
reload(components.main)
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
    Build a global control component with a COP control.
    """

    NAME = "global"
    SIDE = "M"
    COMP_TYPE = "global_control_component"
    SUB_OPERATORS_COUNT = 1
    LOCAL_ROTATION_AXES = True
    AXES = "Y"
    BND_JNT_ATTR_NAME = "bnd_joint"
    WS_ORIENTATION_ATTR_NAME = "worldspace_orientation"

    def __init__(
        self,
        index=constants.DEFAULT_INDEX,
        operators_root_node=None,
        main_operator_node=None,
        sub_operator_node=None,
    ):
        """
        Init function.

        Args:
            index(int, optional): The Component index.
            operators_root_node(pmc.PyNode(), optional): The operators root
            node.
            main_operator_node(pmc.PyNode(), optional): The main operator_node.
            sub_operator_node(pmc.PyNode(), optional)): The sub operator node.

        """
        components.main.Component.__init__(
            self,
            self.NAME,
            self.COMP_TYPE,
            self.SIDE,
            index,
            operators_root_node,
            main_operator_node,
            sub_operator_node,
        )

    def add_component_defined_attributes(self):
        """
        Add Component specific attributes to operator.
        And fill the cd_attributes list for meta data.
        """
        self.bnd_joint = {
            "name": self.BND_JNT_ATTR_NAME,
            "attrType": "bool",
            "keyable": False,
            "channelBox": False,
        }
        self.world_space_orientation_attr = {
            "name": self.WS_ORIENTATION_ATTR_NAME,
            "attrType": "bool",
            "keyable": False,
            "channelBox": False,
            "defaultValue": True,
        }
        # Add the attributes to the main_meta_nd of the operator.
        cd_attributes_list = [self.bnd_joint, self.world_space_orientation_attr]
        for attr_ in cd_attributes_list:
            attributes.add_attr(node=self.main_meta_nd, **attr_)
        # It is important to append all user defined attributes to this list.
        # So they are registered as meta data in the meta node.,
        # Please append the attributes name not the the attribute dict.
        cd_attributes_ref_list = [
            self.BND_JNT_ATTR_NAME,
            self.WS_ORIENTATION_ATTR_NAME,
        ]
        for reg_attr in cd_attributes_ref_list:
            self.cd_attributes.append(reg_attr)

    def _init_operator(self, parent=None):
        """
        Init the operator creation.
        """
        self.build_operator(
            self.AXES,
            self.SUB_OPERATORS_COUNT,
            parent,
            self.LOCAL_ROTATION_AXES,
        )

    def build_component_logic(self):
        """
        Build Component logic. It is derivative method from parent class.
        """
        # Name reformatting.
        index = self.operator_meta_data.get(constants.META_MAIN_COMP_INDEX)
        side = self.operator_meta_data.get(constants.META_MAIN_COMP_SIDE)
        global_control_name = "{}_global_{}_CON".format(side, str(index))
        local_control_name = "{}_local_{}_CON".format(side, str(index))
        cop_control_name = "{}_COP_{}_CON".format(side, str(index))
        cop_offset_name = "{}_COP_{}_offset_CON".format(side, str(index))
        # Get match matrix from meta data.
        orig_main_op_match_matrix = self.operator_meta_data.get(
            constants.META_MAIN_OP_ND_WS_MATRIX_STR
        )
        orig_sub_op_match_matrix = self.operator_meta_data.get(
            constants.META_SUB_OP_ND_WS_MATRIX_STR
        )[0]
        # normalize the match matrix in scale.
        main_op_tweaked_matrix = mayautils.matrix_normalize_scale(
            orig_main_op_match_matrix
        )
        sub_op_tweaked_matrix = mayautils.matrix_normalize_scale(
            orig_sub_op_match_matrix
        )
        # average the sub_op_nd ws matrix scale.
        scale_x, scale_y, scale_z = orig_main_op_match_matrix.scale
        sub_op_ws_matrix_scale_avg = (scale_x + scale_y + scale_z) / 3
        # Get world space bool in meta data.
        worldspace_orientation = self.operator_meta_data.get(
            self.WS_ORIENTATION_ATTR_NAME
        )
        # Reset the matrix in rotation.
        if worldspace_orientation:
            main_op_tweaked_matrix = mayautils.matrix_reset_rotation(
                main_op_tweaked_matrix
            )
        # Get bnd jnt creation bool in meta data.
        bnd_jnt_creation = self.operator_meta_data.get(self.BND_JNT_ATTR_NAME)
        # Get control curve color from rig meta data.
        control_curve_color = self.get_control_curve_color_from_rig_meta_data(
            side, "control"
        )
        sub_control_curve_color = self.get_control_curve_color_from_rig_meta_data(
            side, "sub_control"
        )
        # Create the control curves.
        global_control_curve = curves.TransformControl().create_curve(
            name=global_control_name,
            match=main_op_tweaked_matrix,
            scale=orig_main_op_match_matrix.scale * (2, 2, 2),
            color_index=control_curve_color,
            lock_visibility=True,
            lock_scale=True,
        )
        local_control_curve = curves.SquareControl().create_curve(
            name=local_control_name,
            match=main_op_tweaked_matrix,
            scale=orig_main_op_match_matrix.scale * (1.95, 1.95, 1.95),
            color_index=sub_control_curve_color,
            lock_visibility=True,
            lock_scale=True,
        )
        cop_offset_control_curve = curves.PyramideControl().create_curve(
            name=cop_offset_name,
            match=sub_op_tweaked_matrix,
            scale=orig_sub_op_match_matrix.scale * (1.5, 1.5, 1.5),
            color_index=control_curve_color,
            lock_visibility=True,
            lock_scale=True,
            move=[0, 0, -5 * sub_op_ws_matrix_scale_avg],
        )
        cop_control_curve = curves.PyramideControl().create_curve(
            name=cop_control_name,
            match=sub_op_tweaked_matrix,
            scale=orig_sub_op_match_matrix.scale,
            color_index=sub_control_curve_color,
            lock_visibility=True,
            lock_scale=True,
            move=[0, 0, -5 * sub_op_ws_matrix_scale_avg],
        )
        controls_curves_list = [
            global_control_curve[1],
            local_control_curve[1],
            cop_offset_control_curve[1],
            cop_control_curve[1],
        ]
        # Create offset grp.
        offset_grp = pmc.createNode(
            "transform", n="{}_offset_GRP".format(global_control_name)
        )
        # Parent controls as hierarchy.
        mayautils.create_hierarchy(
            nodes=controls_curves_list, include_parent=True
        )
        # At control to offset group.
        offset_grp.addChild(global_control_curve[0])
        # At objects to output class lists.
        for control_curve in controls_curves_list:
            self.controls.append(control_curve)
        for control_curve in [local_control_curve[1], cop_control_curve[1]]:
            self.output_matrix_nd_list.append(control_curve)
            if bnd_jnt_creation:
                self.bnd_output_matrix.append(control_curve)
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

    def set_worldspace_orientation(self, value):
        """
        Set the control to worldspace orientation.

        Args:
            value(bool): Set the control to worldspace orientation.

        """
        self.main_meta_nd.attr(self.WS_ORIENTATION_ATTR_NAME).set(value)

    def set_bnd_joint_creation(self, value=True):
        """
        Enable/Disable the bind joint creation.

        Args:
            value(bool): Enable/Disable the bnd joint creation.

        """
        self.main_meta_nd.attr(self.BND_JNT_ATTR_NAME).set(value)

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
# Date:       2021 / 03 / 01

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
from components.global_component.callbacks import ChangePivotCallback
from components.global_component.callbacks import (
    BEFORE_CHANGE_PIV_SCRIPT_NODE_STR,
)

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
    CHANGE_PIVOT_ATTR = "change_pivot"
    RESET_PIVOT_ATTR = "reset_pivot"
    CHANGE_PIVOT_CONTROL_CURVE = "change_pivot_control"
    CHANGE_PIVOT_TSR_REF_META_ATTR = "change_pivot_tsr"
    RESET_PIVOT_TSR_REF_META_ATTR = "reset_pivot_tsr"
    LOCAL_CON_REF_META_ATTR = "local_control"
    COP_CONTROL_CURVE = "cop_control_curve"

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
        self.global_control_name = ""
        self.local_control_name = ""
        self.change_pivot_name = ""
        self.reset_pivot_tsr_name = ""
        self.change_pivot_tsr_name = ""
        self.cop_control_name = ""
        self.cop_offset_name = ""
        self.global_control_curve = None
        self.local_control_curve = None
        self.change_pivot_control_curve = None
        self.cop_offset_control_curve = None
        self.cop_control_curve = None

    def add_ud_attributes_to_operators_meta_nd(self):
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

    def add_ud_attributes_to_comp_container_meta_nd(self):
        # Define custom attributes for comp container meta nd.
        change_pivot_control_attr = {
            "name": self.CHANGE_PIVOT_CONTROL_CURVE,
            "attrType": "message",
            "keyable": False,
            "channelBox": False,
        }
        local_control_ref_attr = {
            "name": self.LOCAL_CON_REF_META_ATTR,
            "attrType": "message",
            "keyable": False,
            "channelBox": False,
        }
        change_pivot_attr = {
            "name": self.CHANGE_PIVOT_ATTR,
            "attrType": "bool",
            "keyable": False,
            "channelBox": False,
        }
        reset_pivot_attr = {
            "name": self.RESET_PIVOT_ATTR,
            "attrType": "bool",
            "keyable": False,
            "channelBox": False,
        }
        change_pivot_ref_tsr_attr = {
            "name": self.CHANGE_PIVOT_TSR_REF_META_ATTR,
            "attrType": "message",
            "keyable": False,
            "channelBox": False,
        }
        reset_pivot_ref_tsr_attr = {
            "name": self.RESET_PIVOT_TSR_REF_META_ATTR,
            "attrType": "message",
            "keyable": False,
            "channelBox": False,
        }
        cop_control_curve_attr = {
            "name": self.COP_CONTROL_CURVE,
            "attrType": "message",
            "keyable": False,
            "channelBox": False,
        }
        container_meta_nd_ud_attr_list = [
            local_control_ref_attr,
            change_pivot_control_attr,
            change_pivot_attr,
            reset_pivot_attr,
            change_pivot_ref_tsr_attr,
            reset_pivot_ref_tsr_attr,
            cop_control_curve_attr,
        ]
        for attr_ in container_meta_nd_ud_attr_list:
            attributes.add_attr(self.component_root.meta_nd, **attr_)

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
        self.global_control_name = "{}_global_{}_CON".format(side, str(index))
        self.local_control_name = "{}_local_{}_CON".format(side, str(index))
        self.change_pivot_name = "{}_cop_change_pivot_{}_CON".format(
            side, str(index)
        )
        self.reset_pivot_tsr_name = "{}_cop_reset_pivot_{}_TRS".format(
            side, str(index)
        )
        self.change_pivot_tsr_name = "{}_cop_change_pivot_{}_TRS".format(
            side, str(index)
        )
        self.cop_control_name = "{}_cop_{}_CON".format(side, str(index))
        self.cop_offset_name = "{}_cop_offset_{}_CON".format(side, str(index))
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
        # average the sub_op_nd ws matrix scale. We will need it to multiply
        # the z axes move of the control cv from the cop control curve.
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
        self.global_control_curve = curves.TransformControl().create_curve(
            name=self.global_control_name,
            match=main_op_tweaked_matrix,
            scale=orig_main_op_match_matrix.scale * (2, 2, 2),
            color_index=control_curve_color,
            lock_visibility=True,
            lock_scale=True,
        )
        self.local_control_curve = curves.SquareControl().create_curve(
            name=self.local_control_name,
            match=main_op_tweaked_matrix,
            scale=orig_main_op_match_matrix.scale * (1.95, 1.95, 1.95),
            color_index=sub_control_curve_color,
            lock_visibility=True,
            lock_scale=True,
        )
        self.change_pivot_control_curve = curves.LocatorControl().create_curve(
            name=self.change_pivot_name,
            match=sub_op_tweaked_matrix,
            scale=orig_sub_op_match_matrix.scale,
            color_index=sub_control_curve_color,
            lock_visibility=True,
            lock_scale=True,
            move=[0, 0, -5 * sub_op_ws_matrix_scale_avg],
        )
        self.cop_offset_control_curve = curves.PyramideControl().create_curve(
            name=self.cop_offset_name,
            match=sub_op_tweaked_matrix,
            scale=orig_sub_op_match_matrix.scale * (1.5, 1.5, 1.5),
            color_index=control_curve_color,
            lock_visibility=True,
            lock_scale=True,
            move=[0, 0, -5 * sub_op_ws_matrix_scale_avg],
        )
        self.cop_control_curve = curves.PyramideControl().create_curve(
            name=self.cop_control_name,
            match=sub_op_tweaked_matrix,
            scale=orig_sub_op_match_matrix.scale,
            color_index=sub_control_curve_color,
            lock_visibility=True,
            lock_scale=True,
            move=[0, 0, -5 * sub_op_ws_matrix_scale_avg],
        )
        controls_curves_list = [
            self.global_control_curve[1],
            self.local_control_curve[1],
            self.change_pivot_control_curve[1],
            self.cop_offset_control_curve[1],
            self.cop_control_curve[1],
        ]
        # Create offset grp.
        offset_grp = pmc.createNode(
            "transform", n="{}_offset_GRP".format(self.global_control_name)
        )
        # Connect cop control curve with the comp container meta_nd.
        self.cop_control_curve[1].message.connect(
            self.component_root.meta_nd.attr(self.COP_CONTROL_CURVE)
        )
        # Connect the change pivot control curve with the comp container meta_nd.
        self.change_pivot_control_curve[1].message.connect(
            self.component_root.meta_nd.attr(self.CHANGE_PIVOT_CONTROL_CURVE)
        )
        # Connect local control with the comp container meta_nd.
        self.local_control_curve[1].message.connect(
            self.component_root.meta_nd.attr(self.LOCAL_CON_REF_META_ATTR)
        )
        # Change Pivot transform node.
        change_pivot_trs = pmc.createNode("transform",
                                          n=self.change_pivot_tsr_name)
        change_pivot_trs.setMatrix(sub_op_tweaked_matrix, worldSpace=True)
        self.cop_control_curve[1].addChild(change_pivot_trs)
        change_pivot_trs.message.connect(
            self.component_root.meta_nd.attr(
                self.CHANGE_PIVOT_TSR_REF_META_ATTR
            )
        )
        # Reset Pivot transform node.
        reset_pivot_trs = pmc.createNode("transform",
                                         n=self.reset_pivot_tsr_name)
        reset_pivot_trs.setMatrix(sub_op_tweaked_matrix, worldSpace=True)
        self.local_control_curve[1].addChild(reset_pivot_trs)
        reset_pivot_trs.message.connect(
            self.component_root.meta_nd.attr(self.RESET_PIVOT_TSR_REF_META_ATTR)
        )
        # Add reset / change pivot attr to cop offset control.
        change_pivot_attr = {
            "name": self.CHANGE_PIVOT_ATTR,
            "attrType": "bool",
            "keyable": True,
            "channelBox": True,
        }
        reset_pivot_attr = {
            "name": self.RESET_PIVOT_ATTR,
            "attrType": "bool",
            "keyable": True,
            "channelBox": True,
        }
        attributes.add_attr(self.change_pivot_control_curve[1],
                            **change_pivot_attr)
        attributes.add_attr(self.change_pivot_control_curve[1],
                            **reset_pivot_attr)
        # Connect reset / change pivot attr to comp container meta_nd.
        self.change_pivot_control_curve[1].attr(self.CHANGE_PIVOT_ATTR).connect(
            self.component_root.meta_nd.attr(self.CHANGE_PIVOT_ATTR)
        )
        self.change_pivot_control_curve[1].attr(self.RESET_PIVOT_ATTR).connect(
            self.component_root.meta_nd.attr(self.RESET_PIVOT_ATTR)
        )
        # Parent controls as hierarchy.
        mayautils.create_hierarchy(
            nodes=controls_curves_list, include_parent=True
        )
        # Connect the change pivot attribute with cop offset buffer group.
        reverse_nd = pmc.createNode(
            "reverse", n=self.change_pivot_name.replace("CON", "REVND")
        )
        self.change_pivot_control_curve[1].attr(self.CHANGE_PIVOT_ATTR).connect(
            reverse_nd.inputX
        )
        reverse_nd.outputX.connect(self.cop_offset_control_curve[0].visibility)
        # At control to offset group.
        offset_grp.addChild(self.global_control_curve[0])
        # create the script node for the change pivot callback.
        self.component_root.create_script_nd(
            beforeScript=BEFORE_CHANGE_PIV_SCRIPT_NODE_STR,
            name=self.change_pivot_name.replace("CON", "SCND"),
        )
        # At objects to output class lists.
        for control_curve in controls_curves_list:
            self.controls.append(control_curve)
        for transform in [self.local_control_curve[1], change_pivot_trs]:
            self.output_matrix_nd_list.append(transform)
            if bnd_jnt_creation:
                self.bnd_output_matrix.append(transform)
        self.component_rig_list.append(offset_grp)
        self.input_matrix_offset_grp.append(offset_grp)
        # Init the change pivot callback at creation.
        change_pivot_cbs = ChangePivotCallback()
        change_pivot_cbs.init_pivot_callback()
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

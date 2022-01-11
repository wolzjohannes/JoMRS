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
# Date:       2021 / 11 / 15

"""
Build a spine rig based on motion path nodes. With FK/IK blending and FK/IK
snap callback. Squash volume preservation.
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
reload(components.main)
reload(constants)

##########################################################
# GLOBALS
##########################################################

_LOGGER = logging.getLogger(__name__ + ".py")

##########################################################
# CLASSES
##########################################################


class MainCreate(components.main.Component):
    """
    Build the spine_0 rig component
    """

    COMP_TYPE = "spine_0_component"
    LOCAL_ROTATION_AXES = True
    DEFAULT_AXES = "Y"
    DEFAULT_SUB_OPERATORS_COUNT = 4

    def __init__(
        self,
        name,
        side=constants.DEFAULT_SIDE,
        axes=DEFAULT_AXES,
        index=constants.DEFAULT_INDEX,
        sub_operators_count=DEFAULT_SUB_OPERATORS_COUNT,
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
        self.volume_preservation_attr_name = "volume_preservation"
        self.ik_fk_snap_attr_name = "ik_fk_snap"
        self.fk_controls = []

    def add_ud_attributes_to_operators_meta_nd(self):
        """
        Add Component specific attributes to operator.
        And fill the cd_attributes list for meta data.
        """
        volume_preservation_attr = {
            "name": self.volume_preservation_attr_name,
            "attrType": "bool",
            "keyable": False,
            "channelBox": False,
        }
        ik_fk_snap_attr = {
            "name": self.ik_fk_snap_attr_name,
            "attrType": "bool",
            "keyable": False,
            "channelBox": False,
        }
        # Add the attributes to the main_meta_nd of the operator.
        cd_attributes_list = [volume_preservation_attr, ik_fk_snap_attr]
        for attr_ in cd_attributes_list:
            attributes.add_attr(node=self.main_meta_nd, **attr_)
        # It is important to append all user defined attributes to this list.
        # So they are registered as meta data in the meta node.
        # Please append the attributes name not the the attribute dict.
        cd_attributes_ref_list = [
            self.volume_preservation_attr_name,
            self.ik_fk_snap_attr_name,
        ]
        for reg_attr in cd_attributes_ref_list:
            self.cd_attributes.append(reg_attr)

    def _init_operator(self, parent=None):
        """
        Init the operator creation.
        """
        self.build_operator(
            axes=self.axes,
            sub_operators_count=self.sub_operators_count,
            parent=parent,
            local_rotate_axes=self.LOCAL_ROTATION_AXES,
        )
        length_control_name = "{}_length_{}_{}_{}".format(
            self.side,
            self.name,
            self.index,
            constants.NODE_NAMES_SUFFIX_DICT.get("control"),
        )
        length_control_ins = curves.BoxControl()
        length_control = length_control_ins.create_curve(
            name=length_control_name,
            scale=[2.5, 2.5, 2.5],
            match=self.sub_operators[-1],
        )
        self.add_node(length_control.buffer_grp)
        self.main_op_nd.addChild(length_control.buffer_grp)
        self.add_node_to_node_list(length_control.control)
        self.add_node_to_node_list(length_control.buffer_grp)
        # Refactor the operator for the component needs.
        # Here i change the aim constraint to a different behaviour.
        length_control.control.parentMatrix[0].connect(
            self.lra_nd_aim_con.target[0].targetParentMatrix, force=True
        )
        length_control.control.rotatePivot.connect(
            self.lra_nd_aim_con.target[0].targetRotatePivot, force=True
        )
        length_control.control.rotatePivotTranslate.connect(
            self.lra_nd_aim_con.target[0].targetRotateTranslate, force=True
        )
        length_control.control.translate.connect(
            self.lra_nd_aim_con.target[0].targetTranslate, force=True
        )
        self.lra_node_buffer_grp.addChild(self.sub_operators[0])
        sub_node_buffer_grps = [
            mayautils.create_parent_grp(sub_node, sub_node.getParent())
            for sub_node in self.sub_operators
        ]
        [
            self.add_node(sub_node_buffer_grp)
            for sub_node_buffer_grp in sub_node_buffer_grps
        ]
        [
            self.add_node_to_node_list(sub_node_buffer_grp)
            for sub_node_buffer_grp in sub_node_buffer_grps
        ]
        sub_nodes_lock_axes = [
            "tx",
            "ty",
            "tz",
            "ro",
            "rx",
            "ry",
            "rz",
            "sx",
            "sy",
            "sz",
        ]
        sub_nodes_lock_axes.remove("t{}".format(self.axes.lower()))
        [
            attributes.lock_and_hide_attributes(
                sub_node, attributes=sub_nodes_lock_axes
            )
            for sub_node in self.sub_operators
        ]
        dis_between_nd = pmc.createNode("distanceBetween")
        dis_between_nd.rename(
            "{}_{}_{}_0_{}".format(
                self.side,
                self.name,
                self.index,
                constants.NODE_NAMES_SUFFIX_DICT.get("distance"),
            )
        )
        decomp_nd_list = [
            pmc.createNode(
                "decomposeMatrix",
                n="{}_{}_{}_{}_{}".format(
                    self.side,
                    self.name,
                    self.index,
                    x,
                    constants.NODE_NAMES_SUFFIX_DICT.get("decompose_matrix"),
                ),
            )
            for x in range(2)
        ]
        self.add_node(dis_between_nd)
        self.add_node_to_node_list(dis_between_nd)
        [self.add_node(decomp_nd) for decomp_nd in decomp_nd_list]
        [self.add_node_to_node_list(decomp_nd) for decomp_nd in decomp_nd_list]
        decomp_nd_0, decomp_nd_1 = decomp_nd_list
        self.main_op_nd.worldMatrix[0].connect(decomp_nd_0.inputMatrix)
        length_control.control.worldMatrix[0].connect(decomp_nd_1.inputMatrix)
        decomp_nd_0.outputTranslate.connect(dis_between_nd.point1)
        decomp_nd_1.outputTranslate.connect(dis_between_nd.point2)
        divider = 1.0 / len(self.sub_operators)
        plus_minus_average_nd_0 = pmc.createNode("plusMinusAverage")
        plus_minus_average_nd_0.rename(
            "{}_{}_{}_0_{}".format(
                self.side,
                self.name,
                self.index,
                constants.NODE_NAMES_SUFFIX_DICT.get("plus_minus_average"),
            )
        )
        plus_minus_average_nd_1 = pmc.createNode("plusMinusAverage")
        plus_minus_average_nd_1.rename(
            "{}_{}_{}_1_{}".format(
                self.side,
                self.name,
                self.index,
                constants.NODE_NAMES_SUFFIX_DICT.get("plus_minus_average"),
            )
        )
        main_scale_mult_double_lin = pmc.createNode("multDoubleLinear")
        main_scale_mult_double_lin.rename(
            "{}_{}_{}_0_{}".format(
                self.side,
                self.name,
                self.index,
                constants.NODE_NAMES_SUFFIX_DICT.get("mult_double_linear"),
            )
        )
        [
            (self.add_node(pl_ma_nd), self.add_node_to_node_list(pl_ma_nd))
            for pl_ma_nd in [
                plus_minus_average_nd_0,
                plus_minus_average_nd_1,
                main_scale_mult_double_lin,
            ]
        ]
        dis_between_nd.distance.connect(plus_minus_average_nd_0.input1D[0])
        plus_minus_average_nd_0.operation.set(2)
        plus_minus_average_nd_1.operation.set(3)
        plus_minus_average_nd_1.output1D.connect(
            main_scale_mult_double_lin.input1
        )
        main_scale_mult_double_lin.output.connect(
            plus_minus_average_nd_0.input1D[1]
        )
        dis_between_nd.distance.connect(main_scale_mult_double_lin.input2)
        main_scale_mult_double_lin.input2.disconnect()
        for index, axe in enumerate("XYZ"):
            self.main_op_nd.attr("scale{}".format(axe)).connect(
                plus_minus_average_nd_1.input1D[index]
            )
        for node_index, sub_node_buffer_grp in enumerate(sub_node_buffer_grps):
            mult_double_linear_nd = pmc.createNode("multDoubleLinear")
            mult_double_linear_nd.rename(
                "{}_{}_{}_{}_{}".format(
                    self.side,
                    self.name,
                    self.index,
                    node_index + 1,
                    constants.NODE_NAMES_SUFFIX_DICT.get("mult_double_linear"),
                )
            )
            multiply_divide_nd = pmc.createNode("multiplyDivide")
            multiply_divide_nd.rename(
                "{}_{}_{}_{}_{}".format(
                    self.side,
                    self.name,
                    self.index,
                    node_index,
                    constants.NODE_NAMES_SUFFIX_DICT.get("multiply_divide"),
                )
            )
            multiply_divide_nd.operation.set(2)
            plus_minus_average_nd_1.output1D.connect(multiply_divide_nd.input2X)
            plus_minus_average_nd_0.output1D.connect(
                mult_double_linear_nd.input1
            )
            mult_double_linear_nd.input2.set(divider)
            mult_double_linear_nd.output.connect(multiply_divide_nd.input1X)
            multiply_divide_nd.outputX.connect(
                sub_node_buffer_grp.attr("translate{}".format(self.axes))
            )
            self.add_node(mult_double_linear_nd)
            self.add_node(multiply_divide_nd)
            self.add_node_to_node_list(mult_double_linear_nd)
            self.add_node_to_node_list(multiply_divide_nd)
        self.lra_node.attr("rotate{}".format(self.axes)).set(
            lock=False, keyable=True
        )

    def build_component_logic(self):
        """
        Build Component logic. It is derivative method from parent class.
        """
        # Add objects to create the component.
        # Fk controls.
        name = self.operator_meta_data.get(constants.META_MAIN_COMP_NAME)
        index = self.operator_meta_data.get(constants.META_MAIN_COMP_INDEX)
        side = self.operator_meta_data.get(constants.META_MAIN_COMP_SIDE)
        aim_axes = self.operator_meta_data.get(constants.META_OP_CREATION_AXES)
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
        # Transfer the rotation form the main lra node matrix the sub matrices.
        # Because the lra node is the master for all rotation values in the
        # component. This is a cheap way to orient my joints the component.
        sub_op_tweaked_matrix = [
            mayautils.matrix_transfer_rotation(
                lra_nd_tweaked_matrix, sub_matrix
            )
            for sub_matrix in sub_op_tweaked_matrix
        ]
        # Get control curve color from rig meta data.
        control_curve_color = self.get_control_curve_color_from_rig_meta_data(
            side, "control"
        )
        sub_control_curve_color = self.get_control_curve_color_from_rig_meta_data(
            side, "sub_control"
        )
        ########## Create all needed objects for the component. ################
        # Create the joint for the motion path spline setup.
        spine_joints = list()
        spine_joints.append(
            mayautils.create_joint(
                name="{}_DRV_spline_{}_{}_0_JNT".format(side, name, index),
                typ="DRV",
                match_matrix=lra_nd_tweaked_matrix,
            )
        )
        for count, mtx in enumerate(sub_op_tweaked_matrix):
            jnt_name = "{}_DRV_spline_{}_{}_{}_JNT".format(
                side, name, index, count + 1
            )
            jnt = mayautils.create_joint(
                name=jnt_name, typ="DRV", match_matrix=mtx
            )
            spine_joints.append(jnt)
        # Get the distance between the main_op_node and the last sub_op_node.
        # Then place 5 transforms in that range on the creation axes of the
        # operator.
        spine_curve_ik_control_buffer_groups = []
        spine_curve_ik_controls = []
        pos_mult = 0.25
        box_control_instance = curves.BoxControl()
        curve_control_0 = box_control_instance.create_curve(
            name="{}_IK_{}_{}_0_CON".format(side, name, index),
            match=lra_nd_tweaked_matrix,
            scale=orig_lra_nd_match_matrix.scale * (10, 10, 10),
            color_index=control_curve_color,
        )
        spine_curve_ik_control_buffer_groups.append(curve_control_0.buffer_grp)
        spine_curve_ik_controls.append(curve_control_0.control)
        for x in range(4):
            curve_control = box_control_instance.create_curve(
                name="{}_IK_{}_{}_{}_CON".format(side, name, index, x + 1),
                match=sub_op_tweaked_matrix[-1],
                scale=orig_lra_nd_match_matrix.scale * (10, 10, 10),
                color_index=control_curve_color,
            )
            spine_curve_ik_control_buffer_groups.append(
                curve_control.buffer_grp
            )
            spine_curve_ik_controls.append(curve_control.control)
        for node in spine_curve_ik_control_buffer_groups[1:5]:
            curve_control_0.buffer_grp.addChild(node)
            node.translate.set(
                node.translate.get()[0] * pos_mult,
                node.translate.get()[1] * pos_mult,
                node.translate.get()[2] * pos_mult,
            )
            pos_mult = pos_mult + 0.25
            pmc.parent(node, world=True)
        spine_curve_fk_control_buffer_groups = []
        spine_curve_fk_controls = []
        spine_curve_knots_control_trs = []
        for count_, node in enumerate(spine_curve_ik_control_buffer_groups):
            fk_control = curves.CircleControl().create_curve(
                name="{}_FK_{}_{}_{}_CON".format(side, name, index, count_),
                match=node,
                scale=orig_lra_nd_match_matrix.scale * (10, 10, 10),
                color_index=sub_control_curve_color,
                lock_visibility=True,
                lock_scale=True,
            )
            knote_trs = mayautils.create_ref_transform(
                name, side, index, count_, match_transform=node
            )
            spine_curve_knots_control_trs.append(knote_trs)
            spine_curve_fk_control_buffer_groups.append(fk_control.buffer_grp)
            spine_curve_fk_controls.append(fk_control.control)
        # Create the actual spine curve on base of the 5 transforms.
        spine_curve_name = "{}_spine_{}_{}_CRV".format(side, name, index)
        spine_curve = mayautils.create_curve_from_transforms(
            transforms=spine_curve_knots_control_trs,
            name=spine_curve_name,
            degree=3,
            connect=True,
        )
        # Group the nodes.
        ik_controls_grp = pmc.group(
            spine_curve_ik_control_buffer_groups,
            n="{}_IK_{}_{}_0_GRP".format(side, name, index),
        )
        fk_control_grp = pmc.group(
            spine_curve_fk_control_buffer_groups,
            n="{}_FK_{}_{}_0_GRP".format(side, name, index),
        )
        ref_trs_grp = pmc.group(
            spine_curve_knots_control_trs,
            n="{}_REF_{}_{}_0_GRP".format(side, name, index),
        )
        spine_ik_sc_joints = [
            mayautils.create_joint(
                name="{}_IK_SC_{}_{"
                "}_{}_JNT".format(side, name, index, count),
                typ="IK",
                match_matrix=mtx,
            )
            for count, mtx in enumerate(
                [lra_nd_tweaked_matrix, sub_op_tweaked_matrix[-1]]
            )
        ]
        spine_ik_rev_sc_joints = [
            mayautils.create_joint(
                name="{}_IK_REV_SC_{"
                "}_{"
                "}_{}_JNT".format(side, name, index, count),
                typ="IK",
                match_matrix=mtx,
            )
            for count, mtx in enumerate(
                [sub_op_tweaked_matrix[-1], lra_nd_tweaked_matrix]
            )
        ]
        local_y_space_record_trs_nodes = [
            mayautils.create_ref_transform(
                name=name, side=side, index=index, count=count, match_matrix=mtx
            )
            for count, mtx in enumerate(
                [sub_op_tweaked_matrix[-1], lra_nd_tweaked_matrix]
            )
        ]
        # Put a ref transform on each sub op on the spline curve.
        spine_mop_param_list = []
        lra_nd_mop_param = spine_curve.getParamAtPoint(
            lra_nd_tweaked_matrix.translate, "world"
        )
        spine_mop_param_list.append(lra_nd_mop_param)
        ####### Create nodes for atcual rig behaviour of the component.#########
        for sc_jnt in spine_ik_sc_joints + spine_ik_rev_sc_joints:
            sc_jnt.jointOrient.set(sc_jnt.rotate.get())
            sc_jnt.rotate.set(0, 0, 0)
        mayautils.create_hierarchy(spine_ik_sc_joints)
        mayautils.create_hierarchy(spine_ik_rev_sc_joints)
        spine_ik_sc_joints[-1].jointOrient.set(0, 0, 0)
        spine_ik_rev_sc_joints[-1].jointOrient.set(0, 0, 0)
        spine_ik_sc_joints[-1].addChild(spine_ik_rev_sc_joints[0])
        # self.main_fk_control = curves.BoxControl().create_curve(
        #     name=self.fk_controls_name,
        #     match=lra_nd_tweaked_matrix,
        #     scale=orig_lra_nd_match_matrix.scale * (4, 4, 4),
        #     color_index=sub_control_curve_color,
        #     lock_visibility=True,
        #     lock_scale=True,
        # )
        # self.fk_controls.append(self.main_fk_control)
        # # At objects to output class lists.
        # for control_curve in controls_curves_list:
        #     self.controls.append(control_curve)
        # self.component_rig_list.append(offset_grp)
        # self.input_matrix_offset_grp.append(offset_grp)
        logger.log(
            level="info",
            message="Component logic created "
            "for: {} Component".format(
                self.operator_meta_data[constants.META_MAIN_COMP_NAME]
            ),
            logger=_LOGGER,
        )

    def set_volume_preservation(self, value):
        """
        Enable/Disable volume preservation.

        Args:
            value(bool): Enable/Disable the volume preservation setup creation.

        """
        self.main_meta_nd.attr(self.volume_preservation_attr_name).set(value)

    def set_ik_fk_snap(self, value):
        """
        Set ik_fk_snap.

        Args:
            value(bool): Enable/Disable the ik_fk_snap setup creation.

        """
        self.main_meta_nd.attr(self.ik_fk_snap_attr_name).set(value)

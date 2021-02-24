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
# Date:       2021 / 02 / 24

"""
Build a single_control_component. Which can be used as main control or as simple fk
component
"""

import pymel.core as pmc
import attributes
import constants
import curves
import components.main
import logging
import logger
import strings
import mayautils

##########################################################
# GLOBALS
##########################################################

_LOGGER = logging.getLogger(__name__ + ".py")

##########################################################
# CLASSES
##########################################################


class MainCreate(components.main.Component):
    """
    Single FK control class. This class creates a single control and single
    joint component which could be used as main control for attribute
    purposes or as single fk rig component.
    """

    COMP_TYPE = "single_control_component"
    SUB_OPERATORS_COUNT = 0
    LOCAL_ROTATION_AXES = True
    AXES = "X"
    CONTROL_SHAPES = [
        {"shape": "box", "instance": curves.BoxControl()},
        {"shape": "sphere", "instance": curves.SphereControl()},
        {"shape": "pyramide", "instance": curves.PyramideControl()},
        {"shape": "quader", "instance": curves.QuaderControl()},
        {"shape": "square", "instance": curves.SquareControl()},
        {"shape": "circle", "instance": curves.CircleControl()},
        {"shape": "hexagon", "instance": curves.HexagonControl()},
    ]
    CONTROL_SHAPE_ATTR_NAME = "control_shape"
    BND_JNT_ATTR_NAME = "bnd_joint"
    WS_ORIENTATION_ATTR_NAME = "worldspace_orientation"
    LOCK_TRANSFORMATION_ATTRIBUTES = [
        "lock_translateX",
        "lock_translateY",
        "lock_translateZ",
        "lock_rotateX",
        "lock_rotateY",
        "lock_rotateZ",
        "lock_scaleX",
        "lock_scaleY",
        "lock_scaleZ",
    ]

    def __init__(
        self,
        name=constants.DEFAULT_OPERATOR_NAME,
        side=constants.DEFAULT_SIDE,
        index=constants.DEFAULT_INDEX,
        operators_root_node=None,
        main_operator_node=None,
        sub_operator_node=None,
    ):
        """
        Init function.

        Args:
            name(str, optional): Component name.
            side(str, optional): The Component side.
            index(int, optional): The Component index.
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

    def add_ud_attributes_to_operators_meta_nd(self):
        """
        Add Component specific attributes to operator.
        And fill the cd_attributes list for meta data.
        """
        self.control_shapes_attr = {
            "name": self.CONTROL_SHAPE_ATTR_NAME,
            "enum": [data["shape"] for data in self.CONTROL_SHAPES],
            "keyable": False,
            "hidden": False,
            "writable": True,
            "channelBox": False,
        }
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
        }
        # Add the attributes to the main_meta_nd of the operator.
        attributes.add_enum_attribute(
            node=self.main_meta_nd, **self.control_shapes_attr
        )
        cd_attributes_list = [self.bnd_joint, self.world_space_orientation_attr]
        for lock_attr in self.LOCK_TRANSFORMATION_ATTRIBUTES:
            attributes_dic = {
                "name": lock_attr,
                "attrType": "bool",
                "keyable": False,
                "channelBox": False,
            }
            cd_attributes_list.append(attributes_dic)
        for attr_ in cd_attributes_list:
            attributes.add_attr(node=self.main_meta_nd, **attr_)
        # It is important to append all user defined attributes to this list.
        # So they are registered as meta data in the meta node.,
        # Please append the attributes name not the the attribute dict.
        cd_attributes_ref_list = [
            self.CONTROL_SHAPE_ATTR_NAME,
            self.BND_JNT_ATTR_NAME,
            self.WS_ORIENTATION_ATTR_NAME,
        ]
        cd_attributes_ref_list.extend(self.LOCK_TRANSFORMATION_ATTRIBUTES)
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
        component_side = self.operator_meta_data.get(
            constants.META_MAIN_COMP_SIDE
        )
        control_name = constants.DEFAULT_CONTROL_NAME_PATTERN
        control_name = strings.search_and_replace(
            control_name, "M_", "{}_".format(component_side)
        )
        control_name = strings.search_and_replace(
            control_name,
            "name",
            self.operator_meta_data.get(constants.META_MAIN_COMP_NAME),
        )
        control_name = strings.search_and_replace(
            control_name,
            "index",
            str(self.operator_meta_data.get(constants.META_MAIN_COMP_INDEX)),
        )
        # Find correct control shape based on meta data.
        for index, shape_instance in enumerate(self.CONTROL_SHAPES):
            if index is self.operator_meta_data.get(
                self.CONTROL_SHAPE_ATTR_NAME
            ):
                curve_instance = shape_instance.get("instance")
        # Get match matrix from meta data.
        orig_match_matrix = self.operator_meta_data.get(
            constants.META_MAIN_OP_ND_WS_MATRIX_STR
        )
        # Get world space bool in meta data.
        worldspace_orientation = self.operator_meta_data.get(
            self.WS_ORIENTATION_ATTR_NAME
        )
        # Get bnd jnt creation bool in meta data.
        bnd_jnt_creation = self.operator_meta_data.get(self.BND_JNT_ATTR_NAME)
        # normalize the match matrix in scale.
        tweaked_matrix = mayautils.matrix_normalize_scale(orig_match_matrix)
        # Reset the matrix in rotation.
        if worldspace_orientation:
            tweaked_matrix = mayautils.matrix_reset_rotation(tweaked_matrix)
        # Get control curve color from rig meta data.
        control_curve_color = self.get_control_curve_color_from_rig_meta_data(
            component_side, "control"
        )
        # Create the control curve.
        control_curve = curve_instance.create_curve(
            name=control_name,
            match=tweaked_matrix,
            scale=orig_match_matrix.scale,
            color_index=control_curve_color,
            lock_visibility=True,
        )
        # Create offset grp.
        offset_grp = pmc.createNode(
            "transform", n="{}_offset_GRP".format(control_name)
        )
        # At control to offset group.
        offset_grp.addChild(control_curve[0])
        self.controls.append(control_curve[1])
        self.component_rig_list.append(offset_grp)
        self.input_matrix_offset_grp.append(offset_grp)
        self.output_matrix_nd_list.append(control_curve[1])
        # lock and hide transform attributes if it is defined in the meta data.
        for lock_attr in self.LOCK_TRANSFORMATION_ATTRIBUTES:
            if self.operator_meta_data.get(lock_attr):
                attribute_string = lock_attr.split("_")[1]
                attributes.lock_and_hide_attributes(
                    control_curve[1], attributes=attribute_string
                )
        if bnd_jnt_creation:
            self.bnd_output_matrix.append(control_curve[1])
        logger.log(
            level="info",
            message="Component logic created "
            "for: {} Component".format(
                self.operator_meta_data[constants.META_MAIN_COMP_NAME]
            ),
            logger=_LOGGER,
        )

    def set_control_shape(self, control_shape):
        """
        Set the control shape for the Component.

        Args:
            control_shape(str): The controls shapes.
            Valid values are ['box', 'sphere', 'pyramide', 'quader', 'square',
            'hexagon', 'circle']

        """
        for index, data in enumerate(self.CONTROL_SHAPES):
            if control_shape is data["shape"]:
                self.main_meta_nd.attr(self.CONTROL_SHAPE_ATTR_NAME).set(index)
                return
        logger.log(
            level="error",
            message='"{}" is not a valid shape.\nValid is {}'.format(
                control_shape, self.CONTROL_SHAPES
            ),
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

    def set_lock_and_hide_transform_attribute(self, transform_attribute, value):
        """
        Lock and hide attribute on created component.

        Args:
            transform_attribute(str): The attribute to lock.
            Valid values are [
            'translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY',
            'rotateZ', 'scaleX', 'scaleY', 'scaleZ'
            ]
            value(bool): Lock and unlock.

        """
        for lock_attr in self.LOCK_TRANSFORMATION_ATTRIBUTES:
            if transform_attribute in lock_attr:
                self.main_meta_nd.attr(lock_attr).set(value)

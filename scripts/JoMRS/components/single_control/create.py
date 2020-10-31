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
# Date:       2020 / 10 / 20

"""
Build a single single_control
"""

import pymel.core as pmc
import attributes
import constants
import curves
import components.main
import logging
import logger
import strings

reload(curves)
reload(attributes)
reload(components.main)
reload(constants)

##########################################################
# GLOBALS
##########################################################

_LOGGER = logging.getLogger(__name__ + ".py")

##########################################################
# CLASSES
##########################################################


class Main(components.main.Component):
    """
    Single single_control Component class
    """

    COMP_TYPE = "single_control"
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

    def add_component_defined_attributes(self):
        """
        Add Component specific attributes to operator.
        And fill the cd_attributes list for meta data.
        """
        self.control_shapes_attr = {
            "name": constants.CONTROL_SHAPE_ATTR_NAME,
            "enum": [data["shape"] for data in self.CONTROL_SHAPES],
            "keyable": False,
            "hidden": False,
            "writable": True,
            "channelBox": False,
        }
        attributes.add_enum_attribute(
            node=self.main_meta_nd, **self.control_shapes_attr
        )
        self.cd_attributes.append(constants.CONTROL_SHAPE_ATTR_NAME)

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
        control_name = constants.DEFAULT_CONTROL_NAME_PATTERN
        control_name = strings.search_and_replace(
            control_name,
            "M_",
            "{}_".format(
                self.operator_meta_data.get(constants.META_MAIN_COMP_SIDE)
            ),
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
        # Create offset grp.
        offset_grp = pmc.createNode(
            "transform", n="{}_offset_GRP".format(control_name)
        )
        # Find correct control shape based on meta data.
        for index, shape_instance in enumerate(self.CONTROL_SHAPES):
            if index is self.operator_meta_data["control_shape"]:
                curve_instance = shape_instance.get("instance")
        # Create control curve and match it with main_op_nd.
        curve = curve_instance.create_curve(
            name=control_name,
            match=self.operator_meta_data.get(
                constants.META_MAIN_OP_ND_WS_MATRIX_STR
            ),
        )
        # At control to offset group.
        offset_grp.addChild(curve[0])
        self.controls.append(curve[1])
        self.component_rig_list.append(offset_grp)
        self.input_matrix_offset_grp.append(offset_grp)
        self.bnd_output_matrix.append(curve[1])
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
                self.main_meta_nd.attr(constants.CONTROL_SHAPE_ATTR_NAME).set(
                    index
                )
                return
        logger.log(
            level="error",
            message='"{}" is not a valid shape.\nValid is {}'.format(
                control_shape, self.CONTROL_SHAPES
            ),
        )

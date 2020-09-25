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
# Date:       2020 / 09 / 23

"""
Build a single single_control
"""

import pymel.core as pmc
import attributes
import constants
import curves
from components import main
import logging
import logger
import strings

reload(curves)
reload(attributes)
reload(main)

##########################################################
# GLOBALS
##########################################################

_LOGGER = logging.getLogger(__name__ + ".py")

##########################################################
# CLASSES
##########################################################


class Main(main.component):
    """
    Single single_control component class

    Example:
        Create the operator.
        >>> import pymel.core as pmc
        >>> import components.main as main
        >>> import components.single_control.create as create
        >>> selected = main.selected()
        >>> control = create.Main('Test', 'L', 0, selected, selected, selected)
        >>> control._init_operator()
        >>> control.set_control_shape('pyramide')
        Create the single_control component based on the selected operator.
        >>> selected = main.selected()
        >>> component = create.Main(main_operator_node=selected)
        >>> component.build_from_operator()

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
        name=None,
        side=None,
        index=None,
        operators_root_node=None,
        main_operator_node=None,
        sub_operator_node=None,
    ):
        """
        Init function.

        Args:
            name(str, optional): Component name.
            component_type(str, optional): Component type.
            side(str, optional): The component side.
            index(int, optional): The component index.
            operators_root_node(pmc.PyNode(), optional): The operators root
            node.
            main_operator_node(pmc.PyNode(), optional): The main operator_node.
            sub_operator_node(pmc.PyNode(), optional)): The sub operator node.

        """
        main.component.__init__(
            self,
            name,
            self.COMP_TYPE,
            side,
            index,
            operators_root_node,
            main_operator_node,
            sub_operator_node,
        )

        self.control_shapes_attr = {
            "name": constants.CONTROL_SHAPE_ATTR_NAME,
            "enum": [data["shape"] for data in self.CONTROL_SHAPES],
            "keyable": False,
            "hidden": False,
            "writable": True,
            "channelBox": False,
        }

    def _init_operator(self):
        """
        Init the operator creation.
        """
        self.build_operator(
            self.AXES, self.SUB_OPERATORS_COUNT, self.LOCAL_ROTATION_AXES
        )

        attributes.add_enum_attribute(
            node=self.main_meta_nd, **self.control_shapes_attr
        )

    def build_component_logic(self, main_operator_ws_matrix=None):
        """
        Build component logic. It is derivative method from parent class.
        """
        if not main_operator_ws_matrix:
            main_operator_ws_matrix = self.get_main_op_ws_matrix()
        control_name = constants.DEFAULT_CONTROL_NAME_PATTERN
        control_name = strings.search_and_replace(
            control_name, "M_", "{}_".format(self.drawn_side)
        )
        control_name = strings.search_and_replace(
            control_name, "name", self.drawn_name
        )
        control_name = strings.search_and_replace(
            control_name, "index", str(self.drawn_index)
        )
        offset_grp = pmc.createNode(
            "transform", n="{}_offset_GRP".format(control_name)
        )
        curve_instance = self.get_control_shape_instance()
        curve = curve_instance.create_curve(
            name=control_name, match=main_operator_ws_matrix
        )
        offset_grp.addChild(curve[0])
        self.controls.append(curve[1])
        self.component_rig_list.append(offset_grp)
        self.input_matrix_offset_grp.append(offset_grp)
        self.bnd_output_matrix.append(curve[1])

    def set_control_shape(self, control_shape):
        """
        Set the control shape for the component.

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

    def get_control_shape_instance(self):
        """
        Gives back the control shape instance based on set
        control shape meta data.

        Return:
            Python object from curves module.

        """
        shape = self.main_meta_nd.attr(constants.CONTROL_SHAPE_ATTR_NAME).get(
            asString=True
        )
        for data in self.CONTROL_SHAPES:
            if shape == data["shape"]:
                return data["instance"]

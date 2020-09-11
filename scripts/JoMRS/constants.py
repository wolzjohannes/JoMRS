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
# Date:       2020 / 08 / 30

"""
JoMRS constants module for global values.
"""

import os

DEFAULT_CONTROL_NAME_PATTERN = 'M_name_index_CON'

ICONS_PATH = os.path.normpath('{}/icons'.format(
    os.environ.get("JoMRS").split("scripts")[0])
)

OP_ROOT_TAG_NAME = "JOMRS_op_root"

OP_MAIN_TAG_NAME = "JOMRS_op_main"

OP_SUB_TAG_NAME = "JOMRS_op_sub"

OP_ROOT_NAME = "M_MAIN_operators_0_GRP"

MAIN_OP_ROOT_NODE_NAME = "M_MAIN_op_0_CON"

SUB_OP_ROOT_NODE_NAME = "M_SUB_op_0_CON"

ROOT_OP_META_NODE_NAME = "M_ROOT_op_0"

ROOT_OP_META_ND_ATTR_NAME = "root_op_meta_nd"

MAIN_OP_META_ND_ATTR_NAME = "main_op_meta_nd"

SUB_OP_META_ND_ATTR_NAME = "sub_op_meta_nd"

MAIN_OP_MESSAGE_ATTR_NAME = "main_operator_nd"

ROOT_OP_MESSAGE_ATTR_NAME = "root_operator_nd"

SUB_OP_MESSAGE_ATTR_NAME = "sub_operator_nd"

LINEAR_CURVE_NAME = "M_linear_op_0_CRV"

DEFAULT_OPERATOR_NAME = "component"

DEFAULT_SIDE = "M"

DEFAULT_INDEX = 0

DEFAULT_SUB_OPERATORS_COUNT = 0

DEFAULT_AXES = "X"

DEFAULT_SPACING = 10

DEFAULT_SUB_OPERATORS_SCALE = [0.25, 0.25, 0.25]

DEFAULT_CONNECTION_TYPES = "translate;rotate;scale"

DEFAULT_COMPONENT_TYPE = 'None'

META_NODE_ID = "meta_node"

META_TYPE = "meta_class"

META_BASE_TYPE = "meta_node_class"

META_GOD_TYPE = "god_meta_class"

META_TYPE_A = "root_operators_meta_class"

META_TYPE_B = "main_operator_meta_class"

META_TYPE_C = "sub_operator_meta_class"

META_DEFAULT_CONNECTION_TYPES = "connection_types"

META_ROOT_RIG_NAME = "rig_name"

META_LEFT_RIG_COLOR = "l_rig_color"

META_LEFT_RIG_SUB_COLOR = "l_rig_sub_color"

META_RIGHT_RIG_COLOR = "r_rig_color"

META_RIGHT_RIG_SUB_COLOR = "r_rig_sub_color"

META_MID_RIG_COLOR = "m_rig_color"

META_MID_RIG_SUB_COLOR = "m_rig_sub_color"

META_MAIN_COMP_NAME = "component_name"

META_MAIN_COMP_TYPE = "component_type"

META_MAIN_COMP_SIDE = "component_side"

META_MAIN_COMP_INDEX = "component_index"

META_MAIN_CONNECTION_TYPES = "connection_types"

META_MAIN_IK_SPACES = "ik_spaces_ref"

META_MAIN_FK_SPACES = "fk_spaces_ref"

META_MAIN_IK_PVEC_SPACES = "ik_pvec_spaces_ref"

META_MAIN_CONNECT_ND = "connect_nd"

META_MAIN_RIG_BUILD_CLASS_REF = "rig_build_class_ref"

META_MAIN_PARENT_ND = "parent_nd"

META_MAIN_CHILD_ND = "child_nd"

META_GOD_META_ND_ATTR = 'meta_nd'

MAIN_META_ND_PLUG = "main_meta_nd"

SUB_META_ND_PLUG = "sub_meta_nd"

BND_OUTPUT_WS_PORT_NAME = "BND_output_ws_matrix"

OUTPUT_WS_PORT_NAME = "output_ws_matrix"

INPUT_WS_PORT_NAME = "input_ws_matrix"

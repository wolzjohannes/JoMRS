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
# Date:       2021 / 03 / 05

"""
JoMRS constants module for global values.
"""

import os

DEFAULT_CONTROL_NAME_PATTERN = 'M_name_index_CON'

ICONS_PATH = os.path.normpath('{}/icons'.format(
    os.environ.get("JoMRS").split("scripts")[0])
)

BUILD_JSON_PATH = os.path.normpath('{}/json'.format(
    os.environ.get("JoMRS").split("scripts")[0])
)

OP_ROOT_TAG_NAME = "JOMRS_op_root"

OP_MAIN_TAG_NAME = "JOMRS_op_main"

OP_SUB_TAG_NAME = "JOMRS_op_sub"

OP_LRA_TAG_NAME = "JOMRS_op_lra"

SUB_OP_LRA_TAG_NAME = "JOMRS_sub_op_lra"

OP_ROOT_NAME = "M_MAIN_operators_0_GRP"

MAIN_OP_ROOT_NODE_NAME = "M_MAIN_op_0_CON"

SUB_OP_ROOT_NODE_NAME = "M_SUB_op_0_CON"

ROOT_OP_META_NODE_NAME = "M_ROOT_op_0"

RIG_META_NODE_NAME = "M_RIG_0"

COMP_META_NODE_NAME = "M_COMP_0"

CONTAINER_META_NODE_NAME = "M_CONTAINER_0"

ROOT_OP_META_ND_ATTR_NAME = "root_op_meta_nd"

MAIN_OP_META_ND_ATTR_NAME = "main_op_meta_nd"

SUB_OP_META_ND_ATTR_NAME = "sub_op_meta_nd"

COMPONENT_META_ND_ATTR_NAME = "component_meta_nd"

CONTAINER_META_ND_ATTR_NAME = "container_meta_nd"

MAIN_OP_MESSAGE_ATTR_NAME = "main_operator_nd"

ROOT_OP_MESSAGE_ATTR_NAME = "root_operator_nd"

SUB_OP_MESSAGE_ATTR_NAME = "sub_operator_nd"

LINEAR_CURVE_NAME = "M_linear_op_0_CRV"

DEFAULT_OPERATOR_NAME = "Component"

DEFAULT_SIDE = "M"

DEFAULT_INDEX = 0

DEFAULT_SUB_OPERATORS_COUNT = 0

DEFAULT_AXES = "X"

DEFAULT_SPACING = 10

DEFAULT_SUB_OPERATORS_SCALE = [0.25, 0.25, 0.25]

DEFAULT_CONNECTION_TYPES = "translate;rotate;scale"

DEFAULT_COMPONENT_TYPE = 'None'

META_DIRTY_EVAL_ATTR = 'dirty'

META_GOD_ND_NAME = "god_meta_0_METAND"

META_NODE_ID = "meta_node"

META_TYPE = "meta_class"

META_BASE_TYPE = "meta_node_class"

META_GOD_TYPE = "god_meta_class"

META_TYPE_A = "root_operators_meta_class"

META_TYPE_B = "main_operator_meta_class"

META_TYPE_C = "sub_operator_meta_class"

META_TYPE_D = "container_meta_class"

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

META_COMPONENT_DEFINED_ATTR = "component_defined_attributes"

META_MAIN_OP_ND_WS_MATRIX_STR = "main_op_nd_ws_matrix"

META_SUB_OP_ND_WS_MATRIX_STR = "sub_op_nd_ws_matrix"

META_LRA_ND_WS_MATRIX_STR = "lra_nd_ws_matrix"

META_SUB_LRA_ND_WS_MATRIX_STR = "sub_lra_nd_ws_matrix"

META_CONTAINER_TYPE_ATTR = "container_type"

META_SCRIPT_ND = "script_nd"

UUID_ATTR_NAME = "JoMRS_UUID"

GOD_META_ND_ARRAY_PLUG_NAME = "meta_nodes"

ROOT_META_ND_ARRAY_PLUG_NAME = "main_meta_nodes"

SUB_META_ND_PLUG = "sub_meta_nd"

BND_OUTPUT_WS_PORT_NAME = "BND_output_ws_matrix"

OUTPUT_WS_PORT_NAME = "output_ws_matrix"

INPUT_WS_PORT_NAME = "input_ws_matrix"

NODE_LIST_ATTR_NAME = "node_list"

RIG_ROOT_NODE = "M_RIG_name_0_GRP"

CONTAINER_NODE_ATTR_NAME = 'container_nd'

OP_ROOT_ND_UUID_SUFFIX = 'root_op'

MAIN_OP_ND_UUID_SUFFIX = 'main_op'

RIG_CONTAINER_UUID_SUFFIX = 'rig_container'

COMP_CONTAINER_UUID_SUFFIX = 'comp_container'

CONTAINER_UUID_SUFFIX = 'container_node'

OUTPUT_WS_PORT_INDEX = 'output_ws_matrix_index'

PARENT_OUTPUT_WS_PORT_INDEX = 'parent_output_ws_matrix_index'

INPUT_WS_MATRIX_OFFSET_ND = 'input_ws_matrix_offset_nd'

BND_JNT_DEFAULT_NAME = 'side_BND_name_index_count_JNT'

BND_JNT_ROOT_ND_ATTR = 'BND_jnt_root_nd'

CONTAINER_TYPE_ATTR = 'container_type'

RIG_CONTAINER_UUID_DIC_KEY = 'rig_container_uuid'

COMP_CONTAINER_UUID_DIC_KEY = 'comp_container_uuid'

RIG_CONTAINER_TYPE = 'RIG'

COMPONENT_CONTAINER_TYPE = 'COMP'

META_DATA_DIC_ITEM_0 = 'root_meta_nd'

META_DATA_DIC_ITEM_1 = 'meta_data'
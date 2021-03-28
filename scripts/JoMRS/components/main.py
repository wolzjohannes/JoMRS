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
# Date:       2021 / 03 / 14

"""
Rig components main module. This class is the template to create a rig
Component. Every rig Component should inherit this class as template.
"""
import os
import pymel.core as pmc
import strings
import attributes
import operators
import logger
import logging
import constants
import mayautils


##########################################################
# Methods
# init hierarchy
# input output management
# build process
# build steps. Example: layout rig. orient rig. ref nodes.
# all repedative things in a Component build.
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
# Add entry in ref rig build class attr
##########################################################

##########################################################
# GLOBALS
##########################################################

_LOGGER = logging.getLogger(__name__ + ".py")

##########################################################
# FUNCTIONS
##########################################################


def selected():
    """
    Gets back a selected transform or container node.

    Returns:
       pmc.PyNode if successful. None if fail.

    """
    containers = pmc.ls(sl=True, containers=True)
    transforms = pmc.ls(sl=True, tr=True)
    if containers:
        return containers[0]
    if transforms:
        return transforms[0]
    return None


##########################################################
# CLASSES
##########################################################


class Component(operators.ComponentOperator):
    """
    Component template class.
    """

    def __init__(
        self,
        name=constants.DEFAULT_OPERATOR_NAME,
        component_type=constants.DEFAULT_COMPONENT_TYPE,
        side=constants.DEFAULT_SIDE,
        index=constants.DEFAULT_INDEX,
        operators_root_node=None,
        main_operator_node=None,
        sub_operator_node=None,
    ):
        """
        Init important data.

        Args:
            name(str, optional): Component name.
            component_type(str, optional): Component type.
            side(str, optional): The Component side.
            index(int, optional): The Component index.
            operators_root_node(pmc.PyNode(), optional): The operators root
            node.
            main_operator_node(pmc.PyNode(), optional): The main operator_node.
            sub_operator_node(pmc.PyNode(), optional)): The sub operator node.

        """
        operators.ComponentOperator.__init__(
            self, operators_root_node, main_operator_node, sub_operator_node
        )
        self.name = name
        self.component_type = component_type
        self.side = side
        self.index = index
        self.component_root = []
        self.component_rig_list = []
        self.bnd_output_matrix = []
        self.input_matrix_offset_grp = []
        self.output_matrix_nd_list = []
        self.controls = []
        self.operator_meta_data = {}
        self.rig_meta_data = {}

    def add_ud_attributes_to_operators_meta_nd(self):
        """
        Method to implement extra ud attributes to the operators meta node..
        """
        logger.log(
            level="info",
            message="Not implemented yet",
            func=self.add_ud_attributes_to_operators_meta_nd,
            logger=_LOGGER,
        )

    def add_ud_attributes_to_comp_container_meta_nd(self):
        """
        Method to add extra ud attributes to container meta nd.
        """
        logger.log(
            level="info",
            message="Not implemented yet",
            func=self.add_ud_attributes_to_comp_container_meta_nd,
            logger=_LOGGER,
        )

    def build_operator(
        self,
        axes,
        sub_operators_count,
        parent=None,
        local_rotate_axes=True,
        connect_node=None,
        ik_space_ref=None,
        sub_operators_local_rotate_axes=False,
    ):
        """
        Build Component operator.

        Args:
            axes(str): The build axes. Valid is X, -X, Y, -Y, Z, -Z.
            sub_operators_count(int): Sub operators count.
            parent(pmc.PyNode): The parent node.
            connect_node(str): The connect node .
            ik_space_ref(list): Spaces given as nodes in a string
            local_rotate_axes(bool): Enable/Disable.
            sub_operators_local_rotate_axes(bool): Enable the local rotate
            axes for the sub_operators.

        """
        if not parent:
            parent = selected()
        self.create_component_op_node(
            name=self.name,
            side=self.side,
            index=self.index,
            axes=axes,
            sub_operators_count=sub_operators_count,
            local_rotate_axes=local_rotate_axes,
            parent=parent,
            sub_operators_local_rotate_axes=sub_operators_local_rotate_axes,
        )
        self.set_component_name(self.name)
        self.set_component_type(self.component_type)
        self.set_component_side(self.side)
        self.set_component_index(self.index)
        self.add_ud_attributes_to_operators_meta_nd()
        self.set_cd_attributes()
        if connect_node:
            self.set_connect_nd(connect_node)
        if ik_space_ref:
            self.set_ik_spaces_ref(ik_space_ref)
        logger.log(
            level="info",
            message="{} Component operator "
            "build with the name: {}".format(self.component_type, self.name),
            logger=_LOGGER,
        )

    def get_operator_meta_data(self):
        """
        Collect the operators meta data.
        """
        self.operator_meta_data[
            constants.META_MAIN_OP_ND_WS_MATRIX_STR
        ] = self.get_main_op_ws_matrix()
        self.operator_meta_data[
            constants.META_LRA_ND_WS_MATRIX_STR
        ] = self.get_lra_nd_ws_matrix()
        self.operator_meta_data[
            constants.META_SUB_OP_ND_WS_MATRIX_STR
        ] = self.get_sub_op_nodes_ws_matrix()
        self.operator_meta_data[
            constants.META_SUB_LRA_ND_WS_MATRIX_STR
        ] = self.get_sub_lra_nd_ws_matrix()
        self.operator_meta_data[
            constants.META_MAIN_COMP_NAME
        ] = self.get_component_name()
        self.operator_meta_data[
            constants.META_MAIN_COMP_TYPE
        ] = self.get_component_type()
        self.operator_meta_data[
            constants.META_MAIN_COMP_SIDE
        ] = self.get_component_side()
        self.operator_meta_data[
            constants.META_MAIN_COMP_INDEX
        ] = self.get_component_index()
        self.operator_meta_data[
            constants.META_MAIN_CONNECTION_TYPES
        ] = self.get_connection_types()
        self.operator_meta_data[
            constants.META_MAIN_IK_SPACES
        ] = self.get_ik_spaces_ref()
        self.operator_meta_data[
            constants.META_MAIN_CONNECT_ND
        ] = self.get_connect_nd()
        self.operator_meta_data[
            constants.META_MAIN_PARENT_ND
        ] = self.get_parent_nd()
        self.operator_meta_data[
            constants.META_MAIN_CHILD_ND
        ] = self.get_child_nd()
        self.operator_meta_data[
            constants.UUID_ATTR_NAME
        ] = self.main_meta_nd.get_uuid()
        self.operator_meta_data[
            constants.PARENT_OUTPUT_WS_PORT_INDEX
        ] = self.main_meta_nd.get_parent_ws_output_index()
        self.operator_meta_data.update(self.get_cd_attributes())

    def get_rig_meta_data(self):
        """
        Collect rig meta data.
        """
        self.rig_meta_data[
            constants.UUID_ATTR_NAME
        ] = self.root_meta_nd.get_uuid()
        self.rig_meta_data[constants.META_ROOT_RIG_NAME] = self.get_rig_name()
        self.rig_meta_data[
            constants.META_LEFT_RIG_COLOR
        ] = self.get_l_control_rig_color()
        self.rig_meta_data[
            constants.META_LEFT_RIG_SUB_COLOR
        ] = self.get_l_sub_control_rig_color()
        self.rig_meta_data[
            constants.META_RIGHT_RIG_COLOR
        ] = self.get_r_control_rig_color()
        self.rig_meta_data[
            constants.META_RIGHT_RIG_SUB_COLOR
        ] = self.get_r_sub_control_rig_color()
        self.rig_meta_data[
            constants.META_MID_RIG_COLOR
        ] = self.get_m_control_rig_color()
        self.rig_meta_data[
            constants.META_MID_RIG_SUB_COLOR
        ] = self.get_m_sub_control_rig_color()

    def create_component_container(self):
        """
        Init rig component container its contents..
        """
        self.component_root = CompContainer(
            comp_name=self.operator_meta_data.get(
                constants.META_MAIN_COMP_NAME
            ),
            comp_side=self.operator_meta_data.get(
                constants.META_MAIN_COMP_SIDE
            ),
            comp_index=self.operator_meta_data.get(
                constants.META_MAIN_COMP_INDEX
            ),
            component_type=self.operator_meta_data.get(
                constants.META_MAIN_COMP_TYPE
            ),
        )
        self.component_root.create_comp_container()
        # Refactor Main op uuid to comp uuid
        uuid_ = self.operator_meta_data.get(constants.UUID_ATTR_NAME)
        uuid_ = strings.search_and_replace(
            uuid_,
            constants.MAIN_OP_ND_UUID_SUFFIX,
            constants.COMP_CONTAINER_UUID_SUFFIX,
        )
        self.component_root.set_uuid(uuid_)
        logger.log(
            level="info",
            message="Component hierarchy setted up "
            "for: {} Component".format(
                self.operator_meta_data[constants.META_MAIN_COMP_NAME]
            ),
            logger=_LOGGER,
        )

    def create_input_ws_matrix_port(self, name):
        """
        Create a input port for ws matrix connection.

        Args:
            name(str): Name of the attribute.

        """
        attributes.add_attr(
            self.component_root.container_content.get("input"),
            name="{}_input_ws_matrix".format(name),
            attrType="matrix",
            keyable=False,
            hidden=True,
        )

    def create_input_os_matrix_port(self, name):
        """
        Create a input port for os matrix connection.

        Args:
            name(str): Name of the attribute.

        """
        attributes.add_attr(
            self.component_root.container_content.get("input"),
            name="{}_input_os_matrix".format(name),
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
            self.component_root.container_content.get("output"),
            name="{}_output_ws_matrix".format(name),
            attrType="matrix",
            keyable=False,
            hidden=True,
        )

    def create_output_os_matrix_port(self, name):
        """
        Create a output port for os matrix connection.

        Args:
            name(str): Name of the attribute.

        """
        attributes.add_attr(
            self.component_root.container_content.get("output"),
            name="{}_output_os_matrix".format(name),
            attrType="matrix",
            keyable=False,
            hidden=True,
        )

    def add_ud_port(
        self,
        component_port="input",
        name=None,
        type_="float",
        minValue=0,
        maxValue=1,
        value=1,
    ):
        """
        Add user defined port to the input or output port of a rig Component.
        By Default it add a float value to the input port with a given
        name, with a min value of 0.0 a max value of 1.0 and a value of 1.0.

        Args:
            component_port(str): The rig components port.
            name(str): The port name.
            type_(str): The port typ.
            minValue(float or int): The minimal port value.
            maxValue(float or int): The maximum port value.
            value(float or int or str): The port value.

        """
        valid_ports = ["input", "output"]
        if component_port not in valid_ports:
            raise AttributeError(
                'Chosen port not valid. Valid values are ["input", "output"]'
            )
        node = self.component_root.container_content.get("input")
        if component_port == "output":
            node = self.component_root.container_content.get("output")

        attributes.add_attr(
            node=node,
            name=name,
            attrType=type_,
            minValue=minValue,
            maxValue=maxValue,
            value=value,
        )

    def build_component_logic(self):
        """
        Method for building a Component. Use the list variables
        self.component_rig_list, self.bnd_output_matrix,
        self.input_matrix_offset_grp to define input and output connections
        of the Component.
        """
        # Logger section for proper user feedback.
        logger.log(
            level="info",
            message="Component logic created "
            "for: {} Component".format(
                self.operator_meta_data[constants.META_MAIN_COMP_NAME]
            ),
            logger=_LOGGER,
        )
        return True

    def connect_inner_component_edges(self):
        """
        Method to connect the component rig content with the input and
        outputs of the component.
        """
        # connect every node in the bnd_output_matrix list as BND output in
        # the output node.
        for index, bnd_node in enumerate(self.bnd_output_matrix):
            bnd_node.worldMatrix[0].connect(
                self.component_root.container_content.get("output").attr(
                    "{}[{}]".format(
                        constants.BND_OUTPUT_WS_PORT_NAME, str(index)
                    )
                )
            )
        # connect every node in the input_matrix_offset_grp with the
        # input_ws_matrix_offset_nd attr on the meta nd. For further use to
        # connect the different components.
        if self.input_matrix_offset_grp:
            self.component_root.set_input_ws_matrix_offset_nd(
                self.input_matrix_offset_grp
            )
        # each node in the output_matrix_nd_list will be connected with
        # output_ws_matrix node of the component output nd.
        if self.output_matrix_nd_list:
            for index, output_nd in enumerate(self.output_matrix_nd_list):
                output_nd.worldMatrix[0].connect(
                    self.component_root.container_content.get("output").attr(
                        "{}[{}]".format(
                            constants.OUTPUT_WS_PORT_NAME, str(index)
                        )
                    )
                )
        # every node in the component rig list will be a child of the
        # component node.
        if self.component_rig_list:
            for node in self.component_rig_list:
                self.component_root.add_node_to_container_content(
                    node, "component"
                )
        # Step feedback
        logger.log(
            level="info",
            message="Inner component edges connected "
            "for: {} Component".format(
                self.operator_meta_data[constants.META_MAIN_COMP_NAME]
            ),
            logger=_LOGGER,
        )

    def create_BND_joints(self):
        """
        Create the component bind joints.
        """
        output_nd = self.component_root.container_content.get("output")
        connected_bnd_outputs = output_nd.attr(
            constants.BND_OUTPUT_WS_PORT_NAME
        ).get()
        if not connected_bnd_outputs:
            return False
        main_op_ws_scale = self.operator_meta_data.get(
            constants.META_MAIN_OP_ND_WS_MATRIX_STR
        ).scale
        # calculate the scale average for the correct joint radius.
        scale_x, scale_y, scale_z = main_op_ws_scale
        main_op_ws_scale_avg = (scale_x + scale_y + scale_z) / 3
        temp = []
        for count in range(len(connected_bnd_outputs)):
            # Bind joint name creation.
            bnd_joint_name = strings.search_and_replace(
                constants.BND_JNT_DEFAULT_NAME,
                "side",
                self.operator_meta_data.get(constants.META_MAIN_COMP_SIDE),
            )
            bnd_joint_name = strings.search_and_replace(
                bnd_joint_name,
                "name",
                self.operator_meta_data.get(constants.META_MAIN_COMP_NAME),
            )
            bnd_joint_name = strings.search_and_replace(
                bnd_joint_name,
                "index",
                str(
                    self.operator_meta_data.get(constants.META_MAIN_COMP_INDEX)
                ),
            )
            bnd_joint_name = strings.search_and_replace(
                bnd_joint_name, "count", str(count)
            )
            bnd_joint = mayautils.create_joint(bnd_joint_name, typ="BND")
            bnd_joint.radius.set(main_op_ws_scale_avg)
            mul_ma_nd = mayautils.create_matrix_constraint(
                source=bnd_joint,
                target=output_nd,
                target_plug="{}[{}]".format(
                    constants.BND_OUTPUT_WS_PORT_NAME, str(count)
                ),
            )
            # get the matrix constraint nodes and add them to the component
            # container.
            offset_matrix_nd = mul_ma_nd.matrixIn[0].connections()
            decomp_nd = mul_ma_nd.matrixSum.connections()
            for node in [offset_matrix_nd, decomp_nd, mul_ma_nd]:
                self.component_root.container.addNode(node)
            # The part below will check if the component is a mirrored
            # component. If it will get the negative scale value in the
            # bnd joints and make it positive! This is important for a correct
            # rig hierarchy without buffer transforms.
            negate_axe = []
            if bnd_joint.scaleX.get() < 0:
                negate_axe.append("X")
            elif bnd_joint.scaleY.get() < 0:
                negate_axe.append("Y")
            elif bnd_joint.scaleZ.get() < 0:
                negate_axe.append("Z")
            if negate_axe:
                for axe in negate_axe:
                    mult_nd_name = strings.search_and_replace(
                        decomp_nd.name(),
                        "_DEMAND",
                        "_scale_{}_MULDOLINND".format(axe),
                    )
                    mult_nd = pmc.createNode("multDoubleLinear", n=mult_nd_name)
                    mult_nd.input2.set(-1)
                    decomp_nd.attr("outputScale{}".format(axe)).connect(
                        mult_nd.input1
                    )
                    mult_nd.output.connect(
                        bnd_joint.attr(
                            bnd_joint.attr("scale{}".format(axe)), force=True
                        )
                    )
            temp.append(bnd_joint)
        # If it is more then one joint it will create a hierarchy.
        if len(temp) > 1:
            mayautils.create_hierarchy(temp, True)
        # set joint orient to zero because this would mess up the matrix
        # constraint setup.
        for jnt in temp:
            jnt.jointOrient.set(0, 0, 0)
        self.component_root.set_bnd_root_nd(temp[-1])
        # Step feedback
        logger.log(
            level="info",
            message="BND joint hierarchy build "
            "for: {} Component".format(
                self.operator_meta_data[constants.META_MAIN_COMP_NAME]
            ),
            logger=_LOGGER,
        )

    def build_from_operator(self, operator_meta_data=None, rig_meta_data=None):
        """
        Build the whole Component rig from operator.
        With initial hierarchy.

        Args:
            operator_meta_data(dict): Operators meta data.
            rig_meta_data(dict): Rig meta data.

        """
        if not operator_meta_data:
            self.get_operator_meta_data()
        else:
            self.operator_meta_data = operator_meta_data
        if not rig_meta_data:
            self.get_rig_meta_data()
        else:
            self.rig_meta_data = rig_meta_data
        self.clean_objects()
        self.create_component_container()
        self.add_ud_attributes_to_comp_container_meta_nd()
        self.build_component_logic()
        self.connect_inner_component_edges()
        self.create_BND_joints()

    def clean_objects(self):
        """
        Clean class objects for reuse.
        """
        del self.component_rig_list[:]
        del self.bnd_output_matrix[:]
        del self.input_matrix_offset_grp[:]
        del self.output_matrix_nd_list[:]

    def get_control_curve_color_from_rig_meta_data(self, side, control_typ):
        """
        Get the the control curve color from rig meta data.

        Args:
            side(str): Define the control curve side.
            Valid values are ['L', 'R', 'M']
            control_typ(str): Define if the control is sub or normal control
            curve. Valid values are ['control', 'sub_control']

        Returns:
             Integer: The maya color index specified for that control_type
             and side in the rig meta data.

        """
        if not self.rig_meta_data:
            logger.log(
                level="error", message="No rig meta data found.", logger=_LOGGER
            )
            return False
        if side == "L" and control_typ == "control":
            return self.rig_meta_data.get(constants.META_LEFT_RIG_COLOR)
        elif side == "L" and control_typ == "sub_control":
            return self.rig_meta_data.get(constants.META_LEFT_RIG_SUB_COLOR)
        elif side == "R" and control_typ == "control":
            return self.rig_meta_data.get(constants.META_RIGHT_RIG_COLOR)
        elif side == "R" and control_typ == "sub_control":
            return self.rig_meta_data.get(constants.META_RIGHT_RIG_SUB_COLOR)
        elif side == "M" and control_typ == "control":
            return self.rig_meta_data.get(constants.META_MID_RIG_COLOR)
        elif side == "M" and control_typ == "sub_control":
            return self.rig_meta_data.get(constants.META_MID_RIG_SUB_COLOR)


class CompContainer(mayautils.ContainerNode):
    """
    Create a container node designed for rig components..
    """

    CONTENT_GROUPS = ["input", "output", "component", "spaces"]

    def __init__(
        self,
        comp_name=None,
        comp_side=None,
        comp_index=0,
        component_container=None,
        component_type=None,
    ):
        """
        Args:
            comp_name(str): The rig component name.
            comp_side(str): The component side.
            comp_index(int): The component index.
            component_container(pmc.PyNode()): A component container to pass.
            component_type(str): The rig component type.
        """
        super(CompContainer, self).__init__(
            container_node=component_container, content_root_node=True
        )
        self.name = "M_ROOT_name_component_0_GRP"
        self.meta_nd_name = constants.COMP_META_NODE_NAME
        self.icon = os.path.normpath(
            "{}/components_logo.png".format(constants.ICONS_PATH)
        )
        self.component_type = component_type
        self.script_nd = []
        if comp_name and comp_side:
            self.meta_nd_name = self.meta_nd_name.replace("COMP", comp_name)
            self.name = (
                self.name.replace("M", comp_side)
                .replace("name", comp_name)
                .replace("0", str(comp_index))
            )
            self.name = strings.string_checkup(self.name)
            self.container_content_root_name = (
                self.container_content_root_name.replace("M", comp_side)
                .replace("content_root", "{}_content_root".format(comp_name))
                .replace("0", str(comp_index))
            )

    def create_comp_container(self):
        """
        Create the component container.
        """
        self.create_container()
        self.create_container_content_from_list(self.CONTENT_GROUPS)
        attributes.add_attr(
            node=self.meta_nd,
            name=constants.META_MAIN_COMP_TYPE,
            attrType="string",
            keyable=False,
            channelBox=False,
        )
        attributes.add_attr(
            self.container_content.get("input"),
            name=constants.INPUT_WS_PORT_NAME,
            attrType="matrix",
            multi=True,
            keyable=False,
            hidden=True,
        )
        attributes.add_attr(
            self.container_content.get("output"),
            name=constants.OUTPUT_WS_PORT_NAME,
            attrType="matrix",
            multi=True,
            keyable=False,
            hidden=True,
        )
        attributes.add_attr(
            self.container_content.get("output"),
            name=constants.BND_OUTPUT_WS_PORT_NAME,
            attrType="matrix",
            multi=True,
            keyable=False,
            hidden=True,
        )
        self.set_container_type(constants.COMPONENT_CONTAINER_TYPE)
        self.set_component_type(self.component_type)

    def set_input_ws_matrix_offset_nd(self, offset_nd_list):
        """
        Connect a list of nodes with the input ws matrix nd port on the
        container meta nd

        Args:
            offset_nd_list(list): The node list to connect with the offset nd
            list port.

        """
        for index, node in enumerate(offset_nd_list):
            node.message.connect(
                self.meta_nd.attr(
                    "{}[{}]".format(
                        constants.INPUT_WS_MATRIX_OFFSET_ND, str(index)
                    )
                )
            )

    def get_input_ws_matrix_offset_nd(self):
        """
        Get the input ws matrix offset nd.

        Returns:
            List: All connected offset nodes
            
        """
        return self.meta_nd.attr(constants.INPUT_WS_MATRIX_OFFSET_ND).get()

    def set_bnd_root_nd(self, node):
        """
        Set the bnd root nd.
        """
        node.message.connect(self.meta_nd.attr(constants.BND_JNT_ROOT_ND_ATTR))

    def set_component_type(self, type):
        """
        Set the component type in component container meta nd.

        Args:
            type(str): The component type.

        """
        self.meta_nd.attr(constants.META_MAIN_COMP_TYPE).set(type)

    def get_bnd_root_nd(self):
        """
        Get the bnd root node

        Returns:
             pmc.PyNode(): The bnd root node.

        """
        return self.meta_nd.attr(constants.BND_JNT_ROOT_ND_ATTR).get()

    def create_script_nd(
        self,
        scriptType=1,
        beforeScript="",
        afterScript="",
        name="",
        sourceType="python",
    ):
        """
        Create a script node which corresponds to the component container.
        It is add to the component container and connected to the meta node by
        default.

        Args:
            scriptType(int): When the script will execute.
            Valid values are:
            [0: Execute on demand, 1: Execute on file load or on node
            deletion, 2: Execute on file load or on node deletion when not in
            batch mode, 3: Internal, 4: Execute on software render,
            5: Execute on software frame render, 6: Execute on scene
            configuration, 7: Execute on time changed.]
            beforeScript(str): The script executed during file load.
            afterScript(str): The script executed when the script node is
            deleted.
            name(str): The nodes name.
            sourceType(str): Sets the language type for both the attached
            scripts. Default is "python".

        """
        data_dic = {
            "scriptType": scriptType,
            "beforeScript": beforeScript,
            "afterScript": afterScript,
            "name": name,
            "sourceType": sourceType,
        }
        script_nd = pmc.PyNode(pmc.scriptNode(**data_dic))
        self.meta_nd.add_script_nd(script_nd)
        self.container.addNode(script_nd)
        self.script_nd.append(script_nd)

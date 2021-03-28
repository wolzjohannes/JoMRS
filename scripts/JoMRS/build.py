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
Rig build module. Collect the rig data based on the specified rig operators
in the scene. Based on that data it execute the rig build. This module produces
a bunch of list and dictionaries which are used to build the final rig.
This data can be saved as json file. And it can build a rig based on a json
file imports.
"""

import pymel.core as pmc
import pymel.core.datatypes as dt
import constants
import logger
import logging
import components.main
import mayautils
import strings
import importlib
import os
import json
import copy
import meta

##########################################################
# GLOBALS
##########################################################

_LOGGER = logging.getLogger(__name__ + ".py")

##########################################################
# CLASSES
##########################################################


class MainBuild(object):
    """
    Main class to build a rig based on the operators in the scene.
    The rig building is divided in steps. All steps are their own method.
    And the "self.execute_building_steps()" method will execute them in the
    right order. This method is the finale building method.

    The steps are:
    self.get_meta_data(rig_meta_data, operator_meta_data)
    self.process_component_parenting_data(component_parenting_data)
    self.build_rig_container()
    self.build_components()
    self.connect_components()
    self.connect_components_inputs_with_components_rig_offsets_grp()
    self.parent_components()
    self.arrange_deformation_hierarchy()

    """

    def __init__(self):
        self.selection = components.main.selected()
        self.component_instance = components.main.Component(
            operators_root_node=self.selection,
            main_operator_node=self.selection,
            sub_operator_node=self.selection,
        )
        self.god_meta_nd = []
        self.operators_meta_data = []
        self.rig_meta_data = []
        self.parenting_data_dic = []
        self.rig_container = None
        self.rig_container_uuid = ""

    def get_meta_data(self, rig_meta_data=None, operator_meta_data=None):
        """
        Get meta data. If no operators_root node or main_op_nd is
        selected get the data found in the scene. It collect the
        rig_meta_data and the operator_meta_data. It stores the data in the
        "self.rig_meta_data" and "self.operators_meta_data" variables.

        Args:
            rig_meta_data(List): Filled with dict.
            operator_meta_data(List): Filled with dict.

        Example:
            >>>import build
            >>>build_instance = build.MainBuild()
            >>>build_instance.get_meta_data()
            [{'root_meta_nd': nt.RootOpMetaNode(u'M_ROOT_op_0_METAND'),
            'meta_data': {'rig_name': u'MOM', 'r_rig_color': 6,
            'l_rig_sub_color': 18,
            'JoMRS_UUID': u'cc4064e3-f3b0-4512-8e44-b914b3df3c1e-root_op',
            'l_rig_color': 13, 'r_rig_sub_color': 9, 'm_rig_sub_color': 11,
            'm_rig_color': 17}},
            {'root_meta_nd': nt.RootOpMetaNode(u'M_ROOT_op_1_METAND'),
            'meta_data': {'rig_name': u'Test', 'r_rig_color': 6,
            'l_rig_sub_color': 18,
            'JoMRS_UUID': u'd16fe8f1-0d50-4a20-9b61-79a2f2f817bd-root_op',
            'l_rig_color': 13, 'r_rig_sub_color': 9, 'm_rig_sub_color': 11,
            'm_rig_color': 17}}]
            [{'root_meta_nd': nt.RootOpMetaNode(u'M_ROOT_op_0_METAND'),
            'meta_data': [{'component_type': u'test_single_control',
            'component_side': u'L',
            'main_op_nd_ws_matrix':
            Matrix([[-0.855774425863, -0.416261824405, -0.307207137909, 0.0],
            [0.495584209548, -0.489167922022, -0.717712362519, 0.0],
            [0.148480380138, -0.766446891577, 0.624910184831, 0.0],
            [-16.108, 14.13, 0.97, 1.0]]), 'sub_op_nd_ws_matrix': [],
            'connection_types': [u'translate', u'rotate', u'scale'],
            'ik_spaces_ref': None, 'connect_nd': None, 'child_nd': [],
            'parent_nd': None, u'control_shape': 1, 'component_index': 0,
            'JoMRS_UUID': u'f0bc993e-38e5-4210-816c-3dac633b6ee0-main_op',
            'component_name': u'MOM'}]},
            {'root_meta_nd': nt.RootOpMetaNode(u'M_ROOT_op_1_METAND'),
            'meta_data': [{'component_type': u'test_single_control',
            'component_side': u'M',
            'main_op_nd_ws_matrix':
            Matrix([[0.0498978099393, 0.554286236569, -0.830829089834, 0.0],
            [0.439365178618, 0.734866446494, 0.516652248263, 0.0],
            [0.896921651194, -0.390817187144, -0.206865845057, 0.0],
            [13.124, 13.397, -9.37, 1.0]]), 'sub_op_nd_ws_matrix': [],
            'connection_types': [u'translate', u'rotate', u'scale'],
            'ik_spaces_ref': None, 'connect_nd': None, 'child_nd': [],
            'parent_nd': None, u'control_shape': 2, 'component_index': 1,
            'JoMRS_UUID': u'62c00a43-269b-4b19-b275-2bc7d9b28162-main_op',
            'component_name': u'Test'}]}]

        """
        logger.log(
            level="info", message="### Get meta data. " "###", logger=_LOGGER
        )
        # Pass data from json file or other source.
        self.operators_meta_data = operator_meta_data
        self.rig_meta_data = rig_meta_data
        # If no data passed generate it.
        if not operator_meta_data:
            if not self.selection:
                self.get_meta_data_from_all_root_meta_nodes_in_scene(
                    "operators"
                )
            else:
                self.get_operators_meta_data_from_root_meta_node()
        if not rig_meta_data:
            if not self.selection:
                self.get_meta_data_from_all_root_meta_nodes_in_scene("rig")
            else:
                self.get_rig_meta_data_from_root_meta_node(
                    self.component_instance.root_meta_nd
                )

    def process_component_parenting_data(self, component_parenting_data=None):
        """
        Process the correct parenting data based on the rig and operator meta
        data. It will store the data in the "self.parenting_data_dic" variable.

        Args:
            component_parenting_data(List): List filled with dict to pass.

        Example:
            >>>import build
            >>>build_instance = build.MainBuild()
            >>>build_instance.process_component_parenting_data()
            [{'root_meta_nd_uuid':
            u'cc4064e3-f3b0-4512-8e44-b914b3df3c1e-rig_container',
            'rig_components_uuid':
            [u'f0bc993e-38e5-4210-816c-3dac633b6ee0-comp_container']},
            {'root_meta_nd_uuid':
            u'd16fe8f1-0d50-4a20-9b61-79a2f2f817bd-rig_container',
            'rig_components_uuid': [
            u'62c00a43-269b-4b19-b275-2bc7d9b28162-comp_container']}]

        """
        logger.log(
            level="info",
            message="### Processing component parenting data dictionary. "
            "###",
            logger=_LOGGER,
        )
        result = []
        self.parenting_data_dic = component_parenting_data
        if not component_parenting_data:
            for op_meta_data in self.operators_meta_data:
                data_dic = {}
                for rig_meta_data in self.rig_meta_data:
                    if op_meta_data.get(
                        constants.META_DATA_DIC_ITEM_0
                    ) == rig_meta_data.get(constants.META_DATA_DIC_ITEM_0):
                        rig_components_list = []
                        for rig_components in op_meta_data.get(
                            constants.META_DATA_DIC_ITEM_1
                        ):
                            comp_container_uuid = strings.search_and_replace(
                                rig_components.get(constants.UUID_ATTR_NAME),
                                constants.MAIN_OP_ND_UUID_SUFFIX,
                                constants.COMP_CONTAINER_UUID_SUFFIX,
                            )
                            rig_components_list.append(comp_container_uuid)
                        data_dic[
                            constants.RIG_CONTAINER_UUID_DIC_KEY
                        ] = strings.search_and_replace(
                            rig_meta_data.get(
                                constants.META_DATA_DIC_ITEM_1
                            ).get(constants.UUID_ATTR_NAME),
                            constants.OP_ROOT_ND_UUID_SUFFIX,
                            constants.RIG_CONTAINER_UUID_SUFFIX,
                        )
                        data_dic[
                            constants.COMP_CONTAINER_UUID_DIC_KEY
                        ] = rig_components_list
                result.append(data_dic)
            self.parenting_data_dic = result

    def build_rig_container(self):
        """
        Build the rig container and its sibling containers.
        """
        logger.log(
            level="info",
            message="### Start building rig container. " "###",
            logger=_LOGGER,
        )
        # Loop through the rig meta data.
        for data in self.rig_meta_data:
            self.rig_container = RigContainer(
                data.get(constants.META_DATA_DIC_ITEM_1).get("rig_name")
            )
            self.rig_container.create_rig_container()
            # Refactor root_op uuid to rig_container uuid. So we are able to
            # find the container easier in the scene and we are not limited
            # to hardcoded names. The refactored uuid link the operators root
            # and the rig container. This is important for the component
            # parenting.
            self.rig_container_uuid = (
                data.get(constants.META_DATA_DIC_ITEM_1)
                .get(constants.UUID_ATTR_NAME)
                .replace(
                    constants.OP_ROOT_ND_UUID_SUFFIX,
                    constants.RIG_CONTAINER_UUID_SUFFIX,
                )
            )
            # Give the rig container its refactored uuid.
            self.rig_container.set_uuid(self.rig_container_uuid)

    def build_components(self):
        """
        Build all rig components based on passed operators meta data.
        """
        if not self.operators_meta_data:
            logger.log(
                level="error", message="No operators meta data " "accessible"
            )
            return False
        logger.log(
            level="info",
            message="### Start building rig components. " "###",
            logger=_LOGGER,
        )
        # Loop through the operators meta data
        for data in self.operators_meta_data:
            # Get root meta node. This represent the operators root node.
            root_meta_nd = data.get(constants.META_DATA_DIC_ITEM_0)
            # Loop trough rig_meta_data and get the correct rig meta data based
            # on the root_meta_nd.
            rig_m_data = None
            for rig_data in self.rig_meta_data:
                if rig_data.get(constants.META_DATA_DIC_ITEM_0) == root_meta_nd:
                    rig_m_data = rig_data.get(constants.META_DATA_DIC_ITEM_1)
            # Get the operators meta data belongs to root_meta_nd.
            meta_data = data.get(constants.META_DATA_DIC_ITEM_1)
            logger.log(
                level="info",
                message="Build components for {}".format(root_meta_nd),
                logger=_LOGGER,
            )
            # loop through meta data
            for op_m_data in meta_data:
                # based on the component type stored in the meta data create
                # the python import statement string for each found component
                # type.
                component_module_name = "components.{}.create".format(
                    op_m_data.get(constants.META_MAIN_COMP_TYPE)
                )
                # import correct module for each component based on the
                # formatted import statement string.
                create_module = importlib.import_module(component_module_name)
                # instance the MainCreate class which is the base of each rig
                # component.
                main_create = create_module.MainCreate()
                # build each component
                main_create.build_from_operator(op_m_data, rig_m_data)

    def connect_components(self):
        """
        Will connect all input and outputs of each component.
        """
        if not self.operators_meta_data:
            logger.log(
                level="error", message="No operators meta data " "accessible"
            )
            return False
        logger.log(
            level="info",
            message="### Connect component inputs and outputs. " "###",
            logger=_LOGGER,
        )
        # loop trough the operators_meta_data.
        for dic in self.operators_meta_data:
            # get the meta data form dic.
            meta_data = dic.get(constants.META_DATA_DIC_ITEM_1)
            for data in meta_data:
                # try to get the parent meta data node.
                parent_meta_nd = data.get(constants.META_MAIN_PARENT_ND)
                # if parent meta data node exist go further.
                if parent_meta_nd:
                    # check if the parent_meta_nd is a meta node.
                    # If  not i guess it is already JoMRS uuid string.
                    if isinstance(parent_meta_nd, meta.MainOpMetaNode):
                        # get the parent meta uuid data.
                        parent_meta_nd_ui = parent_meta_nd.get_uuid()
                    else:
                        # guess the instance is JoMRS uuid string.
                        parent_meta_nd_ui = parent_meta_nd
                    # refactor the parent meta nd uuid to component meta nd
                    # uuid.
                    parent_component_container_uuid = strings.search_and_replace(
                        parent_meta_nd_ui,
                        constants.MAIN_OP_ND_UUID_SUFFIX,
                        constants.COMP_CONTAINER_UUID_SUFFIX,
                    )
                    # get the parent component container nd based on the
                    # refactored parent meta nd uuid.
                    parent_component_container_nd = self.get_container_node_from_uuid(
                        parent_component_container_uuid
                    )
                    # refactor the child meta nd uuid to component meta nd
                    # uuid.
                    child_component_container_uuid = strings.search_and_replace(
                        data.get(constants.UUID_ATTR_NAME),
                        constants.MAIN_OP_ND_UUID_SUFFIX,
                        constants.COMP_CONTAINER_UUID_SUFFIX,
                    )
                    # get the child component container nd based on the
                    # refactored child meta nd uuid.
                    child_component_container_nd = self.get_container_node_from_uuid(
                        child_component_container_uuid
                    )
                    # parent component instance to get output node.
                    parent_component_instance = components.main.CompContainer(
                        component_container=parent_component_container_nd
                    )
                    # get container content to set container content dic.
                    parent_component_instance.get_container_content()
                    # get the output node from container dic.
                    parent_component_container_nd_output = parent_component_instance.container_content.get(
                        "output"
                    )
                    # child component instance to get output node.
                    child_component_container_instance = components.main.CompContainer(
                        component_container=child_component_container_nd
                    )
                    # get container content to set container content dic.
                    child_component_container_instance.get_container_content()
                    # get the input node from container dic.
                    child_component_container_nd_input = child_component_container_instance.container_content.get(
                        "input"
                    )
                    # connect the output and input node.
                    parent_component_container_nd_output.attr(
                        "{}[{}]".format(
                            constants.OUTPUT_WS_PORT_NAME,
                            data.get(constants.PARENT_OUTPUT_WS_PORT_INDEX),
                        )
                    ).connect(
                        child_component_container_nd_input.attr(
                            "{}[0]".format(constants.INPUT_WS_PORT_NAME)
                        )
                    )

    def connect_components_inputs_with_components_rig_offsets_grp(self):
        """
        Connect the component inputs with the component rig offsets of each
        created component. This step has to be always after
        self.connect_components() method.
        """
        if not self.operators_meta_data:
            logger.log(
                level="error", message="No operators meta data " "accessible"
            )
            return False
        logger.log(
            level="info",
            message="### Connect the components inputs with the components rig "
            "offsets grp. ###",
            logger=_LOGGER,
        )
        # loop through the operators_meta_data
        for dic in self.operators_meta_data:
            # get the meta_data
            meta_data = dic.get(constants.META_DATA_DIC_ITEM_1)
            for data in meta_data:
                # get the main_op_uuid
                main_op_uuid = data.get(constants.UUID_ATTR_NAME)
                comp_container = self.get_component_container_from_main_op_nd_uuid(
                    main_op_uuid
                )
                # Create the component instance for further use
                comp_container_instance = components.main.CompContainer(
                    component_container=comp_container
                )
                # Get the component input node.
                comp_container_instance.get_container_content()
                comp_container_input = comp_container_instance.container_content.get(
                    "input"
                )
                # Get rig offset node from the container meta nd.
                rig_ws_offset_nd = (
                    comp_container_instance.get_input_ws_matrix_offset_nd()
                )
                # For each node in rig_ws_offset_nd create a matrix constraint.
                for index, node in enumerate(rig_ws_offset_nd):
                    mul_ma_nd = mayautils.create_matrix_constraint(
                        source=node,
                        target=comp_container_input,
                        maintain_offset=True,
                        target_plug="{}[{}]".format(
                            constants.INPUT_WS_PORT_NAME, str(index)
                        ),
                    )
                    decomp_nd = mul_ma_nd.matrixSum.connections()
                    offset_nd = mul_ma_nd.matrixIn[0].connections()
                    matrix_constraint_nodes = [mul_ma_nd, decomp_nd, offset_nd]
                    # add all content matrix nodes to the container.
                    for node in matrix_constraint_nodes:
                        comp_container_instance.container.addNode(node)

    def arrange_deformation_hierarchy(self):
        """
        Will build the deformation rig hierarchy.
        """
        if not self.operators_meta_data:
            logger.log(
                level="error", message="No operators meta data " "accessible"
            )
            return False
        logger.log(
            level="info",
            message="### Collect all component BND hierarchies and arrange it "
            "to a deformation single hierarchy. ###",
            logger=_LOGGER,
        )
        # loop through the parent data dic.
        for dic in self.parenting_data_dic:
            temp = []
            rig_container_uuid = dic.get(constants.RIG_CONTAINER_UUID_DIC_KEY)
            comp_container_uuid_list = dic.get(
                constants.COMP_CONTAINER_UUID_DIC_KEY
            )
            rig_container_nd = self.get_container_node_from_uuid(
                rig_container_uuid
            )
            # If no rig container node exist fail.
            if not rig_container_nd:
                logger.log(
                    level="error",
                    message="No rig container with "
                    "uuid: {} exist.".format(rig_container_uuid),
                    logger=_LOGGER,
                )
                return False
            rig_container_instance = RigContainer(
                rig_container=rig_container_nd
            )
            # get rig container content.
            rig_container_instance.get_container_content()
            # get the rig key.
            rig_key = [
                key
                for key in rig_container_instance.container_content.keys()
                if "_RIG_" in key
            ]
            rig_key = [key for key in rig_key if "_GRP" in key][0]
            # get the "M_RIG_0_GRP" container.
            m_rig_container_grp = rig_container_instance.container_content.get(
                rig_key
            )
            # loop through the component uuid list.
            for comp_con_uuid in comp_container_uuid_list:
                # get each component container.
                component_container = self.get_container_node_from_uuid(
                    comp_con_uuid
                )
                comp_container_instance = components.main.CompContainer(
                    component_container=component_container
                )
                # get the bnd root node from component
                bnd_root_node = comp_container_instance.get_bnd_root_nd()
                # at the bnd root to temp list.
                if bnd_root_node:
                    temp.append(bnd_root_node)
            if temp:
                # use temp list for hierarchy creation.
                mayautils.create_hierarchy(temp, True)
                # add the rig hierarchy root node to the rig container. The last
                # object in the temp list is always the rig hierarchy root node.
                m_rig_container_grp.addNode(temp)

    def parent_components(self):
        """
        Add the rig components to the components sibling node of the rig
        container. Based on the parenting_data_dic dictionary.
        """
        logger.log(
            level="info",
            message="### Add rig components to rig container. " "###",
            logger=_LOGGER,
        )
        for data_dic in self.parenting_data_dic:
            # Filter the rig container in the scene based on his JoMRS uuid.
            rig_container_nd = self.get_container_node_from_uuid(
                data_dic.get(constants.RIG_CONTAINER_UUID_DIC_KEY)
            )
            rig_container_nd = RigContainer(rig_container=rig_container_nd)
            # add rig components to rig container
            for comp_container_uuid in data_dic.get(
                constants.COMP_CONTAINER_UUID_DIC_KEY
            ):
                comp_container = self.get_container_node_from_uuid(
                    comp_container_uuid
                )
                rig_container_nd.add_rig_component(comp_container)

    def execute_building_steps(
        self,
        rig_meta_data=None,
        operator_meta_data=None,
        component_parenting_data=None,
        save_meta_data_json=True,
    ):
        """
        Execute all rig building steps.

        Args:
            rig_meta_data(List): Filled with dict.
            operator_meta_data(List): Filled with dict.
            component_parenting_data(List): Filled with dict.
            save_meta_data_json(bool): Save the current build as json meta
            data file in the rig package temp folder as backup.

        """
        self.get_meta_data(rig_meta_data, operator_meta_data)
        self.process_component_parenting_data(component_parenting_data)
        self.build_rig_container()
        self.build_components()
        self.connect_components()
        self.connect_components_inputs_with_components_rig_offsets_grp()
        self.parent_components()
        self.arrange_deformation_hierarchy()
        if save_meta_data_json:
            self.save_meta_data_as_json()

    def get_root_meta_nd_from_god_meta_node(self):
        """
        Return all root meta nodes from god meta node.

        Returns:
            List: All root meta nodes connected to the god meta node.
            None if fail.

        """
        # If no god meta node stored, store it.
        if not self.god_meta_nd:
            self.get_god_meta_nd_from_scene()
        # Return all root meta nodes.
        if self.god_meta_nd:
            return self.god_meta_nd.list_meta_nodes(
                class_filter=constants.META_TYPE_A
            )

    def get_operators_meta_data_from_root_meta_node(self, root_meta_nd=None):
        """
        Gives back all operators meta data from operators root node. And
        store it the "self.operators_meta_data()" variable.

        Args:
            root_meta_nd(pmc.PyNode, optional): Root meta node.

        Returns:
            List: Filled with a dictionary for each root_meta_nd.
            [{constants.META_DATA_DIC_ITEM_0:pmc.PyNode(),
            constants.META_DATA_DIC_ITEM_1:List}]

        """
        meta_data = []
        # Get all main meta nodes from root meta node as dictionaries.
        main_meta_nodes_data = self.get_main_meta_nodes_from_root_meta_node(
            root_meta_nd
        )
        # Filter the meta nodes from the dic.
        main_meta_nodes = main_meta_nodes_data.get("main_meta_nodes")
        # Filter the root meta nodes from the dic.
        root_meta_nd = main_meta_nodes_data.get(constants.META_DATA_DIC_ITEM_0)
        # if main meta nodes exist. Get the operators meta data and store it
        # in a list.
        if main_meta_nodes:
            # get each main operator node from each main_op_meta node.
            all_main_op_nodes = [
                meta_node.get_main_op_nd() for meta_node in main_meta_nodes
            ]
            # Store component class instance and pass the main_op_node. So we
            # can use the get_operator_meta_data() method. The we store the
            # operator_meta_data dic in the meta_data list.
            for main_op_nd in all_main_op_nodes:
                component_instance = components.main.Component(
                    main_operator_node=main_op_nd
                )
                component_instance.get_operator_meta_data()
                meta_data.append(component_instance.operator_meta_data)
        self.operators_meta_data = [
            {
                constants.META_DATA_DIC_ITEM_0: root_meta_nd,
                constants.META_DATA_DIC_ITEM_1: meta_data,
            }
        ]
        return [
            {
                constants.META_DATA_DIC_ITEM_0: root_meta_nd,
                constants.META_DATA_DIC_ITEM_1: meta_data,
            }
        ]

    def get_rig_meta_data_from_root_meta_node(self, root_meta_nd=None):
        """
        Get rig meta data from root meta node.

        Args:
            root_meta_nd(pmc.PyNode, optional): Root meta node.

        """
        # If no root_meta_nd stored get the selected JoMRS node and from
        # there get the root_meta_nd.
        if not root_meta_nd:
            if self.component_instance.root_meta_nd:
                root_meta_nd = self.component_instance.root_meta_nd
            else:
                logger.log(
                    level="error",
                    message="Need a selected JoMRS node " "in the scene",
                    logger=_LOGGER,
                )
                return False
        # Get the operator_root_node from root_meta_no. Then create a
        # component class instance and pass the operators_root_nd. So we are
        # able to use the "get_rig_meta_data()" class and store the
        # rig_meta_data dic.
        operator_root_node = root_meta_nd.get_root_op_nd()
        component_instance = components.main.Component(
            operators_root_node=operator_root_node
        )
        component_instance.get_rig_meta_data()
        self.rig_meta_data = [
            {
                constants.META_DATA_DIC_ITEM_0: root_meta_nd,
                constants.META_DATA_DIC_ITEM_1: component_instance.rig_meta_data,
            }
        ]
        return self.rig_meta_data

    def get_main_meta_nodes_from_root_meta_node(self, root_meta_nd=None):
        """
        Get all main meta nodes from root meta nd.

        Args:
            root_meta_nd(pmc.PyNode, optional): Root meta node.

        Returns:
            Dict: ALl connected meta_nodes.
            {constants.META_DATA_DIC_ITEM_0:pmc.PyNode(), "main_meta_nodes":List}
            False if fail.

        """
        if not root_meta_nd:
            if self.component_instance.root_meta_nd:
                root_meta_nd = self.component_instance.root_meta_nd
            else:
                logger.log(
                    level="error",
                    message="Need a selected JoMRS node " "in the scene",
                    logger=_LOGGER,
                )
                return False
        return {
            constants.META_DATA_DIC_ITEM_0: root_meta_nd,
            "main_meta_nodes": root_meta_nd.get_main_meta_nodes(),
        }

    def get_god_meta_nd_from_scene(self):
        """
        Get the scene meta node.

        Returns:
            pmc.PyNode(): The god network node.

        """
        temp = pmc.ls(typ="network")
        # Filter the JoMRS meta nodes from all found network nodes.
        for node in temp:
            if (
                node.hasAttr(constants.META_NODE_ID)
                and node.attr(constants.META_NODE_ID).get() is True
                and node.attr(constants.META_TYPE).get()
                == constants.META_GOD_TYPE
            ):
                self.god_meta_nd.append(node)
        # Be sure that only one god_meta_nd exist.
        if self.god_meta_nd:
            if len(self.god_meta_nd) > 1:
                logger.log(
                    level="error",
                    message="More then one god meta node in the scene not allowed.",
                    logger=_LOGGER,
                )
                self.god_meta_nd = None
                return False
            self.god_meta_nd = self.god_meta_nd[0]
            return True
        logger.log(
            level="error",
            message="No god meta node in the scene",
            logger=_LOGGER,
        )
        return False

    def get_meta_data_from_all_root_meta_nodes_in_scene(self, meta_data_type):
        """
        Collect the meta data from all root meta nodes in the scene.

        Args:
            meta_data_type(str): Defines meta data type to collect.
            Valid values are ['operators', 'rig']

        Returns:
            List: Filled with a dictionary for each root_meta_nd.
            [{constants.META_DATA_DIC_ITEM_0:pmc.PyNode(),
            constants.META_DATA_DIC_ITEM_1:List}]

        """
        result = []
        all_root_nodes = self.get_root_meta_nd_from_god_meta_node()
        if meta_data_type == "operators":
            for root_meta_node in all_root_nodes:
                self.get_operators_meta_data_from_root_meta_node(root_meta_node)
                result.append(self.operators_meta_data[0])
            self.operators_meta_data = result
        elif meta_data_type == "rig":
            for root_meta_node in all_root_nodes:
                self.get_rig_meta_data_from_root_meta_node(root_meta_node)
                result.append(self.rig_meta_data[0])
            self.rig_meta_data = result
        return result

    @staticmethod
    def get_container_node_from_uuid(uuid_):
        """
        Get a container from JoMRS uuid.

        Args:
            uuid_(str): The uuid for the node to search for

        Return:
            pmc.PyNode(): If successful. None if fail.

        """
        result = None
        # Get all container nodes in the scene.
        scene_containers = pmc.ls(containers=True)
        for container in scene_containers:
            # Create a container class instance so we are able to use the
            # get_uuid() method.
            container_instance = mayautils.ContainerNode(
                container_node=container
            )
            try:
                # Use a try and except to get the uuid because not every
                # container node has the uuid stored as meta data. And we are
                # only interested for the nodes with this meta data.
                if container_instance.get_uuid() == uuid_:
                    result = container_instance.container
            except:
                continue
        return result

    def get_component_container_from_main_op_nd_uuid(self, main_op_uuid):
        """
        Gives back the component_container node form main_op_nd_uuid.

        Args:
            main_op_uuid(str): The main op nd uuid.

        Returns:
            pmc.PyNode() if successful. False if not.

        """
        # reformat the main_op_nd_uuid to comp_container_uuid
        comp_container_uuid = strings.search_and_replace(
            main_op_uuid,
            constants.MAIN_OP_ND_UUID_SUFFIX,
            constants.COMP_CONTAINER_UUID_SUFFIX,
        )
        # Get the component container from reformatted uuid.
        comp_container = self.get_container_node_from_uuid(comp_container_uuid)
        if not comp_container:
            logger.log(
                level="error",
                message="Component container "
                "with {} uuid "
                "not exist.".format(comp_container_uuid),
            )
            return False
        return comp_container

    def get_rig_containers_from_scene(self):
        """
        Gives back all rig containers from scene based on the god meta node.

        Returns:
            List: All found meta nodes. None if fail

        """
        rig_containers = []
        if not self.god_meta_nd:
            self.get_god_meta_nd_from_scene()
        if self.god_meta_nd:
            containers_meta_nd = self.god_meta_nd.list_meta_nodes(
                class_filter=constants.META_TYPE_D
            )
            if containers_meta_nd:
                for meta_nd in containers_meta_nd:
                    if (
                        meta_nd.get_container_type()
                        == constants.RIG_CONTAINER_TYPE
                    ):
                        rig_containers.append(meta_nd.get_container_node())
        return rig_containers

    def save_meta_data_as_json(self):
        """
        Save the operators_meta data as json file in temp folder.
        """
        operators_meta_data = (
            self.refactor_operators_meta_data_for_json_export()
        )
        rig_meta_data = self.refactor_rig_meta_data_for_json_export()
        data = {
            "operators_meta_data": operators_meta_data,
            "rig_meta_data": rig_meta_data,
            "parenting_data_dic": self.parenting_data_dic,
        }
        with open(
            os.path.normpath(
                "{}/temp/latest_rig_build.json".format(
                    constants.BUILD_JSON_PATH
                )
            ),
            "w",
        ) as json_file:
            json.dump(data, json_file, sort_keys=True, indent=4)

    def refactor_operators_meta_data_for_json_export(self):
        """
        Refactor the operators_meta so that it can be exported as json file.
        Its mainly refactor all PyMel related stuff to json serializable
        formats.

        Returns:
            List: The refactored list.

        """
        # Create a deepcopy of the meta data list to keep the stored meta
        # data in memory untouched.
        meta_data_list = copy.deepcopy(self.operators_meta_data)
        for dic in meta_data_list:
            root_meta_nd = dic.get(constants.META_DATA_DIC_ITEM_0)
            dic[constants.META_DATA_DIC_ITEM_0] = root_meta_nd.name()
            meta_data = dic.get(constants.META_DATA_DIC_ITEM_1)
            for data in meta_data:
                # Get stuff for json refactor. That is stuff which is PyMel
                # related and can not be json serialized.
                connect_nd = data.get(constants.META_MAIN_CONNECT_ND)
                parent_nd = data.get(constants.META_MAIN_PARENT_ND)
                child_nd = data.get(constants.META_MAIN_CHILD_ND)
                main_op_ws_matrix = data.get(
                    constants.META_MAIN_OP_ND_WS_MATRIX_STR
                )
                lra_nd_ws_matrix = data.get(constants.META_LRA_ND_WS_MATRIX_STR)
                sub_lra_nd_ws_matrix = data.get(
                    constants.META_SUB_LRA_ND_WS_MATRIX_STR
                )
                sub_op_ws_matrix = data.get(
                    constants.META_SUB_OP_ND_WS_MATRIX_STR
                )
                # Get all pmc.PyNodes() and refactor them to JoMRS uuids.
                if connect_nd:
                    data[constants.META_MAIN_CONNECT_ND] = connect_nd.get_uuid()
                if parent_nd:
                    data[constants.META_MAIN_PARENT_ND] = parent_nd.get_uuid()
                if child_nd:
                    data[constants.META_MAIN_CHILD_ND] = [
                        node.get_uuid() for node in child_nd
                    ]
                # Get all PyMel Matrix Objects to refactor them to nested lists.
                if main_op_ws_matrix:
                    data[constants.META_MAIN_OP_ND_WS_MATRIX_STR] = [
                        list(mat) for mat in main_op_ws_matrix
                    ]
                if lra_nd_ws_matrix:
                    data[constants.META_LRA_ND_WS_MATRIX_STR] = [
                        list(mat) for mat in lra_nd_ws_matrix
                    ]
                if sub_lra_nd_ws_matrix:
                    data[constants.META_SUB_LRA_ND_WS_MATRIX_STR] = [
                        list(mat) for mat in sub_lra_nd_ws_matrix
                    ]
                # The sub operators objects are special because for each
                # sub_operators node you will find a Matrix Object in the
                # list. That is why we have to loop twice.
                if sub_op_ws_matrix:
                    sub_op_ws_matrix_temp_list = [
                        list(mat) for mat in sub_op_ws_matrix
                    ]
                    data[constants.META_SUB_OP_ND_WS_MATRIX_STR] = [
                        list(mat) for mat in sub_op_ws_matrix_temp_list
                    ]
        return meta_data_list

    @staticmethod
    def refactor_operators_meta_data_from_json_import(json_data):
        """
        Refactor back all needed PyMel objects in json dictionary.

        Args:
            json_data(dic): Th imported json data dic.

        Returns:
            Dictionary: The refactored dictionary.

        """
        operators_meta_data = json_data.get("operators_meta_data")
        for dic in operators_meta_data:
            meta_data = dic.get(constants.META_DATA_DIC_ITEM_1)
            for data in meta_data:
                # Find all world matrix lists.
                main_op_nd_ws_matrix = data.get(
                    constants.META_MAIN_OP_ND_WS_MATRIX_STR
                )
                lra_nd_ws_matrix = data.get(constants.META_LRA_ND_WS_MATRIX_STR)
                sub_lra_nd_ws_matrix = data.get(
                    constants.META_SUB_LRA_ND_WS_MATRIX_STR
                )
                sub_op_nd_ws_matrix = data.get(
                    constants.META_SUB_OP_ND_WS_MATRIX_STR
                )
                # Refactor all ws matrix lists to a PyMel Matrix object.
                if main_op_nd_ws_matrix:
                    data[constants.META_MAIN_OP_ND_WS_MATRIX_STR] = dt.Matrix(
                        main_op_nd_ws_matrix
                    )
                if lra_nd_ws_matrix:
                    data[constants.META_LRA_ND_WS_MATRIX_STR] = dt.Matrix(
                        lra_nd_ws_matrix
                    )
                if sub_lra_nd_ws_matrix:
                    data[constants.META_SUB_LRA_ND_WS_MATRIX_STR] = [
                        dt.Matrix(sub_lra_nd)
                        for sub_lra_nd in sub_lra_nd_ws_matrix
                    ]
                if sub_op_nd_ws_matrix:
                    data[constants.META_SUB_OP_ND_WS_MATRIX_STR] = [
                        dt.Matrix(sub) for sub in sub_op_nd_ws_matrix
                    ]
        json_data["operators_meta_data"] = operators_meta_data
        return json_data

    def refactor_rig_meta_data_for_json_export(self):
        """
        Refactor the rig_meta so that it can be exported as json file.
        Its mainly refactor all PyMel related stuff to json serializable
        formats.

        Returns:
            List: The refactored list.

        """
        rig_meta_data = copy.deepcopy(self.rig_meta_data)
        for dic in rig_meta_data:
            root_meta_nd = dic.get(constants.META_DATA_DIC_ITEM_0)
            dic[constants.META_DATA_DIC_ITEM_0] = root_meta_nd.name()
        return rig_meta_data

    @staticmethod
    def load_json_rig_build_file(file_path=None):
        """
        Load the rig build meta data from json file.
        If no file_path is given it will take the latest rig build json file
        from the package temp folder.

        Args:
            file_path(str): The file_path to the json file.

        Returns:
             Dictionary: The meta data dic.

        """
        if not file_path:
            file_path = os.path.normpath(
                "{}/temp/latest_rig_build.json".format(
                    constants.BUILD_JSON_PATH
                )
            )
        with open(file_path) as json_file:
            data = json.load(json_file)
        return data

    def build_from_json_file(self, file_path=None):
        """
        Build the rig based on a json_file. If no file_path is given it will
        take the latest rig build json file from the package temp folder.
        """
        json_data = self.load_json_rig_build_file(file_path)
        json_data = self.refactor_operators_meta_data_from_json_import(
            json_data
        )
        self.execute_building_steps(
            json_data.get("rig_meta_data"),
            json_data.get("operators_meta_data"),
            json_data.get("parenting_data_dic"),
            False,
        )


class RigContainer(mayautils.ContainerNode):
    """
    Create a container node designed for the rig content.
    """

    CONTENT_GROUPS = [
        "M_RIG_0_GRP",
        "M_COMPONENTS_0_GRP",
        "M_GEO_0_GRP",
        "M_BSHP_0_GRP",
        "M_SHARED_ATTR_0_GRP",
        "M_NO_TRANSFORM_0_GRP",
    ]

    def __init__(self, rig_name=None, rig_container=None):
        """
        Args
            rig_name(str): The rig name.
            rig_container(pmc.PyNode()): A rig container to pass.

        """
        super(RigContainer, self).__init__()
        self.meta_nd_name = constants.RIG_META_NODE_NAME
        self.name = constants.RIG_ROOT_NODE
        self.icon = os.path.normpath(
            "{}/rig_hierarchy_logo.png".format(constants.ICONS_PATH)
        )
        self.container = rig_container
        if not self.container:
            if rig_name:
                self.name = self.name.replace("name", rig_name)
                self.name = strings.string_checkup(self.name)

    def create_transform(self, name):
        """
        Overwritten method from base class. It use a container node instead
        of a simple transform.

        Args:
            name(str): Container name.

        """
        self.container_content[name] = pmc.nt.Container(n=name)
        self.container.addNode(
            self.container_content[name], ish=True, ihb=True, iha=True, inc=True
        )
        # Check if a container node with the same name exist.
        # If so the new created container get a number in the suffix as maya
        # standard procedure. Then we take that and put it at the correct place
        # in our naming convention.
        container_content_name = strings.normalize_suffix_1(
            self.container_content[name].name(), logger_=_LOGGER
        )
        self.container_content[name].rename(container_content_name)

    def add_node_to_container_content(self, node, content_name):
        """
        Overwritten base class method. Add node to container content.

        Args:
            node(pmc.PyNode()): The node to add.
            content_name(str): The content node.

        """
        self.container_content.get(content_name).addNode(
            node, ish=True, ihb=True, iha=True, inc=True
        )

    def create_rig_container(self):
        """
        Create the rig container.
        """
        self.create_container()
        self.create_container_content_from_list(self.CONTENT_GROUPS)
        self.set_container_type(constants.RIG_CONTAINER_TYPE)

    def add_rig_component(self, rig_component=None):
        """
        Add rig component to rig container.

        Args:
            rig_component(pmc.PyNode()): The rig component node.

        """
        # Get container content
        self.get_container_content()
        # Filter the component group
        keys = self.container_content.keys()
        component_key = [
            comp_key
            for comp_key in keys
            if strings.search("COMPONENTS", comp_key)
        ][0]
        # Add rig component node to component sibling of the rig container.
        self.add_node_to_container_content(rig_component, component_key)

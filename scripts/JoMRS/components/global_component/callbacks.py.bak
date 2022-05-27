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
Module for callback creation fro this component
"""

import pymel.core as pmc
from pymel.core.system import Namespace
from maya.api import OpenMaya as om2
import logging

#########################################################################
# GLOBALS
#########################################################################

logging.basicConfig(level=logging.INFO)

#########################################################################
# CLASSES
#########################################################################


class ChangePivotCallback(object):
    """
    OpenMaya callback class. It will change the pivot of the cop control to
    specified position.
    """

    META_ND_TAG = "meta_node"
    CHANGE_PIVOT_ATTR = "change_pivot"
    RESET_PIVOT_ATTR = "reset_pivot"
    CHANGE_PIVOT_TSR_REF_META_ATTR = "change_pivot_tsr"
    RESET_PIVOT_TSR_REF_META_ATTR = "reset_pivot_tsr"
    CHANGE_PIVOT_CONTROL_CURVE = "change_pivot_control"
    LOCAL_CON_REF_META_ATTR = "local_control"
    COP_CONTROL_CURVE = "cop_control_curve"
    GOD_META_ND_NAME = "god_meta_0_METAND"
    GOD_META_CLASS = "god_meta_class"
    META_NODES_ARRAY_ATTR_NAME = "meta_nodes"
    META_CLASS_ATTR = "meta_class"
    COMP_TYPE = "global_control_component"
    COMP_TYPE_ATTR_NAME = "component_type"
    CONTAINER_TYPE_ATTR_NAME = "container_type"
    CONTAINER_TYPE = "COMP"
    CONTAINER_ND_ATTR_NAME = "container_nd"
    DIRTY_EVAL_ATTR = "dirty"

    def __init__(self):
        self.god_meta_nodes = []
        self.meta_nodes = []
        self.reset_pivot_attr_value = None
        self.reset_pivot_ref_node = None
        self.change_pivot_control_curve = None
        self.change_pivot_tsr = None
        self.local_control_curve = None
        self.cop_control_curve = None
        self.container_nd = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_god_meta_nodes_in_scene(self):
        """
        Get the god meta nodes in the scene.
        """
        namespace = Namespace(":")
        nmsp_list = namespace.listNamespaces(recursive=True)
        temp_0 = []
        temp_1 = []
        if nmsp_list:
            for nmsp in nmsp_list:
                temp_0.append("{}:{}".format(nmsp, self.GOD_META_ND_NAME))
        else:
            temp_0.append(self.GOD_META_ND_NAME)
        for node in temp_0:
            try:
                temp_1.append(pmc.PyNode(node))
            except:
                continue
        temp_1 = [
            node
            for node in temp_1
            if node.hasAttr(self.META_CLASS_ATTR)
            and node.attr(self.META_CLASS_ATTR).get() == self.GOD_META_CLASS
        ]
        temp_1 = [
            node
            for node in temp_1
            if node.hasAttr(self.META_ND_TAG)
            and node.attr(self.META_ND_TAG).get() is True
        ]
        if not temp_1:
            raise NameError(
                'No network node with the name "{}" '
                "exist".format(self.GOD_META_ND_NAME)
            )
        self.god_meta_nodes = temp_1

    def get_component_meta_nodes(self):
        """
        Get component meta node from god_meta_nd.
        """
        self.get_god_meta_nodes_in_scene()
        for god_meta_nd in self.god_meta_nodes:
            self.meta_nodes = [
                meta_nd
                for meta_nd in god_meta_nd.attr(
                    self.META_NODES_ARRAY_ATTR_NAME
                ).get()
                if meta_nd.attr(self.META_ND_TAG).get() is True
                and meta_nd.hasAttr(self.CONTAINER_TYPE_ATTR_NAME)
                and meta_nd.attr(self.CONTAINER_TYPE_ATTR_NAME).get()
                == self.CONTAINER_TYPE
                and meta_nd.hasAttr(self.COMP_TYPE_ATTR_NAME)
                and meta_nd.attr(self.COMP_TYPE_ATTR_NAME).get()
                == self.COMP_TYPE
            ]

    def get_all_important_nodes_from_meta_nd(self, meta_nd):
        """
        Get all important nodes from meta nd.

        Args:
            meta_nd(pmc.PyNode()): The component meta_nd.

        """
        self.reset_pivot_ref_node = meta_nd.attr(
            self.RESET_PIVOT_TSR_REF_META_ATTR
        ).get()
        self.change_pivot_control_curve = meta_nd.attr(
            self.CHANGE_PIVOT_CONTROL_CURVE
        ).get()
        self.change_pivot_tsr = meta_nd.attr(
            self.CHANGE_PIVOT_TSR_REF_META_ATTR
        ).get()
        self.local_control_curve = meta_nd.attr(
            self.LOCAL_CON_REF_META_ATTR
        ).get()
        self.cop_control_curve = meta_nd.attr(self.COP_CONTROL_CURVE).get()
        self.container_nd = meta_nd.attr(self.CONTAINER_ND_ATTR_NAME).get()

    def cop_reset_pivot(self, meta_nd):
        """
        Reset pivot control curve back to default position.

        Args:
            meta_nd(pmc.PyNode()): The component meta_nd.

        """
        self.get_all_important_nodes_from_meta_nd(meta_nd)
        reset_pivot_attr_value = meta_nd.attr(self.RESET_PIVOT_ATTR).get()
        if reset_pivot_attr_value:
            self.local_control_curve.addChild(self.change_pivot_tsr)
            self.change_pivot_control_curve.setMatrix(
                self.reset_pivot_ref_node.getMatrix(worldSpace=True),
                worldSpace=True,
            )
            self.cop_control_curve.addChild(self.change_pivot_tsr)
            self.change_pivot_tsr.translate.set(0, 0, 0)
            self.change_pivot_tsr.rotate.set(0, 0, 0)
            self.change_pivot_tsr.scale.set(1, 1, 1)
            pmc.select(self.change_pivot_control_curve)

    def cop_change_pivot(self, meta_nd):
        """
        Unparent the change pivot tsr. So we are able to offset the cop control.

        Args:
            meta_nd(pmc.PyNode()): The component meta_nd.

        """
        self.get_all_important_nodes_from_meta_nd(meta_nd)
        change_pivot_attr_value = meta_nd.attr(self.CHANGE_PIVOT_ATTR).get()
        if change_pivot_attr_value:
            try:
                self.local_control_curve.addChild(self.change_pivot_tsr)
            except Exception as e:
                print(
                    "{}: Change pivot tsr is already a child of {}.".format(
                        e, self.local_control_curve
                    )
                )
        else:
            try:
                self.cop_control_curve.addChild(self.change_pivot_tsr)
            except Exception as e:
                print(
                    "{}: Change pivot tsr is already a child of {}.".format(
                        e, self.cop_control_curve
                    )
                )
        pmc.select(self.change_pivot_control_curve)

    @staticmethod
    def remove_callbacks_from_node(node_mob):
        """
        Remove all callback stick to a node.

        Args:
            node_mob(MObject): The node to remove all node
                               callbacks from.

        Return:
            Int: Number of callbacks removed

        """
        cbs = om2.MMessage.nodeCallbacks(node_mob)
        cb_count = len(cbs)
        for eachCB in cbs:
            om2.MMessage.removeCallback(eachCB)
        return cb_count

    def callback_(self, msg, plug1, plug2, payload):
        """
        Open Maya API callback function. Execute the real callback.

        Args:
            msg(MMessage): The message given back from the API.
            plug1(MPlug): The first triggered plug of the node.
            plug2(MPlug): The second triggered plug of the node.
            payload(): clientData pass in argument.

        Return:
            The message and the plug of the triggered node.
            False if plug not exist.

        """
        # Check if a plug of the channelbox is triggered. If not fall out.
        if msg != 2056:
            return
        # Check if the attribute we want is triggered. If not fall out.
        if (
            plug1.partialName(includeNodeName=False, useAlias=False)
            == self.CHANGE_PIVOT_ATTR
        ):
            self.cop_change_pivot(meta_nd=payload)
        elif (
            plug1.partialName(includeNodeName=False, useAlias=False)
            == self.RESET_PIVOT_ATTR
        ):
            self.cop_reset_pivot(meta_nd=payload)
        else:
            return False

    def init_pivot_callback(self):
        """
        Initialize the callback.
        """
        # Check if the component meta node exist. If not fall out.
        self.get_component_meta_nodes()
        if not self.meta_nodes:
            raise IndexError(
                'No meta node with the type "{}" exist'.format(self.COMP_TYPE)
            )
        for meta_nd in self.meta_nodes:
            self.get_all_important_nodes_from_meta_nd(meta_nd)
            # Get callback node.
            callback_node = meta_nd.attr(
                self.CHANGE_PIVOT_CONTROL_CURVE
            ).get()
            # MSelection Object of the callback node
            sel = om2.MSelectionList()
            sel.add(str(callback_node))
            settings_mob = sel.getDependNode(0)
            # Remove callback if exist.
            callback_count = self.remove_callbacks_from_node(settings_mob)
            self.logger.info(
                "Component : {} / Callbacks removed: {}".format(
                    self.container_nd, callback_count
                )
            )
            om2.MNodeMessage.addAttributeChangedCallback(
                settings_mob, self.callback_, meta_nd
            )
            self.logger.info(
                "Component : {} / Callback applied to: {}".format(
                    self.container_nd, callback_node
                )
            )

    def undirty_eval_meta_nodes(self):
        """
        Set the eval mode of all component meta nodes to undirty.
        """
        self.get_component_meta_nodes()
        if not self.meta_nodes:
            raise IndexError(
                'No meta node with the type "{}" exist'.format(self.COMP_TYPE)
            )
        for meta_nd in self.meta_nodes:
            if meta_nd.attr(self.DIRTY_EVAL_ATTR).get():
                meta_nd.attr(self.DIRTY_EVAL_ATTR).set(0)
                self.logger.info(
                    "Component : {} / {} tagged as undirty eval.".format(
                        self.container_nd, meta_nd)
                )


#########################################################################
# CALLBACK CLASS AS STRING VARIABLES
#########################################################################

BEFORE_CHANGE_PIV_SCRIPT_NODE_STR = """
import pymel.core as pmc
from pymel.core.system import Namespace
from maya.api import OpenMaya as om2
import logging

#########################################################################
# GLOBALS
#########################################################################

logging.basicConfig(level=logging.INFO)

#########################################################################
# CLASSES
#########################################################################


class ChangePivotCallback(object):
    META_ND_TAG = "meta_node"
    CHANGE_PIVOT_ATTR = "change_pivot"
    RESET_PIVOT_ATTR = "reset_pivot"
    CHANGE_PIVOT_TSR_REF_META_ATTR = "change_pivot_tsr"
    RESET_PIVOT_TSR_REF_META_ATTR = "reset_pivot_tsr"
    CHANGE_PIVOT_CONTROL_CURVE = "change_pivot_control"
    LOCAL_CON_REF_META_ATTR = "local_control"
    COP_CONTROL_CURVE = "cop_control_curve"
    GOD_META_ND_NAME = "god_meta_0_METAND"
    GOD_META_CLASS = "god_meta_class"
    META_NODES_ARRAY_ATTR_NAME = "meta_nodes"
    META_CLASS_ATTR = "meta_class"
    COMP_TYPE = "global_control_component"
    COMP_TYPE_ATTR_NAME = "component_type"
    CONTAINER_TYPE_ATTR_NAME = "container_type"
    CONTAINER_TYPE = "COMP"
    CONTAINER_ND_ATTR_NAME = "container_nd"
    DIRTY_EVAL_ATTR = "dirty"

    def __init__(self):
        self.god_meta_nodes = []
        self.meta_nodes = []
        self.reset_pivot_attr_value = None
        self.reset_pivot_ref_node = None
        self.change_pivot_control_curve = None
        self.change_pivot_tsr = None
        self.local_control_curve = None
        self.cop_control_curve = None
        self.container_nd = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_god_meta_nodes_in_scene(self):
        namespace = Namespace(":")
        nmsp_list = namespace.listNamespaces(recursive=True)
        temp_0 = []
        temp_1 = []
        if nmsp_list:
            for nmsp in nmsp_list:
                temp_0.append("{}:{}".format(nmsp, self.GOD_META_ND_NAME))
        else:
            temp_0.append(self.GOD_META_ND_NAME)
        for node in temp_0:
            try:
                temp_1.append(pmc.PyNode(node))
            except:
                continue
        temp_1 = [
            node
            for node in temp_1
            if node.hasAttr(self.META_CLASS_ATTR)
            and node.attr(self.META_CLASS_ATTR).get() == self.GOD_META_CLASS
        ]
        temp_1 = [
            node
            for node in temp_1
            if node.hasAttr(self.META_ND_TAG)
            and node.attr(self.META_ND_TAG).get() is True
        ]
        if not temp_1:
            raise NameError(
                'No network node with the name "{}" '
                "exist".format(self.GOD_META_ND_NAME)
            )
        self.god_meta_nodes = temp_1

    def get_component_meta_nodes(self):
        self.get_god_meta_nodes_in_scene()
        for god_meta_nd in self.god_meta_nodes:
            self.meta_nodes = [
                meta_nd
                for meta_nd in god_meta_nd.attr(
                    self.META_NODES_ARRAY_ATTR_NAME
                ).get()
                if meta_nd.attr(self.META_ND_TAG).get() is True
                and meta_nd.hasAttr(self.CONTAINER_TYPE_ATTR_NAME)
                and meta_nd.attr(self.CONTAINER_TYPE_ATTR_NAME).get()
                == self.CONTAINER_TYPE
                and meta_nd.hasAttr(self.COMP_TYPE_ATTR_NAME)
                and meta_nd.attr(self.COMP_TYPE_ATTR_NAME).get()
                == self.COMP_TYPE
            ]

    def get_all_important_nodes_from_meta_nd(self, meta_nd):
        self.reset_pivot_ref_node = meta_nd.attr(
            self.RESET_PIVOT_TSR_REF_META_ATTR
        ).get()
        self.change_pivot_control_curve = meta_nd.attr(
            self.CHANGE_PIVOT_CONTROL_CURVE
        ).get()
        self.change_pivot_tsr = meta_nd.attr(
            self.CHANGE_PIVOT_TSR_REF_META_ATTR
        ).get()
        self.local_control_curve = meta_nd.attr(
            self.LOCAL_CON_REF_META_ATTR
        ).get()
        self.cop_control_curve = meta_nd.attr(self.COP_CONTROL_CURVE).get()
        self.container_nd = meta_nd.attr(self.CONTAINER_ND_ATTR_NAME).get()

    def cop_reset_pivot(self, meta_nd):
        self.get_all_important_nodes_from_meta_nd(meta_nd)
        reset_pivot_attr_value = meta_nd.attr(self.RESET_PIVOT_ATTR).get()
        if reset_pivot_attr_value:
            self.local_control_curve.addChild(self.change_pivot_tsr)
            self.change_pivot_control_curve.setMatrix(
                self.reset_pivot_ref_node.getMatrix(worldSpace=True),
                worldSpace=True,
            )
            self.cop_control_curve.addChild(self.change_pivot_tsr)
            self.change_pivot_tsr.translate.set(0, 0, 0)
            self.change_pivot_tsr.rotate.set(0, 0, 0)
            self.change_pivot_tsr.scale.set(1, 1, 1)
            pmc.select(self.change_pivot_control_curve)

    def cop_change_pivot(self, meta_nd):
        self.get_all_important_nodes_from_meta_nd(meta_nd)
        change_pivot_attr_value = meta_nd.attr(self.CHANGE_PIVOT_ATTR).get()
        if change_pivot_attr_value:
            try:
                self.local_control_curve.addChild(self.change_pivot_tsr)
            except Exception as e:
                print(
                    "{}: Change pivot tsr is already a child of {}.".format(
                        e, self.local_control_curve
                    )
                )
        else:
            try:
                self.cop_control_curve.addChild(self.change_pivot_tsr)
            except Exception as e:
                print(
                    "{}: Change pivot tsr is already a child of {}.".format(
                        e, self.cop_control_curve
                    )
                )
        pmc.select(self.change_pivot_control_curve)

    @staticmethod
    def remove_callbacks_from_node(node_mob):
        cbs = om2.MMessage.nodeCallbacks(node_mob)
        cb_count = len(cbs)
        for eachCB in cbs:
            om2.MMessage.removeCallback(eachCB)
        return cb_count

    def callback_(self, msg, plug1, plug2, payload):
        # Check if a plug of the channelbox is triggered. If not fall out.
        if msg != 2056:
            return
        # Check if the attribute we want is triggered. If not fall out.
        if (
            plug1.partialName(includeNodeName=False, useAlias=False)
            == self.CHANGE_PIVOT_ATTR
        ):
            self.cop_change_pivot(meta_nd=payload)
        elif (
            plug1.partialName(includeNodeName=False, useAlias=False)
            == self.RESET_PIVOT_ATTR
        ):
            self.cop_reset_pivot(meta_nd=payload)
        else:
            return False

    def init_pivot_callback(self):
        # Check if the component meta node exist. If not fall out.
        self.get_component_meta_nodes()
        if not self.meta_nodes:
            raise IndexError(
                'No meta node with the type "{}" exist'.format(self.COMP_TYPE)
            )
        for meta_nd in self.meta_nodes:
            self.get_all_important_nodes_from_meta_nd(meta_nd)
            # Get callback node.
            callback_node = meta_nd.attr(
                self.CHANGE_PIVOT_CONTROL_CURVE
            ).get()
            # MSelection Object of the callback node
            sel = om2.MSelectionList()
            sel.add(str(callback_node))
            settings_mob = sel.getDependNode(0)
            # Remove callback if exist.
            callback_count = self.remove_callbacks_from_node(settings_mob)
            self.logger.info(
                "Component : {} / Callbacks removed: {}".format(
                    self.container_nd, callback_count
                )
            )
            om2.MNodeMessage.addAttributeChangedCallback(
                settings_mob, self.callback_, meta_nd
            )
            self.logger.info(
                "Component : {} / Callback applied to: {}".format(
                    self.container_nd, callback_node
                )
            )

    def undirty_eval_meta_nodes(self):
        self.get_component_meta_nodes()
        if not self.meta_nodes:
            raise IndexError(
                'No meta node with the type "{}" exist'.format(self.COMP_TYPE)
            )
        for meta_nd in self.meta_nodes:
            if meta_nd.attr(self.DIRTY_EVAL_ATTR).get():
                meta_nd.attr(self.DIRTY_EVAL_ATTR).set(0)
                self.logger.info(
                    "Component : {} / {} tagged as undirty eval.".format(
                        self.container_nd, meta_nd)
                )

change_pivot_cbs = ChangePivotCallback()
change_pivot_cbs.init_pivot_callback()
"""
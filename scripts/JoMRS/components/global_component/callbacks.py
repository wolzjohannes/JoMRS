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
Module for callback creation fro this component
"""

import pymel.core as pmc
import pymel.core.datatypes as dt
from pymel.core.system import Namespace
from maya.api import OpenMaya as om2

#########################################################################
# CLASSES
#########################################################################


class ChangePivotCallback(object):
    """
    OpenMaya callback class. It will change the pivot of the cop control tp
    specified position.
    """
    META_ND_TAG = "meta_node"
    CHANGE_PIVOT_ATTR = "change_pivot"
    RESET_PIVOT_ATTR = "reset_pivot"
    GOD_META_ND_NAME = "god_meta_0_METAND"
    GOD_META_CLASS = "god_meta_class"
    META_NODES_ARRAY_ATTR_NAME = "meta_nodes"
    META_CLASS_ATTR = "meta_class"
    COMP_TYPE = "global_control_component"
    COMP_TYPE_ATTR_NAME = "component_type"
    CONTAINER_TYPE_ATTR_NAME = "container_type"
    CONTAINER_TYPE = "COMP"
    DIRTY_EVAL_ATTR = "dirty"

    def __init__(self):
        self.meta_nd = None
        self.god_meta_nodes = []
        self.meta_nodes = []

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

    def calculate_matrix_offset(self, target, source):
        """Calculate the matrix offset of the source to the target.
        Args:
                target(PyNode): The target node.
                source(PyNode): The source node.
        Retruns:
                The offset matrix values from target to source.
        """
        tm = dt.Matrix(target.getMatrix(ws=True)).inverse()
        sm = dt.Matrix(source.getMatrix(ws=True))
        return sm.__mul__(tm)

    def cop_reset_pivot(self, meta_node):
        """
        Set the offset matrix to the default reset matrix.
        Args:
                meta_node(dagnode): The network node with component
                meta data.
        """
        reset_pivot = meta_node.reset_pivot.get()
        ref_node = meta_node.ref_end_node.get()
        ref_node_matrix_ui = ref_node.getChildren(typ='transform')[0]
        if reset_pivot:
            ref_node_matrix_ui.offset_matrix.set(
                ref_node_matrix_ui.reset_matrix.get())

    def cop_change_pivot(self, meta_node):
        """
        Disconnect the ref node from cop control. And calculate offset.
        Then reconnect the ref node.
        Args:
                meta_node(dagnode): The network node with component
                meta data.
        """
        decomp_node_attr = ['outputTranslate', 'outputRotate',
                            'outputScale']
        change_pivot = meta_node.change_pivot.get()
        ref_node = meta_node.ref_end_node.get()
        ref_node_matrix_ui = ref_node.getChildren(typ='transform')[0]
        decomp_node = ref_node.decomp_node.get()
        control = meta_node.main_control.get()
        if change_pivot:
            for attr_ in decomp_node_attr:
                decomp_node.attr(attr_).disconnect()
            control.getChildren(typ='transform')[0].getShape().visibility.set(0)
            return
        ref_node_matrix_ui.offset_matrix.set(
            calculate_matrix_offset(control, ref_node))
        control.getChildren(typ='transform')[0].getShape().visibility.set(1)
        for attr_ in decomp_node_attr:
            decomp_node.attr(attr_).connect(
                ref_node.attr(attr_.split('output')[1].lower()))
#
    def removeCallbacksFromNode(self, node_mob):
        """
        Remove all callback stick to a node.
        Args:
                node_mob(MObject): The node to remove all node
                                   callbacks from.
        Return:
                Int: Number of callbacks removed
        """
        cbs = om2.MMessage.nodeCallbacks(node_mob)
        cbCount = len(cbs)
        for eachCB in cbs:
            om2.MMessage.removeCallback(eachCB)
        return cbCount
#
    def callback_(self, msg, plug1, plug2, payload):
        """
        Open Maya API callback function. Exectue the real callback.
        Args:
                msg(MMessage): The message given back from the API.
                plug1(MPlug): The first triggered plug of the node.
                plug2(MPlug): The second triggered plug of the node.
                payload(): clientData pass in argument.
        Return:
                The message and the plug of the triggered node.
        """
        changepivot_attr = CHANGEPIVOTATTR
        # Check if a plug of the channelbox is triggered. If not fall out.
        if msg != 2056:
            return
        #Check if the attribute we want is triggered. If not fall out.
        if plug1.partialName(includeNodeName=False, useAlias=False) == changepivot_attr[0]:
            cop_change_pivot(meta_node=payload)
        elif plug1.partialName(includeNodeName=False, useAlias=False) == changepivot_attr[1]:
            cop_reset_pivot(meta_node=payload)
        else:
            return

    def init_pivot_callback(self):
        """
        Initialize the callback.
        """
        # Check if the component meta node exist. If not fall out.
        meta_nodes = get_component_meta_nodes()
        if not meta_nodes:
            raise IndexError('No network nodes with meta data to work with')
            return
        for node in meta_nodes:
            callback_node = node.main_control.get()
            sel = om2.MSelectionList()
            sel.add(str(callback_node))
            settingsMob = sel.getDependNode(0)
            callback_count = removeCallbacksFromNode(settingsMob)
            print '// INFO: change_pivot callbacks removed:', callback_count
            om2.MNodeMessage.addAttributeChangedCallback(settingsMob,
                callback_, node)
            print '// INFO: change_pivot callback applied to', callback_node
#
#
# init_pivot_callback()

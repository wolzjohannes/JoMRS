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
# Date:       2019 / 07 / 02

"""
Meta creation module.
"""
import pymel.all as pmc
import logging
import attributes
import re

##########################################################
# GLOBALS
#########################################################
module_logger = logging.getLogger(__name__ + ".py")
NODEID = 'meta_node'
TYPE = 'meta_name'
BASETYPE = 'meta_class'
GODTYPE = 'god_meta_class'
TYPEA = 'god_operator_meta_class'
##########################################################
# CLASSES
##########################################################


class MetaNode(pmc.nt.Network):
    """
    Creates a network node which works as MetaNode node.
    """

    @classmethod
    def list(cls, *args, **kwargs):
        """ Returns all instances the node in the scene """

        kwargs['type'] = cls.__melnode__
        return [node for node in pmc.ls(*args, **kwargs) if
                isinstance(node, cls)]

    @classmethod
    def _isVirtual(cls, obj, name, tag=NODEID):
        """"
        This actual creates the node. If a specific tag is found.
        If not it will create a default node.
        PyMEL code should not be used inside the callback,
        only API and maya.cmds.
        """
        fn = pmc.api.MFnDependencyNode(obj)
        try:
            if fn.hasAttribute(tag):
                plug = fn.findPlug(tag)
                if plug.asBool() == 1:
                    return True
                return False
        except:
            pass
        return False

    @classmethod
    def _preCreateVirtual(cls, **kwargs):
        """This is called before creation. python allowed."""
        return kwargs

    @classmethod
    def _postCreateVirtual(cls, newNode, tag=NODEID, type=TYPE,
                           class_type=BASETYPE):
        """
        This is called after creation, pymel/cmds allowed.
        It will create a set of attributes. And the important check up tag for
        the meta node.
        """
        newNode.addAttr(tag, at='bool')
        newNode.attr(tag).set(1)
        newNode.addAttr(type, dt='string')
        newNode.attr(type).set(class_type)

class GodMetaNode(MetaNode):
    """
    Creates a Meta Node as God Meta Node for all operators meta nodes.
    """
    SUBNODE_TYPE = GODTYPE
    METAND = []

    @classmethod
    def list(cls, *args, **kwargs):
        """ Returns all instances of all characters in the scene """

        kwargs['type'] = cls.__melnode__
        return [node for node in pmc.ls(*args, **kwargs) if
                isinstance(node, cls)]

    @classmethod
    def _isVirtual(cls, obj, name, tag=NODEID, type=TYPE):
        """"
        This actual creates the node. If a specific tag is found.
        If not it will create a default node.
        PyMEL code should not be used inside the callback,
        only API and maya.cmds.
        """
        fn = pmc.api.MFnDependencyNode(obj)
        try:
            if fn.hasAttribute(tag):
                plug = fn.findPlug(tag)
                if plug.asBool() == 1:
                    if fn.hasAttribute(type):
                        plug = fn.findPlug(type)
                        if plug.asString() == cls.SUBNODE_TYPE:
                            return True
                    return False
        except:
            pass
        return False

    @classmethod
    def _postCreateVirtual(cls, newNode, type=TYPE, name='god_meta_0_METAND'):
        """ This is called before creation, pymel/cmds allowed."""
        MetaNode._postCreateVirtual(newNode)
        newNode.attr(type).set(cls.SUBNODE_TYPE)
        newNode.rename(name)
        cls.METAND.append(newNode)

    def add_meta_node(self, node, metand=METAND, plug='meta_node'):
        new_attribute = {}
        ud_attr = metand[0].listAttr(ud=True)
        meta_plug = [str(attr_) for attr_ in ud_attr if re.search(str(attr_),
                                                                plug)]
        if not meta_plug:
            new_attribute["name"] = "{}_0".format(plug)
            new_attribute["attrType"] = "message"
            new_attribute["keyable"] = False
            new_attribute["channelBox"] = False
            new_attribute["input"] = node.message
        attributes.add_attr(node=metand[0], **new_attribute)


class GodOpMetaNode(MetaNode):
    """
    Creates a Meta Node as God Meta Node for all operators meta nodes.
    """
    SUBNODE_TYPE = TYPEA

    @classmethod
    def list(cls, *args, **kwargs):
        """ Returns all instances of all characters in the scene """

        kwargs['type'] = cls.__melnode__
        return [node for node in pmc.ls(*args, **kwargs) if
                isinstance(node, cls)]

    @classmethod
    def _isVirtual(cls, obj, name, tag=NODEID, type=TYPE):
        """"
        This actual creates the node. If a specific tag is found.
        If not it will create a default node.
        PyMEL code should not be used inside the callback,
        only API and maya.cmds.
        """
        fn = pmc.api.MFnDependencyNode(obj)
        try:
            if fn.hasAttribute(tag):
                plug = fn.findPlug(tag)
                if plug.asBool() == 1:
                    if fn.hasAttribute(type):
                        plug = fn.findPlug(type)
                        if plug.asString() == cls.SUBNODE_TYPE:
                            return True
                    return False
        except:
            pass
        return False

    @classmethod
    def _postCreateVirtual(cls, newNode, type=TYPE, name='god_meta_0_METAND'):
        """ This is called before creation, pymel/cmds allowed."""
        MetaNode._postCreateVirtual(newNode)
        try:
            god_mata_nd = pmc.PyNode(name)
        except:
            god_mata_nd = GodMetaNode()
        newNode.attr(type).set(cls.SUBNODE_TYPE)
        god_mata_nd.add_meta_node(node=newNode)

        rigname_attr = {
            "name": "rig_name",
            "attrType": "string",
            "keyable": False,
        }

        l_ik_rig_color_attr = {
            "name": "l_ik_rig_color",
            "attrType": "long",
            "keyable": False,
            "defaultValue": 13,
            "minValue": 0,
            "maxValue": 31,
        }

        l_ik_rig_sub_color_attr = {
            "name": "l_ik_rig_sub_color",
            "attrType": "long",
            "keyable": False,
            "defaultValue": 18,
            "minValue": 0,
            "maxValue": 31,
        }

        r_ik_rig_color_attr = {
            "name": "r_ik_rig_color",
            "attrType": "long",
            "keyable": False,
            "defaultValue": 6,
            "minValue": 0,
            "maxValue": 31,
        }

        r_ik_rig_sub_color_attr = {
            "name": "r_ik_rig_sub_color",
            "attrType": "long",
            "keyable": False,
            "defaultValue": 9,
            "minValue": 0,
            "maxValue": 31,
        }

        m_ik_rig_color_attr = {
            "name": "m_ik_rig_color",
            "attrType": "long",
            "keyable": False,
            "defaultValue": 17,
            "minValue": 0,
            "maxValue": 31,
        }

        m_ik_rig_sub_color_attr = {
            "name": "m_ik_rig_sub_color",
            "attrType": "long",
            "keyable": False,
            "defaultValue": 11,
            "minValue": 0,
            "maxValue": 31,
        }

        main_op_nodes_attr = {
            "name": "main_op_nodes",
            "attrType": "message",
            "keyable": False,
            "channelBox": False,
        }

        root_node_param_list = [
            rigname_attr,
            l_ik_rig_color_attr,
            l_ik_rig_sub_color_attr,
            r_ik_rig_color_attr,
            r_ik_rig_sub_color_attr,
            m_ik_rig_color_attr,
            m_ik_rig_sub_color_attr,
            main_op_nodes_attr,
        ]
        for attr_ in root_node_param_list:
            attributes.add_attr(node=newNode, **attr_)



pmc.factories.registerVirtualClass( MetaNode, nameRequired=False )
pmc.factories.registerVirtualClass( GodMetaNode, nameRequired=False )
pmc.factories.registerVirtualClass( GodOpMetaNode, nameRequired=False )
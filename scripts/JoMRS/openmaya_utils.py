# Copyright (c) 2022 Johannes Wolz

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Author:     Johannes Wolz / Rigging TD
# Date:       2022 / 08 / 08

"""
Utils code to manage openMaya workflows.
"""

# Import Maya specific modules
import pymel.core
from maya import OpenMaya

##########################################################
# FUNCTIONS
##########################################################


def get_m_object(node):
    """
    Gives back an MObject.

    Args:
        node(str, pymel.core.PyNode()): The nodes name as
                                        string or as
                                        pymel.core.PyNode object.

    Return:
        OpenMaya.MObject: For given node.

    """
    if isinstance(node, pymel.core.PyNode):
        return node.__apimobject__()
    elif isinstance(node, str):
        try:
            om_sel = OpenMaya.MSelectionList()
            om_sel.add(node)
            node = OpenMaya.MObject()
            om_sel.getDependNode(0, node)
            return node
        except:
            raise RuntimeError(
                "Unable to get MObject from given string: {}".format(node)
            )
    else:
        return node


def get_dag_path(node, type):
    """
    Gives back the DAG path on an given node.

    Args:
        node(str): The nodes unique name.
        type(OpenMaya node type): For example: OpenMaya.MFn.kMesh.

    Return:
         OpenMaya dag_path object.

    """
    om_sel = OpenMaya.MSelectionList()
    om_sel.add(node)
    iter_sel = OpenMaya.MItSelectionList(om_sel, type)
    dag_path = OpenMaya.MDagPath()
    iter_sel.getDagPath(dag_path)
    return dag_path


def get_m_obj_array(objects):
    """
    Returns the objects as MObjectArray.

    Args:
        objects(list): List filled with objects names as string.

    Return:
        OpenMaya.MObjectArray.

    """
    m_array = OpenMaya.MObjectArray()
    for idx, obj in enumerate(objects):
        m_array.insert(get_m_object(obj), idx)
    return m_array


def rename_node(object, new_name):
    """
    Rename a node.

    Args:
        object(str, OpenMaya.MObject): Nodes name.
        new_name(str): New name.

    Return:
        String: New node name.

    """
    print(isinstance(object, str))
    if isinstance(object, str):
        m_obj = get_m_object(object)
    elif isinstance(object, OpenMaya.MObject):
        m_obj = object
    else:
        raise TypeError(
            "{} is a not supported object type. You need a string or a "
            "OpenMaya.MObject".format(object)
        )
    m_dag_mod = OpenMaya.MDagModifier()
    m_dag_mod.renameNode(m_obj, new_name)
    m_dag_mod.doIt()
    return new_name

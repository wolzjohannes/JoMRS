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
# Date:       2022 / 08 / 22

"""
Util module for blendShape data management.
With the utils functions you can mainly export and import whole blendShape
setups. But it contains even functions to edit and create blendShape nodes and
targets.
The export data dict is called 'blendshape_data_dict'. This will be reused a
lot of times in a lot of functions and looks like this:

{
    "base_obj_export": "blendShape1_base_geo.obj",
    "blendshape_node_info": {
        "history_location": 0,
        "name": "blendShape1",
        "origin": 0,
        "topologyCheck": true
    },
    "mesh_data": {
        "mesh_shape": "pSphere1Shape",
        "num_polys": 1000000,
        "num_vertices": 999002,
        "poly_vertex_id_list": "blendShape1_poly_vertex_id.npy",
        "verts_ws_pos_list": "blendShape1_verts_ws_positions.npy"
    },
    "target_deltas": [
        {
            "inbetween_deltas": [
                {
                    "5542": {
                        "name": "pSphere2_0.542",
                        "target_components":
                        "blendShape1_inbetween_deltas_0_5542.npz",
                        "target_points":
                        "blendShape1_inbetween_deltas_0_5542.npz",
                        "weight": 0.542
                    }
                }
            ],
            "target_deltas": "blendShape1_deltas_0.npz",
            "target_index": 0,
            "target_name": "pSphere2"
        },
        {
            "inbetween_deltas": [],
            "target_deltas": "blendShape1_deltas_1.npz",
            "target_index": 1,
            "target_name": "pSphere3"
        }
    ],
    "weights_connections_data": []
}

"""

# Import python standart import
import logging
import os
import json
import numpy
import importlib
import glob

# Import Maya specific modules
import pymel.core
import maya.cmds as cmds
from maya import OpenMaya
from maya import OpenMayaAnim

# Import local modules
import decorators
import openmaya_utils
import mesh_utils
import wrap_utils

importlib.reload(openmaya_utils)
importlib.reload(mesh_utils)

##########################################################
# GLOBALS
##########################################################

_LOGGER = logging.getLogger(__name__ + ".py")
_LOGGER.setLevel(logging.INFO)
DECORATORS = decorators.Decorators()
DECORATORS.debug = True
DECORATORS.logger = _LOGGER


_BLENDSHAPE_INFO_DICT = {
    "origin": [
        (OpenMayaAnim.MFnBlendShapeDeformer.kLocalOrigin, {"origin": "local"}),
        (OpenMayaAnim.MFnBlendShapeDeformer.kWorldOrigin, {"origin": "world"}),
    ],
    "historyLocation": [
        (
            OpenMayaAnim.MFnBlendShapeDeformer.kFrontOfChain,
            {"frontOfChain": True},
        ),
        (OpenMayaAnim.MFnBlendShapeDeformer.kNormal, {"automatic": True}),
        (OpenMayaAnim.MFnBlendShapeDeformer.kPost, {"after": True}),
        (OpenMayaAnim.MFnBlendShapeDeformer.kOther, {"afterReference": True}),
    ],
}

##########################################################
# FUNCTIONS
##########################################################


def get_blendshape_node_infos(blendshape_node):
    """
    Get infos from given blendshape node.

    Args:
        blendshape_node(str): Blendshape node name.

    Return:
         Dict: {
        "name": blendshape_node,
        "history_location": blendshape_fn.historyLocation(),
        "origin": blendshape_fn.origin(),
        "topologCheck": bool
        }
    """
    blendshape_fn = get_blendshape_fn(blendshape_node)
    top_check_m_plug = blendshape_fn.findPlug("topologyCheck")
    return {
        "name": blendshape_node,
        "history_location": blendshape_fn.historyLocation(),
        "origin": blendshape_fn.origin(),
        "topologyCheck": top_check_m_plug.asBool(),
    }


def get_weight_connections_data(blendshape_node):
    """
    Get the connected nodes name and the connected plugs from all weight plugs.

    Args:
        blendshape_node(str): Blendshape node name.

    Return:
         List: [((node_name, node_plug_name), weight_name),
                ((node_name, node_plug_name), weight_name)]

    """
    result = []
    blendshape_fn = get_blendshape_fn(blendshape_node)
    weight_plug = blendshape_fn.findPlug("weight")
    for x in range(weight_plug.numElements()):
        plug = weight_plug.elementByPhysicalIndex(x)
        if plug.isConnected():
            source_nd_name, source_plug_name = plug.source().name().split(".")
            data_tuple = (
                (source_nd_name, source_plug_name),
                plug.partialName(False, False, False, True),
            )
            result.append(data_tuple)
    return result


def get_blendshape_nodes(
    node, as_string=True, as_pynode=False, as_fn=False, levels=1
):
    """
    Get all source blendshape nodes from given shape node.

    Args:
        node(str, pymel.core..PyNode()): Mesh shape node.
        as_string(bool): Give nodes names back.
        as_pynode(bool): Give PyNodes back.
        as_fn(bool): Give OpenMaya.MFnBlendShapeDeformer back.
        levels(int): The number of given back blendshape nodes found in
                     connected history.

    Return:
        List: All found blendshape nodes.

    """
    if isinstance(node, str):
        node = pymel.core.PyNode(node)
    bshp_nodes = node.listHistory(
        type="blendShape", allFuture=False, future=False, levels=levels
    )
    if as_pynode:
        return bshp_nodes
    if as_fn:
        return [get_blendshape_fn(node.nodeName()) for node in bshp_nodes]
    if as_string:
        return [node.nodeName() for node in bshp_nodes]


def is_blendshape_node(node):
    """
    Gives back if given node is a blendshape node.

    Args:
        node(str): Name of the node to check.
    
    Return:
        Bool: True/False

    """
    m_object = openmaya_utils.get_m_object(node)
    return bool(m_object.hasFn(OpenMaya.MFn.kBlendShape))


def get_blendshape_fn(blendshape_node):
    """
    Get the OpenMaya.MFnBlendshapeDeformer from given blendshape node name.

    Args:
        blendshape_node(str): Blendshape node name.

    Return:
         OpenMaya.MFnBlendshapeDeformer.

    """
    m_object = openmaya_utils.get_m_object(blendshape_node)
    if is_blendshape_node(m_object):
        return OpenMayaAnim.MFnBlendShapeDeformer(m_object)


def get_weight_indexes(blendshape_node):
    """
    Get all weight indexes from given blendshape node.

    Args:
        blendshape_node(str): Blendshape node name.

    Return:
         List: All found weight indexes.

    """
    blendshape_fn = get_blendshape_fn(blendshape_node)
    m_int_array = OpenMaya.MIntArray()
    blendshape_fn.weightIndexList(m_int_array)
    return m_int_array


def get_base_objects(blendshape_node):
    """
    Get all base objects from given blendshape node.
    The base object is the shape node connected to the
    blendshape deformer.

    Args:
        blendshape_node(str): Blendshape node name.

    Return:
        Tuple: OpenMaya.MFnMesh objects.

    """
    if not isinstance(blendshape_node, pymel.core.PyNode):
        bshp_node = pymel.core.PyNode(blendshape_node)
    base_objects_list = bshp_node.getBaseObjects()
    base_object_tuple = tuple([node.__apimfn__() for node in base_objects_list])
    return base_object_tuple


def get_weight_names(blendshape_node):
    """
    Get the weight attribute names from given blendshape node.

    Args:
        blendshape_node(str): Blendshape node name.

    Return:
        Tuple: All found weight names. Empty if None.

    """
    weight_names = []
    blendshape_fn = get_blendshape_fn(blendshape_node)
    weight_plug = blendshape_fn.findPlug("weight")
    for x in range(weight_plug.numElements()):
        plug = weight_plug.elementByPhysicalIndex(x)
        weight_names.append(plug.partialName(False, False, False, True))
    return tuple(weight_names)


def get_weight_from_inbetween_plug_index(plug_index):
    """
    Get the weight value from given inbetween plug index.

    Args:
        plug_index(int): The index of the inbetween plug

    Return:
        Float: The weight value.

    """
    return float("0.{}".format(str(plug_index)[1:]))


def target_index_exists(blendshape_node, index):
    """
    Check if given target index exist.

    Args:
        blendshape_node(str): Blendshape node name.
        index(int): Index to check for.

    Return:
         Bool: True or False

    """
    indexes = get_weight_indexes(blendshape_node)
    if index in indexes:
        return True
    return False


def get_weight_name_from_index(
    blendshape_node, index, partial_name=False, as_m_object_attr=False
):
    """
    Get weight alias name from given index.

    Args:
        blendshape_node(str): Blendshape node name.
        index(int): The Index to search for.
        partial_name(bool): Gives back as weight name.
        as_m_object_attr: gives back as openMaya.MPlug.Attribute.

    Return:
         String: Weight name
         OpenMaya.MPlug.Attribute object.
         None if weight name not exist at given index.

    """
    blendshape_fn = get_blendshape_fn(blendshape_node)
    weight_plug = blendshape_fn.findPlug("weight")
    try:
        plug = weight_plug.elementByPhysicalIndex(index)
        weight_name = plug.partialName(False, False, False, True)
        if not partial_name:
            weight_name = plug.name()
        if as_m_object_attr:
            weight_name = plug.attribute()
        return weight_name
    except:
        return None


def get_inbetween_values_from_target_index(blendshape_node, index):
    result = []
    inbetween_list = get_inbetween_plugs(blendshape_node, index)
    if inbetween_list:
        result = [
            get_weight_from_inbetween_plug_index(list(in_dict.keys()))[0]
            for in_dict in inbetween_list
        ]
    return result


def rename_weight_name_from_index(blendshape_node, index, new_name):
    """
    Rename weight name found on given index.

    Args:
        blendshape_node(str): Blendshape node name.
        index(int): The Index to search for.
        new_name(str): The new name.

    """
    attribute_from_index = get_weight_name_from_index(blendshape_node, index)
    alias_attributes = [
        attr
        for attr in cmds.aliasAttr(blendshape_node, query=True)
        if "weight" not in attr
    ]
    similar_attributes = [attr for attr in alias_attributes if new_name in attr]
    if similar_attributes:
        new_name = "{}{}".format(new_name, len(similar_attributes))
    cmds.aliasAttr(new_name, attribute_from_index)


def add_target(
    blendshape_node,
    index=None,
    target="new_target",
    weight=1.0,
    is_inbetween=False,
    target_m_object=False,
):
    """
    Add a new empty target to blendshape node.

    Args:
        blendshape_node(str): Blendshape node name.
        index(int): The target index.
        target(str, OpenMaya.MObject): Target name or new target with deltas..
        weight(float): The maximum weight the target will have an effect.
        is_inbetween(bool): Define if new target is an inbetween. If it is
                            the index number will define to which
                             target the inbetween belongs to.

    Return:
        True if succeed.

    """
    blendshape_fn = get_blendshape_fn(blendshape_node)
    base_obj = get_base_objects(blendshape_node)[0]
    base_m_object = openmaya_utils.get_m_object(str(base_obj.name()))
    input_target_array_plug_count = _get_input_target_array_plug_count(
        blendshape_node
    )
    if is_inbetween:
        if target_index_exists(blendshape_node, index):
            if weight == 0.0 or weight == 1.0:
                raise AttributeError(
                    "Weight param can not be 0.0 or 1.0 if you add an "
                    "inbetween."
                )
            blendshape_fn.addTarget(base_m_object, index, weight)
            return True
        else:
            raise IndexError("Target index not exist. Unable to add inbetween.")
    if weight < 1.0 and weight > 0.0:
        raise AttributeError(
            "Weights between 0.0 and 1.0 can just be used as inbetween target."
        )
    if isinstance(target, str):
        blendshape_fn.addTarget(
            base_m_object, input_target_array_plug_count, weight
        )
        rename_weight_name_from_index(
            blendshape_node,
            input_target_array_plug_count,
            target_m_object,
            target,
        )
        return True
    blendshape_fn.addTarget(
        base_m_object, input_target_array_plug_count, target, weight
    )
    DAG_modifier = OpenMaya.MDGModifier()
    DAG_modifier.deleteNode(target)
    return True


@DECORATORS.x_timer
def create_blendshape_node(
    geo_transform,
    name=None,
    origin_enum=0,
    history_location_enum=1,
    targets_list=None,
    inbetweens_list=None,
    topologyCheck=True,
):
    """
    Create a new blendshape node.

    Args:
        geo_transform(str, pymel.core.PyNode()): The transform node of the
                                                 geo for the blendshape node
        name(str): Name of the blendshape node. If None will take maya
                   default naming. Default is None.
        origin_enum(int): Enum index in _BLENDSHAPE_INFO_DICT["origin"] for
                          the spaces of the deformation origin. Default is
                          kLocalOrigin.
        history_location_enum(int): Enum index in
                                    _BLENDSHAPE_INFO_DICT["historyLocation"]
                                    for the place in the deformation order of
                                    the mesh.
                                    Default is kNormal("automatic").
        targets_list(list): List with names(str) or OpenMaya.MObjects for the
                            targets of the node. The order of the list is the
                            index order of the targets.
                            Will just add targets if the list is not None.
                            By default is None.
        inbetweens_list(List): The List to add inbetweens.It has to be filled
                               with this template:
                               [
                               {"target_points": points array,
                                 "target_components": components array,
                                 "name": string or OpenMaya.MObject,
                                 "weight": float}
                                ]
                               The order of the tuples in the list is the index
                               order of the inbetweens belonging.
        topologyCheck(bool): Enable/Disable the topology check of the
                             blendshape node.


    """
    if isinstance(geo_transform, str):
        geo_transform = pymel.core.PyNode(geo_transform)
    mesh_shape_nd_name = [geo_transform.getShape().name(long=None)]
    mesh_shape_m_obj_array = openmaya_utils.get_m_obj_array(mesh_shape_nd_name)
    bshp_fn = OpenMayaAnim.MFnBlendShapeDeformer()
    bshp_fn.create(
        mesh_shape_m_obj_array,
        _BLENDSHAPE_INFO_DICT.get("origin")[origin_enum][0],
        _BLENDSHAPE_INFO_DICT.get("historyLocation")[history_location_enum][0],
    )
    if name:
        bshp_fn.setName(name)
    if targets_list:
        for index, target in enumerate(targets_list):
            add_target(bshp_fn.name(), index, target)
    if inbetweens_list:
        for index_, list_ in enumerate(inbetweens_list):
            for inbetween_dict in list_:
                dict_items = list(inbetween_dict.items())
                for item in dict_items:
                    add_target(
                        bshp_fn.name(),
                        index_,
                        item[1].get("name"),
                        item[1].get("weight"),
                        True,
                    )
    if topologyCheck:
        pymel.core.PyNode(bshp_fn.name()).topologyCheck.set(True)


@DECORATORS.x_timer
def OM_get_blendshape_deltas_from_index(blendshape_node, index, bshp_port=6000):
    """
    Get the blendshape delta values with openMaya.
    This is really fast if you stay in maya.
    But if you want to export this data, it is really slow.
    This is because of the conversion from the openMaya.MPlug.MObject to an
    array we can use further. For that Maya Commands and Mel is faster.

    Args:
        blendshape_node(str): Blendshape node name.
        index(int): The target index.
        bshp_port(int): Port number of the blendshape target. 6000 represents a
                        weight value of 1.0 and 5000 a value of 0.0. 4000 is
                        -1.0.
                        And everything between 6000, 5000 and 4000 are the
                        inbetween targets.
                        This is because the blendshape node supports inbetweens
                        and minus weight values.
                        Default is 6000.
    Return:
        Tuple: (points position as OpenMaya.MObject, affected components as
                OpenMaya.MObject)

    """
    points_pymel_attr = (
        pymel.core.PyNode(blendshape_node)
        .inputTarget[0]
        .inputTargetGroup[index]
        .inputTargetItem[bshp_port]
        .inputPointsTarget
    )
    points_m_object = points_pymel_attr.__apimplug__().asMObject()
    component_pymel_attr = (
        pymel.core.PyNode(blendshape_node)
        .inputTarget[0]
        .inputTargetGroup[index]
        .inputTargetItem[bshp_port]
        .inputComponentsTarget
    )
    components_m_object = component_pymel_attr.__apimplug__().asMObject()
    return (points_m_object, components_m_object)


@DECORATORS.x_timer
def get_blendshape_deltas_from_index(blendshape_node, index, bshp_port=6000):
    """
    Get the blendshape deltas.

    Args
        blendshape_node(str): Blendshape node name.
        index(int): The target index.
        bshp_port(int): Port number of the blendshape target. 6000 represents a
                        weight value of 1.0 and 5000 a value of 0.0. 4000 is
                        -1.0.
                        And everything between 6000, 5000 and 4000 are the
                        inbetween targets.
                        This is because the blendshape node supports inbetweens
                        and minus weight values.
                        Default is 6000.
    Return:
        Tuple: (points positions as array, affected components as array)

    """
    pt = cmds.getAttr(
        "{}.inputTarget[0].inputTargetGroup[{}].inputTargetItem["
        "{}].inputPointsTarget".format(blendshape_node, index, bshp_port)
    )
    ct = cmds.getAttr(
        "{}.inputTarget[0].inputTargetGroup[{}].inputTargetItem["
        "{}].inputComponentsTarget".format(blendshape_node, index, bshp_port)
    )
    return (pt, ct)


@DECORATORS.x_timer
def OM_set_blendshape_deltas_by_index(
    blendshape_node, index, deltas_tuple, bshp_port=6000
):
    """
    Set the blendshape deltas with OpenMaya.

    Args:
        blendshape_node(str): Blendshape node name.
        index(int): The target index.
        deltas_tuple(tuple): Deltas for setting.
                            (points position as OpenMaya.MObject, affected
                            components as OpenMaya.MObject)
        bshp_port(int): Port number of the blendshape target. 6000 represents a
                        weight value of 1.0 and 5000 a value of 0.0. 4000 is
                        -1.0.
                        And everything between 6000, 5000 and 4000 are the
                        inbetween targets.
                        This is because the blendshape node supports inbetweens
                        and minus weight values.
                        Default is 6000.

    """
    if index not in get_weight_indexes(blendshape_node):
        raise AttributeError("Given index not exist. Will abort.")
    target_points = deltas_tuple[0]
    target_indices = deltas_tuple[1]
    points_pymel_attr = (
        pymel.core.PyNode(blendshape_node)
        .inputTarget[0]
        .inputTargetGroup[index]
        .inputTargetItem[bshp_port]
        .inputPointsTarget
    )
    points_m_plug = points_pymel_attr.__apimplug__()
    points_m_plug.setMObject(target_points)
    component_pymel_attr = (
        pymel.core.PyNode(blendshape_node)
        .inputTarget[0]
        .inputTargetGroup[index]
        .inputTargetItem[bshp_port]
        .inputComponentsTarget
    )
    components_m_plug = component_pymel_attr.__apimplug__()
    components_m_plug.setMObject(target_indices)


@DECORATORS.x_timer
def set_blendshape_deltas_by_index(
    blendshape_node, index, deltas_tuple, bshp_port=6000
):
    """
    Set the bendshape deltas with maya commands.

    Args:
        blendshape_node(str): Blendshape node name.
        index(int): The target index.
        deltas_tuple(tuple): Deltas for setting.
                            (points position as array,
                            affected components as array)
        bshp_port(int): Port number of the blendshape target. 6000 represents a
                        weight value of 1.0 and 5000 a value of 0.0. 4000 is
                        -1.0.
                        And everything between 6000, 5000 and 4000 are the
                        inbetween targets.
                        This is because the blendshape node supports inbetweens
                        and minus weight values.
                        Default is 6000.

    """
    pt = deltas_tuple[0]
    ct = deltas_tuple[1]
    cmds.setAttr(
        "{}.inputTarget[0].inputTargetGroup[{}].inputTargetItem[{}"
        "].inputPointsTarget".format(blendshape_node, index, bshp_port),
        len(pt),
        *pt,
        type="pointArray"
    )
    cmds.setAttr(
        "{}.inputTarget[0].inputTargetGroup[{}].inputTargetItem[{}"
        "].inputComponentsTarget".format(blendshape_node, index, bshp_port),
        len(ct),
        *ct,
        type="componentList"
    )


def is_target_connected(blendshape_node, index, bshp_port):
    """
    Gets if target plug is connected to an mesh shape.

    Args:
        blendshape_node(str): Blendshape node name.
        index(int): The target index.
        deltas_tuple(tuple): Deltas for setting.
                            (points position as array,
                            affected components as array)
        bshp_port(int): Port number of the blendshape target. 6000 represents a
                        weight value of 1.0 and 5000 a value of 0.0. 4000 is
                        -1.0.
                        And everything between 6000, 5000 and 4000 are the
                        inbetween targets.
                        This is because the blendshape node supports inbetweens
                        and minus weight values.
    Return:
        Bool: True or False.

    """
    return (
        pymel.core.PyNode(blendshape_node)
        .inputTarget[0]
        .inputTargetGroup[index]
        .inputTargetItem[bshp_port]
        .isConnected()
    )


def get_inbetween_name_from_bshp_port(blendshape_node, bshp_port):
    """
    Get the inbetween name from given bshp port number.

    Args:
        blendshape_node(str): Blendshape node name.
        bshp_port(int): Port number of the blendshape target. 6000 represents a
                        weight value of 1.0 and 5000 a value of 0.0. 4000 is
                        -1.0.
                        And everything between 6000, 5000 and 4000 are the
                        inbetween targets.
                        This is because the blendshape node supports inbetweens
                        and minus weight values.

    Return:
        None if no inbetween exist at bshp port number.
        String if succeed.

    """
    bshp_fn = get_blendshape_fn(blendshape_node)
    m_plug = bshp_fn.findPlug("inbetweenInfoGroup")
    info_plug = m_plug.elementByPhysicalIndex(0).child(0)
    array_plug_elements_num = info_plug.numElements()
    if array_plug_elements_num:
        for x in range(array_plug_elements_num):
            plug_name = (
                info_plug.elementByPhysicalIndex(x).name().split(".")[-1]
            )
            plug_name = plug_name.split("[")[1].split("]")[0]
            port_index = int(plug_name)
            if bshp_port == port_index:
                p_value = (
                    info_plug.elementByPhysicalIndex(x).child(1).asString()
                )
                return p_value


def get_inbetween_plugs(blendshape_node, index):
    """
    Get all inbetween plug numbers from given target index.

    Args:
        blendshape_node(str): Blendshape node name.
        index(int): The target index.

    Result:
        List: [{port_index: inbetween_name},{5250: "test_inbetween_1"}]
        None if no inbetweens exist.

    """
    result_list = list()
    input_target_group_plug = _get_input_target_group_plug(blendshape_node)
    input_target_item_plug = input_target_group_plug.elementByPhysicalIndex(
        index
    ).child(0)
    array_plug_elements_num = input_target_item_plug.numElements()
    if array_plug_elements_num > 1:
        for x in range(array_plug_elements_num):
            plug_name = (
                input_target_item_plug.elementByPhysicalIndex(x)
                .name()
                .split(".")[-1]
            )
            plug_name = plug_name.split("[")[1].split("]")[0]
            port_index = int(plug_name)
            if port_index != 6000:
                inbetween_name = get_inbetween_name_from_bshp_port(
                    blendshape_node, port_index
                )
                result_list.append({port_index: inbetween_name})
    return result_list


def _get_input_target_group_plug(blendshape_node):
    """
    Get the input target group plug. Where all targets are stored.

    Args:
        blendshape_node(str): Blendshape node name.

    Return:
        OpenMaya.MPlug

    """
    try:
        bshp_fn = get_blendshape_fn(blendshape_node)
        m_plug = bshp_fn.findPlug("inputTarget")
        return m_plug.elementByPhysicalIndex(0).child(0)
    except:
        return (
            pymel.core.PyNode(blendshape_node)
            .inputTarget.inputTarget[0]
            .inputTargetGroup.__apimplug__()
        )


def _get_input_target_array_plug_count(blendshape_node):
    """
    Get the target count by the indices of the array plug on the node.

    Args:
        blendshape_node(str): Blendshape node name.

    Return:
        Integer: Count of the plugs.

    """
    input_target_group_plug = _get_input_target_group_plug(blendshape_node)
    m_int_array = OpenMaya.MIntArray()
    return input_target_group_plug.getExistingArrayAttributeIndices(m_int_array)


def get_targets_and_inbetweens_deltas_from_blendshape(
    blendshape_node, as_MObjects=True
):
    """
    Get all deltas of the all inbetweens and targets from given blendshape node.

    Args:
        blendshape_node(str): Blendshape node name.
        as_MObjects(bool): Get the targets and inbetween deltas as
                           OpenMaya.MObject. This is really fast if you stay
                           in the maya session. And do not use the data for
                           an export. Default is True

    Return:
          List: Filled with a multidimensional dict for each target.
          [{"target_name": string,
            "target_index": Integer,
            "target_deltas": {"target_points": points position array
                              or OpenMaya.MObject,
                              "target_components": affected component array
                              or OpenMaya.MObject}
            "inbetween_deltas": [{bshp_port:
                                 {"target_points": points position array or
                                 OpenMaya.MObject,
                                 "target_components": affected component
                                 array or OpenMaya.MObject, "name": String,
                                 "weight": float},
                                 ]

    """
    target_deltas_list = list()
    index_array = get_weight_indexes(blendshape_node)
    for index in index_array:
        target_temp_dict = dict()
        inbetween_temp_list = list()
        if as_MObjects:
            target_temp_dict["target_points"], target_temp_dict[
                "target_components"
            ] = OM_get_blendshape_deltas_from_index(blendshape_node, index)
        else:
            target_temp_dict["target_points"], target_temp_dict[
                "target_components"
            ] = get_blendshape_deltas_from_index(blendshape_node, index)
        inbetween_plugs = get_inbetween_plugs(blendshape_node, index)
        if inbetween_plugs:
            for inbetween_dict in inbetween_plugs:
                port_index = list(inbetween_dict.keys())[0]
                name = get_inbetween_name_from_bshp_port(
                    blendshape_node, port_index
                )
                weight = get_weight_from_inbetween_plug_index(port_index)
                inbetween_temp_dict = dict()
                if as_MObjects:
                    inbetween_temp_dict["target_points"], inbetween_temp_dict[
                        "target_components"
                    ] = OM_get_blendshape_deltas_from_index(
                        blendshape_node, index, port_index
                    )
                else:
                    inbetween_temp_dict["target_points"], inbetween_temp_dict[
                        "target_components"
                    ] = get_blendshape_deltas_from_index(
                        blendshape_node, index, port_index
                    )
                inbetween_temp_dict["name"] = name
                inbetween_temp_dict["weight"] = weight
                inbetween_temp_list.append({port_index: inbetween_temp_dict})
        target_deltas_list.append(
            {
                "target_name": get_weight_name_from_index(
                    blendshape_node, index, True
                ),
                "target_index": index,
                "target_deltas": target_temp_dict,
                "inbetween_deltas": inbetween_temp_list,
            }
        )
    return target_deltas_list


def get_blendshape_data(
    blendshape_node, target_deltas=True, deltas_as_MObjects=True, mesh_data=True
):
    """
    Get all needed data from given blendshape node.

    Args:
        blendshape_node(str): Blendshape node name.
        target_deltas(bool): Get target deltas or not. Default is True.
        deltas_as_MObjects(bool): Get target deltas as OpenMaya.MObject.
                                  Default is True.
        mesh_data(bool): Get mesh data or not.

    Return:
        Dict:
        {
        "blendshape_node_info": {
                                "name": blendshape_node,
                                "history_location":
                                blendshape_fn.historyLocation(),
                                "origin": blendshape_fn.origin(),
                                },
        "mesh_data": {
                    "mesh_shape": string
                    "num_vertices": integer,
                    "num_polys": integer,
                    "poly_vertex_id_list": List with each vertex ID of
                                           each vertex ordered by all polys,
                    "verts_ws_pos_list": List of all worldspace postions
                                         of each vertex of the mesh.
                    },
        "weights_connections_data": [
                                     ((node_name, node_plug_name), weight_name),
                                     ((node_name, node_plug_name), weight_name)
                                     ]
        "target_deltas": List
        }

    """
    data_dict = dict()
    base_obj = get_base_objects(blendshape_node)[0]
    if mesh_data:
        data_dict["mesh_data"] = mesh_utils.get_mesh_data(base_obj)
    data_dict["blendshape_node_info"] = get_blendshape_node_infos(
        blendshape_node
    )
    data_dict["weights_connections_data"] = get_weight_connections_data(
        blendshape_node
    )
    data_dict["target_deltas"] = None
    if target_deltas:
        data_dict[
            "target_deltas"
        ] = get_targets_and_inbetweens_deltas_from_blendshape(
            blendshape_node, deltas_as_MObjects
        )
    return data_dict


@DECORATORS.x_timer
def save_deltas_as_numpy_arrays(
    blendshape_node, save_directory, file_prefix=None
):
    """
    Save the target and inbetween deltas as numpy array zip file.

    Directory order is:
        - blendshape_name
            - targets_deltas
                - {file_prefix}_deltas_{target_index}.npz
            - inbetween_deltas
                - {file_prefix}_inbetween_deltas_{target_index}.npz

    Args:
        blendshape_node(str): Blendshape node name.
        save_directory(str): The directory to save the files into.
        file_prefix(str): Optional prefix for the files. If None will take the
                          blendshape name. Default is None.

    Return:
        List:
            [
            {
                "inbetween_deltas": [
                    {
                        "5542": "blendShape1_inbetween_deltas_0_5542.npz"
                    }
                ],
                "target_deltas": "blendShape1_deltas_0.npz",
                "target_index": 0,
                "target_name": "pSphere2"
            },
            {
                "inbetween_deltas": [],
                "target_deltas": "blendShape1_deltas_1.npz",
                "target_index": 1,
                "target_name": "pSphere3"
            }
            ]

    """
    if not file_prefix:
        file_prefix = blendshape_node
    blendshape_data_list_temp = get_targets_and_inbetweens_deltas_from_blendshape(
        blendshape_node, False
    )
    deltas_package_dir = os.path.normpath(
        os.path.join(save_directory, "targets_deltas")
    )
    inbetween_deltas_package_dir = os.path.normpath(
        os.path.join(save_directory, "inbetween_deltas")
    )
    # first we care about the target deltas
    if not os.path.exists(deltas_package_dir):
        os.mkdir(deltas_package_dir)
    for delta_dict in blendshape_data_list_temp:
        file_name = "{}_deltas_{}".format(
            file_prefix, delta_dict["target_index"]
        )
        target_points_list = delta_dict.get("target_deltas").get(
            "target_points"
        )
        target_components_list = delta_dict.get("target_deltas").get(
            "target_components"
        )
        target_points_list_npy_array = numpy.array(
            target_points_list, dtype=object
        )
        target_components_list_npy_array = numpy.array(
            target_components_list, dtype=object
        )
        deltas_npy_array_dir = os.path.normpath(
            "{}/{}".format(deltas_package_dir, file_name)
        )
        numpy.savez_compressed(
            deltas_npy_array_dir,
            points=target_points_list_npy_array,
            components=target_components_list_npy_array,
        )
        delta_dict["target_deltas"] = "{}.npz".format(file_name)
    # Second we care about the inbetween deltas.
    if not os.path.exists(inbetween_deltas_package_dir):
        os.mkdir(inbetween_deltas_package_dir)
    for delta_dict_ in blendshape_data_list_temp:
        inbetweens_list = delta_dict_.get("inbetween_deltas")
        if inbetweens_list:
            for inb_dict in inbetweens_list:
                port_index = list(inb_dict.keys())[0]
                file_name_ = "{}_inbetween_deltas_{}_{}".format(
                    file_prefix, delta_dict_["target_index"], port_index
                )
                inb_deltas_dict = inb_dict.get(port_index)
                inbetween_points_list = inb_deltas_dict.get("target_points")
                inbetween_components_list = inb_deltas_dict.get(
                    "target_components"
                )
                inbetween_points_list_npy_array = numpy.array(
                    inbetween_points_list, dtype=object
                )
                inbetween_components_list_npy_array = numpy.array(
                    inbetween_components_list, dtype=object
                )
                inb_deltas_npy_array_dir = os.path.normpath(
                    "{}/{}".format(inbetween_deltas_package_dir, file_name_)
                )
                numpy.savez_compressed(
                    inb_deltas_npy_array_dir,
                    points=inbetween_points_list_npy_array,
                    components=inbetween_components_list_npy_array,
                )
                inb_deltas_dict["target_points"] = "{}.npz".format(file_name_)
                inb_deltas_dict["target_components"] = "{}.npz".format(
                    file_name_
                )
    return blendshape_data_list_temp


@DECORATORS.x_timer
def save_deltas_as_shp_file(blendshape_node, save_directory, file_prefix=None):
    """
    Save deltas as maya ./shp file. Thats very fast but has not a good
    inbetween support.

    Args:
        blendshape_node(str): Blendshape node name.
        save_directory(str): The directory to save the files into.
        file_prefix(str): Optional prefix for the name. If None will take the
                          blendshape name. Default is None.

    Return:
        String: The file directory.

    """
    if not file_prefix:
        file_prefix = blendshape_node
    shp_file_path = os.path.normpath(
        "{}/{}.shp".format(save_directory, file_prefix)
    )
    cmds.blendShape(blendshape_node, ep=shp_file_path, edit=True)
    return shp_file_path


def save_blendshape_setup(
    blendshape_node,
    save_directory,
    file_prefix=None,
    prune=True,
    as_shp_file=False,
):
    """
    Save the blendshape data into directory for further usage.
    You can save the data as numpy array or as ./shp file. Default is numpy.

    Args:
        blendshape_node(str): Blendshape node name.
        save_directory(str): The directory to save the files into.
        file_prefix(str): Optional prefix for the name. If None will take the
                          blendshape name. Default is None.
        prune(bool): Removes any points not being deformed by the deformer
                     in its current configuration from the deformer set.
                     Default is True.
        as_shp_file(bool): Will save the target deltas as shp file.

    """
    if not file_prefix:
        file_prefix = blendshape_node
    if not os.path.exists(save_directory):
        _LOGGER.warning(
            "{} not exist. Can not save data json file.".format(save_directory)
        )
        return False
    package_dir = os.path.normpath(os.path.join(save_directory, file_prefix))
    if not os.path.exists(package_dir):
        os.mkdir(package_dir)
    cmds.blendShape(blendshape_node, edit=True, pr=prune)
    bshp_data = get_blendshape_data(blendshape_node, False)
    poly_vertex_id_npy_name = "{}_poly_vertex_id".format(file_prefix)
    verts_pos_npy_name = "{}_verts_ws_positions".format(file_prefix)
    base_obj = get_base_objects(blendshape_node)[0]
    mesh_data_dict = bshp_data.get("mesh_data")
    poly_vertex_id_array = numpy.array(
        mesh_data_dict.get("poly_vertex_id_list"), dtype=object
    )
    mesh_data_dict["poly_vertex_id_list"] = "{}.npy".format(
        poly_vertex_id_npy_name
    )
    vertex_ws_pos_array = numpy.array(
        mesh_data_dict.get("verts_ws_pos_list"), dtype=object
    )
    mesh_data_dict["verts_ws_pos_list"] = "{}.npy".format(verts_pos_npy_name)
    poly_vertex_id_npy_dir = os.path.normpath(
        "{}/{}".format(package_dir, poly_vertex_id_npy_name)
    )
    verts_pos_npy_dir = os.path.normpath(
        "{}/{}".format(package_dir, verts_pos_npy_name)
    )
    base_obj_export_name = "{}_base_geo".format(file_prefix)
    bshp_data["base_obj_export"] = "{}.obj".format(base_obj_export_name)
    base_obj_export_dir = os.path.normpath(
        "{}/{}".format(package_dir, base_obj_export_name)
    )
    base_obj_duplicate_m_obj = base_obj.duplicate()
    mfn_transform = OpenMaya.MFnTransform(base_obj_duplicate_m_obj)
    mfn_transform.setName(base_obj_export_name)
    cmds.select(base_obj_export_name)
    pymel.core.exportSelected(
        base_obj_export_dir,
        constructionHistory=False,
        force=True,
        channels=False,
        constraints=False,
        expressions=False,
        shader=False,
        preserveReferences=False,
        type="mayaBinary",
    )
    cmds.delete(base_obj_export_name)
    numpy.save(poly_vertex_id_npy_dir, poly_vertex_id_array)
    numpy.save(verts_pos_npy_dir, vertex_ws_pos_array)
    if not as_shp_file:
        bshp_data["target_deltas"] = save_deltas_as_numpy_arrays(
            blendshape_node, package_dir, file_prefix
        )
    else:
        bshp_data["target_deltas"] = os.path.basename(
            save_deltas_as_shp_file(blendshape_node, package_dir, file_prefix)
        )
    json_file_dir = os.path.normpath(
        "{}/{}.json".format(package_dir, file_prefix)
    )
    with open(json_file_dir, "w") as json_file:
        json.dump(bshp_data, json_file, sort_keys=True, indent=4)
    _LOGGER.info("Blendshape data saved to: {}".format(package_dir))


def build_blendshape_setup(
    target, blendshape_data, blendshape_name=False, OM_deltas=True
):
    """
    Build the blendshape setup for given target mesh.

    Args:
        target(str, pymel.core.PyNode()): The transform node of the geo for
                                          the blendshape node.
        blendshape_data(dict): The blendshape data dict for the build.
        blendshape_name(str): The blendshape node name. If False will take
                              name from blendshape_data. Default is False.
        OM_deltas(bool): Set the target deltas with OpenMaya.MObject.

    """
    if not blendshape_name:
        blendshape_name = "{}_new".format(
            blendshape_data.get("blendshape_node_info").get("name")
        )
    target_names_list = [
        target_dict.get("target_name")
        for target_dict in blendshape_data.get("target_deltas")
    ]
    inbetween_list = [
        target_dict.get("inbetween_deltas")
        for target_dict in blendshape_data.get("target_deltas")
    ]
    create_blendshape_node(
        target,
        blendshape_name,
        blendshape_data.get("blendshape_node_info").get("origin"),
        blendshape_data.get("blendshape_node_info").get("history_location"),
        target_names_list,
        inbetween_list,
        blendshape_data.get("blendshape_node_info").get("topologyCheck"),
    )
    for index, target_dict in enumerate(blendshape_data.get("target_deltas")):
        # First we set the target deltas.
        if OM_deltas:
            OM_set_blendshape_deltas_by_index(
                blendshape_name,
                index,
                (
                    target_dict.get("target_deltas").get("target_points"),
                    target_dict.get("target_deltas").get("target_components"),
                ),
            )
        else:
            set_blendshape_deltas_by_index(
                blendshape_name,
                index,
                (
                    target_dict.get("target_deltas").get("target_points"),
                    target_dict.get("target_deltas").get("target_components"),
                ),
            )
        # Second the inbetween deltas
        inbetween_deltas = target_dict.get("inbetween_deltas")
        for inbetween_dict in inbetween_deltas:
            items = list(inbetween_dict.items())
            for item in items:
                if OM_deltas:
                    OM_set_blendshape_deltas_by_index(
                        blendshape_name,
                        index,
                        (
                            item[1].get("target_points"),
                            item[1].get("target_components"),
                        ),
                        item[0],
                    )
                else:
                    set_blendshape_deltas_by_index(
                        blendshape_name,
                        index,
                        (
                            item[1].get("target_points"),
                            item[1].get("target_components"),
                        ),
                        item[0],
                    )


def _validate_meshes(source_mesh=None, target_mesh=None, json_file_dir=False):
    """
    Compare two meshes and validate it. You can do it with given source and
    target mesh. Or from a json_file.

    Args:
        source_mesh(str): The source mesh shape node.
        target_mesh(str): The target mesh shape node.
        json_file_path(str): Path to the saved json file.

    Return:
        Succeed:
            Dict: {
            "mesh_shape": string
            "num_vertices": integer,
            "num_polys": integer,
            "poly_vertex_id_list": List with each vertex ID of
                                   each vertex ordered by all polys,
            "verts_ws_pos_list": List of all worldspace postions
                                 of each vertex of the mesh.
            }

        Fail:
            False.

    """
    if not json_file_dir:
        try:
            mesh_data_dict = mesh_utils.check_mesh_data(
                source_mesh, target_mesh
            )
        except:
            raise AttributeError(
                "json_file flag is False. You need to give the "
                "source_mesh and target_mesh flag."
            )
    else:
        mesh_data_dict = mesh_utils.check_mesh_data_from_json(json_file_dir)
    if not mesh_data_dict.get("vertex_count"):
        _LOGGER.error(
            "The vertex count is not equal. New blendshape would "
            "not work probably. Exit execution."
        )
        return False
    if not mesh_data_dict.get("poly_count"):
        _LOGGER.error(
            "The poly count is not equal. New blendshape would "
            "not work probably. Exit execution."
        )
        return False
    if not mesh_data_dict.get("poly_vertex_id_list"):
        _LOGGER.error(
            "The vertex IDs not equal. New blendshape would "
            "not work probably. Exit execution. To get the vertices with "
            "different IDs. Use this command: "
            "`mesh_utils.check_mesh_data_from_json(json_file_dir, "
            "diff_poly_vertex_id=True, "
            "diff_poly_vertex_id_color_on_mesh=True)` or "
            "`mesh_utils.check_mesh_data(source_mesh, target_mesh, "
            "diff_poly_vertex_id=True, "
            "diff_poly_vertex_id_color_on_mesh=True)`"
        )
        return False
    if not mesh_data_dict.get("verts_ws_pos_list"):
        _LOGGER.error(
            "The world position of some vertices are different. "
            "Blendshape targets would have wrong results. "
            "Exit execution. To get the vertices with "
            "different world position. Use this command: "
            "`mesh_utils.check_mesh_data_from_json(json_file_dir, "
            "diff_vertx_ws_pos=True, diff_vertx_ws_color_on_mesh=True)` or "
            "'mesh_utils.check_mesh_data(source_mesh, target_mesh"
            "diff_vertx_ws_pos=True, diff_vertx_ws_color_on_mesh=True)'"
        )
        return False
    return mesh_data_dict


def transfer_blendshape_setup(source, target, validate_meshes=True):
    """
    Transfer a blendshape setup from source to target.

    Args:
        source(str): The source mesh shape node.
        target(str): The target mesh shape node.
        validate_meshes(bool): Enable/Disable mesh validation before transfer.
                              This makes sure that your transfer result is
                              not problematic. Default is True.

    Return:
        True if succeed. None if fail.

    """
    validation_result = True
    if validate_meshes:
        validation_result = _validate_meshes(source, target)
    if validation_result:
        source_blendshape_nd_name = get_blendshape_nodes(source)[0]
        source_blendshape_data = get_blendshape_data(
            source_blendshape_nd_name, mesh_data=False
        )
        build_blendshape_setup(target, source_blendshape_data)
        _LOGGER.info(
            "Blendshape setup transferred from {} to {}".format(source, target)
        )
        return True


def import_blendshape_setup(directory, validate_meshes=True):
    """
    Import blendshape setup from given directory.

    Args:
        directory(str): Setup directory.
        validate_meshes(bool): Enable/Disable mesh validation before import.
                              This makes sure that your import result is
                              not problematic. Default is True.

    Return:
        True if succeed. None if fail.

    """
    normalized_dir = os.path.normpath(directory)
    json_data_file = glob.glob(os.path.join(normalized_dir, r"*.json"))
    if json_data_file:
        with open(json_data_file[0], "r") as json_file:
            blendshape_data_dict = json.load(json_file)
    else:
        raise ImportError(
            "No blendshape data file exist in {}".format(normalized_dir)
        )
    validation_result = True
    if validate_meshes:
        validation_result = _validate_meshes(json_file_dir=json_data_file[0])
    if validation_result:
        target_deltas_dir = os.path.normpath(
            os.path.join(normalized_dir, "targets_deltas")
        )
        inbetweens_deltas_dir = os.path.normpath(
            os.path.join(normalized_dir, "inbetween_deltas")
        )
        if not os.path.exists(target_deltas_dir):
            raise OSError("Directory not exist: {}".format(target_deltas_dir))
        if isinstance(blendshape_data_dict.get("target_deltas"), list):
            for delta_data_dict in blendshape_data_dict.get("target_deltas"):
                npy_file = os.path.normpath(
                    os.path.join(
                        target_deltas_dir, delta_data_dict.get("target_deltas")
                    )
                )
                np_data = numpy.load(npy_file, allow_pickle=True)
                target_points = np_data["points"].tolist()
                target_components = np_data["components"].tolist()
                np_data.close()
                delta_data_dict["target_deltas"] = {
                    "target_points": target_points,
                    "target_components": target_components,
                }
                if delta_data_dict.get("inbetween_deltas"):
                    for inbetween_data_dict in delta_data_dict.get(
                        "inbetween_deltas"
                    ):
                        items = list(inbetween_data_dict.items())
                        for item in items:
                            inb_npy_file = os.path.normpath(
                                os.path.join(
                                    inbetweens_deltas_dir,
                                    item[1].get("target_points"),
                                )
                            )
                            inb_np_data = numpy.load(
                                inb_npy_file, allow_pickle=True
                            )
                            item[1]["target_points"] = inb_np_data[
                                "points"
                            ].tolist()
                            item[1]["target_components"] = inb_np_data[
                                "components"
                            ].tolist()
                            inb_np_data.close()
            target_shape = pymel.core.PyNode(
                blendshape_data_dict.get("mesh_data").get("mesh_shape")
            )
            build_blendshape_setup(
                target_shape.getTransform().name(),
                blendshape_data_dict,
                blendshape_data_dict.get("blendshape_node_info").get("name"),
                False,
            )
            _LOGGER.info(
                "Blendshape setup build with numpy arrays from {}.".format(
                    normalized_dir
                )
            )
        if isinstance(blendshape_data_dict.get("target_deltas"), str):
            file_extension = os.path.splitext(
                blendshape_data_dict.get("target_deltas")
            )
            if file_extension != ".shp":
                raise TypeError(
                    "Given file type:{}. Is not a '.shp' file. Will "
                    "abort import.".format(file_extension)
                )
            shp_file = os.path.normpath(
                os.path.join(
                    normalized_dir, blendshape_data_dict.get("target_deltas")
                )
            )
            cmds.blendShape(ip=shp_file)
            _LOGGER.info(
                "Blendshape setup build with '.shp' file from {}.".format(
                    normalized_dir
                )
            )


def transfer_blendshape_deltas(source_mesh, target_mesh, result_smoothing=2):
    target_shapes_list = []
    inbetween_shapes_list = []
    source_trs = pymel.core.PyNode(source_mesh).getTransform()
    target_trs = pymel.core.PyNode(target_mesh).getTransform()
    shapes_extract_target = target_trs.duplicate(n="evaluation_mesh")[0]
    source_blendshape_node = get_blendshape_nodes(source_mesh)[0]
    source_blendshape_info_data = get_blendshape_node_infos(
        source_blendshape_node
    )
    source_weight_indeces = get_weight_indexes(source_blendshape_node)
    wrap_deformer = wrap_utils.create_wrap_deformer(
        source_trs, shapes_extract_target
    )
    delta_mush = pymel.core.deltaMush(ignoreSelected=True, si=result_smoothing)
    delta_mush.setGeometry(shapes_extract_target)
    extract_grp = pymel.core.createNode("transform", n="extracted_shapes_grp")
    for index in source_weight_indeces:
        bshp_fn = get_blendshape_fn(source_blendshape_node)
        bshp_fn.setWeight(index, 1.0)
        weight_name = get_weight_name_from_index(
            source_blendshape_node, index, True
        )
        extracted_target_shape = shapes_extract_target.duplicate()[0]
        extracted_target_shape.setParent(extract_grp)
        extracted_target_shape.rename(weight_name)
        extracted_target_shape_nd = extracted_target_shape.getShape().rename(
            weight_name)
        target_shapes_list.append(extracted_target_shape_nd.__apimobject__())
        bshp_fn.setWeight(index, 0.0)
        inbetween_plugs_list = get_inbetween_plugs(
            source_blendshape_node, index
        )
        if inbetween_plugs_list:
            for inb_dict in inbetween_plugs_list:
                port_index = list(inb_dict.keys())[0]
                inb_name = inb_dict.get(port_index)
                weight = get_weight_from_inbetween_plug_index(port_index)
                bshp_fn.setWeight(index, weight)
                extract_name = "{}_{}_{}".format(weight_name, index, port_index)
                extract_dupl = shapes_extract_target.duplicate()[0]
                extract_dupl.setParent(extract_grp)
                extract_dupl.rename(extract_name)
                inbetween_shapes_list.append(
                    [extract_dupl, index, weight_name, weight, inb_name]
                )
                bshp_fn.setWeight(index, 0.0)
    pymel.core.delete([wrap_deformer, delta_mush, shapes_extract_target])
    create_blendshape_node(target_trs, source_blendshape_info_data.get(
        "name"), source_blendshape_info_data.get("origin"),
                           source_blendshape_info_data.get(
                               "history_location"), target_shapes_list, None,
                           source_blendshape_info_data.get("topologCheck"))

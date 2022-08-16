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
# Date:       2022 / 08 / 15

"""
Util module for blendShape data management
"""

# Import python standart import
import logging
import os
import json
import numpy

# Import Maya specific modules
import pymel.core
import maya.cmds as cmds
from maya import OpenMaya
from maya import OpenMayaAnim

# Import local modules
import decorators
import openmaya_utils
import mesh_utils

##########################################################
# GLOBALS
##########################################################

_LOGGER = logging.getLogger(__name__ + ".py")
_LOGGER.setLevel(logging.INFO)
DECORATORS = decorators.Decorators()
DECORATORS.debug = True
DECORATORS.logger = _LOGGER


BLENDSHAPE_INFO_DICT = {
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
        }
    """
    blendshape_fn = get_blendshape_fn(blendshape_node)
    return {
        "name": blendshape_node,
        "history_location": blendshape_fn.historyLocation(),
        "origin": blendshape_fn.origin(),
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
        typ="blendShape", allFuture=False, future=False, levels=levels
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
        Tuple: OpenMaya.MFnMesh objects
.
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
    target_name="new_target",
    weight=1.0,
    is_inbetween=False,
):
    """
    Add a new empty target to blendshape node.

    Args:
        blendshape_node(str): Blendshape node name.
        index(int): The target index.
        target_name(str): The target name.
        weight(float): The maximum weight the target will have an effect.
        is_inbetween(bool): Define if new target is an inbetween. If it is
        the index number will define to which target the inbetween belongs to.

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
        else:
            raise IndexError("Target index not exist. Unable to add inbetween.")
    if weight != 1.0 or weight != 0.0:
        raise AttributeError(
            "Weights between 0.0 and 1.0 can just be used as inbetween target."
        )
    blendshape_fn.addTarget(
        base_m_object, input_target_array_plug_count, weight
    )
    rename_weight_name_from_index(
        blendshape_node, input_target_array_plug_count, target_name
    )


@DECORATORS.x_timer
def create_blendshape_node(
    geo_transform,
    name=None,
    origin_enum=0,
    history_location_enum=1,
    targets_name_list=None,
    inbetweens_list=None,
    topologyCheck=False,
):
    """
    Create a new blendshape node.

    Args:
        geo_transform(str, pymel.core.PyNode()): The tansform node of the
                                                 geo for the blendshape node
        name(str): Name of the blendshape node. If None will take maya
                   default naming. Default is None.
        origin_enum(int): Enum index in BLENDSHAPE_INFO_DICT["origin"] for
                          the spaces of the deformation origin. Default is
                          kLocalOrigin.
        history_location_enum(int): Enum index in
                                    BLENDSHAPE_INFO_DICT["historyLocation"]
                                    for the place in the deformation order of
                                    the mesh.
                                    Default is kNormal("automatic").
        targets_name_list(list): List with names(str) for the targets of the
                                 node. The order of the list is the index order
                                 of the targets.
                                 Will just add targets if the list is not None.
                                 By default is None.
        inbetweens_list(List): The List to add inbetweens.It has to be filled
                               with tuples of this template:
                               (name(str), weight(float))
                               The order of the tuples in the list is the index
                               order of the inbetweens belonging.
        topologyCheck(bool): Enable/Disable the topology check of the
                             blendshape node.


    """
    if not topologyCheck:
        if isinstance(geo_transform, str):
            geo_transform = pymel.core.PyNode(geo_transform)
        mesh_shape_nd_name = [geo_transform.getShape().name(long=None)]
        mesh_shape_m_obj_array = openmaya_utils.get_m_obj_array(
            mesh_shape_nd_name
        )
        bshp_fn = OpenMayaAnim.MFnBlendShapeDeformer()
        bshp_fn.create(
            mesh_shape_m_obj_array,
            BLENDSHAPE_INFO_DICT.get("origin")[origin_enum][0],
            BLENDSHAPE_INFO_DICT.get("historyLocation")[history_location_enum][
                0
            ],
        )
    else:
        pymel.core.select(geo_transform)
        bshp_data_dict = {"topologyCheck": True}
        bshp_data_dict.update(
            BLENDSHAPE_INFO_DICT.get("origin")[origin_enum][1]
        )
        bshp_data_dict.update(
            BLENDSHAPE_INFO_DICT.get("historyLocation")[history_location_enum][
                1
            ]
        )
        bshp_nd_name = pymel.core.blendShape(**bshp_data_dict)
        bshp_fn = get_blendshape_fn(bshp_nd_name.name())
    if name:
        bshp_fn.setName(name)
        # openmaya_utils.rename_node(bshp_fn.object(), name)
    if targets_name_list:
        for index, target_name in enumerate(targets_name_list):
            add_target(bshp_fn.name(), index, target_name)
    if inbetweens_list:
        for index_, inbetween_tuple in enumerate(inbetweens_list):
            add_target(
                bshp_fn.name(),
                index_,
                inbetween_tuple[0],
                inbetween_tuple[1],
                True,
            )


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
    bshp_fn = get_blendshape_fn(blendshape_node)
    m_plug = bshp_fn.findPlug("inputTarget")
    return m_plug.elementByPhysicalIndex(0).child(0)


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


def get_targets_and_inbetweens_deltas_from_blendshape(blendshape_node):
    """
    Get all deltas of the all inbetweens and targets from given blendshape node.

    Args:
        blendshape_node(str): Blendshape node name.

    Return:
          List: Filled with a multidimensional dict for each target.
          [{"target_name": string,
            "target_index": Integer,
            "target_deltas": {"target_points": points position array,
                              "target_components": affected component array}
            "inbetween_deltas": [{bshp_port:
                                 {"target_points": points position array,
                                 "target_components": affected component
                                 array}}]]

    """
    target_deltas_list = list()
    index_array = get_weight_indexes(blendshape_node)
    for index in index_array:
        target_temp_dict = dict()
        inbetween_temp_list = list()
        target_temp_dict["target_points"], target_temp_dict[
            "target_components"
        ] = get_blendshape_deltas_from_index(blendshape_node, index)
        inbetween_plugs = get_inbetween_plugs(blendshape_node, index)
        if inbetween_plugs:
            for inbetween_dict in inbetween_plugs:
                port_index = list(inbetween_dict.keys())[0]
                inbetween_temp_dict = dict()
                inbetween_temp_dict["target_points"], inbetween_temp_dict[
                    "target_components"
                ] = get_blendshape_deltas_from_index(
                    blendshape_node, index, port_index
                )
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
        blendshape_node
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
                inb_deltas_dict = list(inb_dict.values())[0]
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
                inb_dict[port_index] = "{}.npz".format(file_name_)
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


def save_blendshape_data(
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
    data = dict()
    poly_vertex_id_npy_name = "{}_poly_vertex_id".format(file_prefix)
    verts_pos_npy_name = "{}_verts_ws_positions".format(file_prefix)
    base_obj = get_base_objects(blendshape_node)[0]
    mesh_data_dict = mesh_utils.get_mesh_data(base_obj)
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
    data["blendshape_node_info"] = get_blendshape_node_infos(blendshape_node)
    data["mesh_data"] = mesh_data_dict
    data["weights_connections_data"] = get_weight_connections_data(
        blendshape_node
    )
    poly_vertex_id_npy_dir = os.path.normpath(
        "{}/{}".format(package_dir, poly_vertex_id_npy_name)
    )
    verts_pos_npy_dir = os.path.normpath(
        "{}/{}".format(package_dir, verts_pos_npy_name)
    )
    base_obj_export_name = "{}_base_obj".format(file_prefix)
    data["base_obj_export"] = "{}.obj".format(base_obj_export_name)
    base_obj_mesh_export_dir = os.path.normpath("{}/{}".format(package_dir,
                                                               base_obj_export_name))
    numpy.save(poly_vertex_id_npy_dir, poly_vertex_id_array)
    numpy.save(verts_pos_npy_dir, vertex_ws_pos_array)
    if not as_shp_file:
        data["target_deltas"] = save_deltas_as_numpy_arrays(
            blendshape_node, package_dir, file_prefix
        )
    else:
        data["target_deltas"] = os.path.basename(
            save_deltas_as_shp_file(blendshape_node, package_dir, file_prefix)
        )
    json_file_dir = os.path.normpath(
        "{}/{}.json".format(package_dir, file_prefix)
    )
    with open(json_file_dir, "w") as json_file:
        json.dump(data, json_file, sort_keys=True, indent=4)
    _LOGGER.info("Blendshape data saved to: {}".format(package_dir))

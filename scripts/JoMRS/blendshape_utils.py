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

##########################################################
# GLOBALS
##########################################################

_LOGGER = logging.getLogger(__name__ + ".py")
_LOGGER.setLevel(logging.INFO)
_DECORATORS = decorators.Decorators()
_DECORATORS.debug = False
_DECORATORS.logger = _LOGGER


BLENDSHAPE_INFO_DICT = {
    "origin": [
        OpenMayaAnim.MFnBlendShapeDeformer.kLocalOrigin,
        OpenMayaAnim.MFnBlendShapeDeformer.kWorldOrigin,
    ],
    "historyLocation": [
        OpenMayaAnim.MFnBlendShapeDeformer.kFrontOfChain,
        OpenMayaAnim.MFnBlendShapeDeformer.kNormal,
        OpenMayaAnim.MFnBlendShapeDeformer.kPost,
        OpenMayaAnim.MFnBlendShapeDeformer.kOther,
    ],
}

##########################################################
# FUNCTIONS
##########################################################


@_DECORATORS.x_timer
def get_mesh_data(mesh_shape):
    """
    Get data from given mesh. Like vertices number and vertex IDs and etc.

    Args:
        mesh_shape(str, OpenMaya.MFnMesh): The mesh shape to get the data from.

    Return:
        Dict: {
        "mesh_shape": string
        "num_vertices": integer,
        "num_polys": integer,
        "poly_vertex_id_list": List with each vertex ID of
                               each vertex ordered by all polys,
        "verts_ws_pos_list": List of all worldspace postions
                             of each vertex of the mesh.
        }

    """
    if isinstance(mesh_shape, str):
        mesh_shape = OpenMaya.MFnMesh(openmaya_utils.get_m_object(mesh_shape))
    num_vertices = mesh_shape.numVertices()
    num_polys = mesh_shape.numPolygons()
    poly_vertex_id_list = []
    for x in range(num_polys):
        m_int_array = OpenMaya.MIntArray()
        mesh_shape.getPolygonVertices(x, m_int_array)
        poly_vertex_id_list.append(list(m_int_array))
    vertex_m_point_array = OpenMaya.MPointArray()
    m_dag_path = openmaya_utils.get_dag_path(
        mesh_shape.name(), OpenMaya.MFn.kMesh
    )
    mfn_mesh = OpenMaya.MFnMesh(m_dag_path)
    mfn_mesh.getPoints(vertex_m_point_array, OpenMaya.MSpace.kWorld)
    verts_ws_pos_list = [
        [
            vertex_m_point_array[x][0],
            vertex_m_point_array[x][1],
            vertex_m_point_array[x][2],
        ]
        for x in range(vertex_m_point_array.length())
    ]
    return {
        "mesh_shape": mesh_shape.name(),
        "num_vertices": num_vertices,
        "num_polys": num_polys,
        "poly_vertex_id_list": poly_vertex_id_list,
        "verts_ws_pos_list": verts_ws_pos_list,
    }


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
        as_pynode(bool): Give Pynodes back.
        as_fn(bool): Give OpenMaya.MFnBlendshape back.
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
        index:
        partial_name:
        as_m_object_attr:
    :return: 
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
    blendshape_fn = get_blendshape_fn(blendshape_node)
    base_obj = get_base_objects(blendshape_node)[0]
    base_m_object = openmaya_utils.get_m_object(str(base_obj.name()))
    input_target_array_plug_count = get_input_target_array_plug_count(
        blendshape_node
    )
    if is_inbetween:
        if target_index_exists(blendshape_node, index):
            if weight == 0.0 or weight == 1.0:
                raise AttributeError(
                    "Weight param can not be 0 or 1 if you add a inbetween."
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


def create_blendshape_node(
    geo_transform, name=None, origin_enum=0, history_location_enum=1
):
    if isinstance(geo_transform, str):
        geo_transform = pymel.core.PyNode(geo_transform)
    mesh_shape_nd_name = [geo_transform.getShape().name(long=None)]
    mesh_shape_m_obj_array = openmaya_utils.get_m_obj_array(mesh_shape_nd_name)
    bshp_fn = OpenMayaAnim.MFnBlendShapeDeformer()
    bshp_fn.create(
        mesh_shape_m_obj_array,
        BLENDSHAPE_INFO_DICT.get("origin")[origin_enum],
        BLENDSHAPE_INFO_DICT.get("historyLocation")[history_location_enum],
    )
    if name:
        openmaya_utils.rename_node(bshp_fn.object(), name)


def _OM_get_blendshape_deltas_from_index(
    blendshape_node, index, bshp_port=6000
):
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


@_DECORATORS.x_timer
def get_blendshape_deltas_from_index(
    blendshape_node, index, bshp_port=6000, openMaya=False
):
    if openMaya:
        return _OM_get_blendshape_deltas_from_index(
            blendshape_node, index, bshp_port
        )
    pt = cmds.getAttr(
        "{}.inputTarget[0].inputTargetGroup[{}].inputTargetItem["
        "{}].inputPointsTarget".format(blendshape_node, index, bshp_port)
    )
    ct = cmds.getAttr(
        "{}.inputTarget[0].inputTargetGroup[{}].inputTargetItem["
        "{}].inputComponentsTarget".format(blendshape_node, index, bshp_port)
    )
    return (pt, ct)


@_DECORATORS.x_timer
def _OM_set_blendshape_deltas_by_index(
    blendshape_node, index, deltas_tuple, bshp_port=6000
):
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


@_DECORATORS.x_timer
def set_blendshape_deltas_by_index(
    blendshape_node, index, deltas_tuple, bshp_port=6000
):
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
    return (
        pymel.core.PyNode(blendshape_node)
        .inputTarget[0]
        .inputTargetGroup[index]
        .inputTargetItem[bshp_port]
        .isConnected()
    )


def get_inbetween_name_from_plug_index(blendshape_node, plug_index):
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
            if plug_index == port_index:
                p_value = (
                    info_plug.elementByPhysicalIndex(x).child(1).asString()
                )
                return p_value


def get_inbetween_plugs(blendshape_node, index):
    result_list = list()
    input_target_group_plug = get_input_target_group_plug(blendshape_node)
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
                inbetween_name = get_inbetween_name_from_plug_index(
                    blendshape_node, port_index
                )
                result_list.append({port_index: inbetween_name})
    return result_list


def get_input_target_group_plug(blendshape_node):
    bshp_fn = get_blendshape_fn(blendshape_node)
    m_plug = bshp_fn.findPlug("inputTarget")
    return m_plug.elementByPhysicalIndex(0).child(0)


def get_input_target_array_plug_count(blendshape_node):
    input_target_group_plug = get_input_target_group_plug(blendshape_node)
    m_int_array = OpenMaya.MIntArray()
    return input_target_group_plug.getExistingArrayAttributeIndices(m_int_array)


def collect_blendshape_data(blendshape_node):
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


@_DECORATORS.x_timer
def save_deltas_as_numpy_arrays(blendshape_node, name, save_directory):
    blendshape_data_list_temp = collect_blendshape_data(blendshape_node)
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
        file_name = "{}_deltas_{}".format(name, delta_dict["target_index"])
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
                    name, delta_dict_["target_index"], port_index
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


@_DECORATORS.x_timer
def save_deltas_as_shp_file(blendshape_node, name, save_directory):
    shp_file_path = os.path.normpath("{}/{}.shp".format(save_directory, name))
    cmds.blendShape(blendshape_node, ep=shp_file_path, edit=True)
    return shp_file_path


def save_blendshape_data(
    blendshape_node, save_directory, name=None, prune=True, as_shp_file=False
):
    if not name:
        name = blendshape_node
    if not os.path.exists(save_directory):
        _LOGGER.warning(
            "{} not exist. Can not save data json file.".format(save_directory)
        )
        return False
    package_dir = os.path.normpath(os.path.join(save_directory, name))
    if not os.path.exists(package_dir):
        os.mkdir(package_dir)
    cmds.blendShape(blendshape_node, edit=True, pr=prune)
    data = dict()
    poly_vertex_id_npy_name = "{}_poly_vertex_id".format(name)
    verts_pos_npy_name = "{}_verts_ws_positions".format(name)
    base_obj = get_base_objects(blendshape_node)[0]
    mesh_data_dict = get_mesh_data(base_obj)
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
    numpy.save(poly_vertex_id_npy_dir, poly_vertex_id_array)
    numpy.save(verts_pos_npy_dir, vertex_ws_pos_array)
    if not as_shp_file:
        data["target_deltas"] = save_deltas_as_numpy_arrays(
            blendshape_node, name, package_dir
        )
    else:
        data["target_deltas"] = os.path.basename(
            save_deltas_as_shp_file(blendshape_node, name, package_dir)
        )
    json_file_dir = os.path.normpath("{}/{}.json".format(package_dir, name))
    with open(json_file_dir, "w") as json_file:
        json.dump(data, json_file, sort_keys=True, indent=4)
    _LOGGER.info("Blendshape data saved to: {}".format(package_dir))


def compare_mesh_data(mesh_data_dict_0, mesh_data_dict_1):
    vertex_count = True
    poly_count = True
    vertex_ids = True
    vertex_ws_pos = True
    if mesh_data_dict_0.get("num_vertices") != mesh_data_dict_1.get(
        "num_vertices"
    ):
        vertex_count = False
        _LOGGER.error("Vertex count not equal.")
    if mesh_data_dict_0.get("num_polys") != mesh_data_dict_1.get("num_polys"):
        poly_count = False
        _LOGGER.error("Poly count not equal.")
    if mesh_data_dict_0.get("poly_vertex_id_list") != mesh_data_dict_1.get(
        "poly_vertex_id_list"
    ):
        vertex_ids = False
        _LOGGER.error("Vertex IDs not equal.")
    if mesh_data_dict_0.get("verts_ws_pos_list") != mesh_data_dict_1.get(
        "verts_ws_pos_list"
    ):
        vertex_ws_pos = False
        _LOGGER.error(
            "World position of some vertices are not matching with"
            " compared ones."
        )
    return {
        "vertex_count": vertex_count,
        "poly_count": poly_count,
        "poly_vertex_id_list": vertex_ids,
        "verts_ws_pos_list": vertex_ws_pos,
    }


def check_mesh_data_from_json(
    json_file_path,
    diff_poly_vertex_id=False,
    diff_color_on_mesh=False,
    diff_vertx_ws_pos=False,
    diff_vertx_ws_on_mesh=False,
):
    base_name = os.path.basename(json_file_path)
    data_dir = os.path.normpath(json_file_path.split(base_name)[0])
    with open(json_file_path, "r") as json_file:
        data_dict = json.load(json_file)
        mesh_data_dict = data_dict.get("mesh_data")
    poly_vertex_id_list_file = os.path.join(
        data_dir, mesh_data_dict.get("poly_vertex_id_list")
    )
    verts_ws_pos_list_file = os.path.join(
        data_dir, mesh_data_dict.get("verts_ws_pos_list")
    )
    base_obj = mesh_data_dict.get("mesh_shape")
    poly_vertex_id_np_array = numpy.load(
        poly_vertex_id_list_file, allow_pickle=True
    )
    verts_ws_pos_np_array = numpy.load(
        verts_ws_pos_list_file, allow_pickle=True
    )
    mesh_data_dict["poly_vertex_id_list"] = poly_vertex_id_np_array.tolist()
    mesh_data_dict["verts_ws_pos_list"] = verts_ws_pos_np_array.tolist()
    if not pymel.core.objExists(base_obj):
        _LOGGER.error("{} not exist. Abort mesh data check.".format(base_obj))
        return False
    mfn_mesh_obj = OpenMaya.MFnMesh(openmaya_utils.get_m_object(base_obj))
    current_mesh_data = get_mesh_data(mfn_mesh_obj)
    compare_mesh_data_dict = compare_mesh_data(
        mesh_data_dict, current_mesh_data
    )
    if diff_poly_vertex_id:
        compare_mesh_data_dict = _diff_mesh_data_arrays(
            compare_mesh_data_dict,
            mesh_data_dict,
            current_mesh_data,
            "poly_vertex_id_list",
            "diff_poly_vertex_id",
        )
        if diff_color_on_mesh:
            _diff_color_on_mesh_func(
                compare_mesh_data_dict.get("diff_poly_vertex_id"),
                base_obj,
                (1.0, 0.0, 0.0),
            )
    if diff_vertx_ws_pos:
        compare_mesh_data_dict = _diff_mesh_data_arrays(
            compare_mesh_data_dict,
            mesh_data_dict,
            current_mesh_data,
            "verts_ws_pos_list",
            "diff_verts_ws_pos",
            True,
        )
        if diff_vertx_ws_on_mesh:
            _diff_color_on_mesh_func(
                compare_mesh_data_dict.get("diff_verts_ws_pos"),
                base_obj,
                (0.0, 0.0, 1.0),
            )
    return compare_mesh_data_dict


def check_mesh_data(
    source_mesh,
    target_mesh,
    diff_poly_vertex_id=False,
    diff_color_on_mesh=False,
    diff_vertx_ws_pos=False,
    diff_vertx_ws_on_mesh=False,
):
    source_mfn_mesh = OpenMaya.MFnMesh(openmaya_utils.get_m_object(source_mesh))
    target_mfn_mesh = OpenMaya.MFnMesh(openmaya_utils.get_m_object(target_mesh))
    mesh_data_dict_0 = get_mesh_data(source_mfn_mesh)
    mesh_data_dict_1 = get_mesh_data(target_mfn_mesh)
    compare_mesh_data_dict = compare_mesh_data(
        mesh_data_dict_0, mesh_data_dict_1
    )
    if diff_poly_vertex_id:
        compare_mesh_data_dict = _diff_mesh_data_arrays(
            compare_mesh_data_dict,
            mesh_data_dict_0,
            mesh_data_dict_1,
            "poly_vertex_id_list",
            "diff_poly_vertex_id",
        )
        if diff_color_on_mesh:
            _diff_color_on_mesh_func(
                compare_mesh_data_dict.get("diff_poly_vertex_id"),
                target_mesh,
                (1.0, 0.0, 0.0),
            )
    if diff_vertx_ws_pos:
        compare_mesh_data_dict = _diff_mesh_data_arrays(
            compare_mesh_data_dict,
            mesh_data_dict_0,
            mesh_data_dict_1,
            "verts_ws_pos_list",
            "diff_verts_ws_pos",
            True,
        )
        if diff_vertx_ws_on_mesh:
            _diff_color_on_mesh_func(
                compare_mesh_data_dict.get("diff_verts_ws_pos"),
                target_mesh,
                (0.0, 0.0, 1.0),
            )
    return compare_mesh_data_dict


@_DECORATORS.x_timer
def _diff_two_arrays(source_list, target_list, use_order_index=False):
    diff_list = []
    if len(source_list) != len(target_list):
        raise IndexError("Arrays do not have the same length.")
    for index, (id_source_list, id_target_list) in enumerate(
        zip(source_list, target_list)
    ):
        if id_source_list != id_target_list:
            if use_order_index:
                diff_list.append(index)
            else:
                diff_list.extend(id_target_list)
    return diff_list


def _diff_color_on_mesh_func(diff_list, target_mesh, color_tuple):
    color_list = [
        "{}.vtx[{}]".format(target_mesh, vtx_id) for vtx_id in diff_list
    ]
    cmds.softSelect(sse=0)
    cmds.select(color_list)
    cmds.polyColorPerVertex(rgb=color_tuple)
    pymel.core.mel.eval("PaintVertexColorToolOptions;")
    cmds.select(clear=True)


def _diff_mesh_data_arrays(
    compare_mesh_data_dict,
    mesh_data_dict_0,
    mesh_data_dict_1,
    array_name,
    result_dict_key,
    use_order_index=False,
):
    if not compare_mesh_data_dict.get(array_name):
        diff_list = _diff_two_arrays(
            mesh_data_dict_0.get(array_name),
            mesh_data_dict_1.get(array_name),
            use_order_index,
        )
        compare_mesh_data_dict[result_dict_key] = diff_list
    return compare_mesh_data_dict

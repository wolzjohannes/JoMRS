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
# Date:       2022 / 08 / 16

"""
Utils to handle maya meshes
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

# Import local modules
import decorators
import openmaya_utils

##########################################################
# FUNCTIONS
##########################################################

_LOGGER = logging.getLogger(__name__ + ".py")
_LOGGER.setLevel(logging.INFO)
DECORATORS = decorators.Decorators()
DECORATORS.debug = True
DECORATORS.logger = _LOGGER


@DECORATORS.x_timer
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
        "verts_ws_pos_list": List of all worldspace positions
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


def _compare_mesh_data(mesh_data_dict_0, mesh_data_dict_1):
    """
    Compare mesh data dictionaries.

    Args:
        mesh_data_dict_0: Source mesh data dict.
        mesh_data_dict_1: Target mesh data dict.

    Return:
         Dict:
         {
        "vertex_count": True/False (Vertex count equal or not),
        "poly_count": True/False (Poly count equal or not),
        "poly_vertex_id_list": True/False (Vertex IDs equal or not),
        "verts_ws_pos_list": True/False (Vertex WS positions equal or not),
        }

    """
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
    diff_poly_vertex_id_color_on_mesh=False,
    diff_vertx_ws_pos=False,
    diff_vertx_ws_color_on_mesh=False,
):
    """
    Check a mesh based from a saved json file.

    Args:
        json_file_path(str): Path to the saved json file.
        diff_poly_vertex_id(bool): Gives back the vertex ids which are
                                   different in a new dict_key. If a difference
                                   exist. Else None.
        diff_poly_vertex_id_color_on_mesh(bool): Will give the vertices
                                                 with a different
                                                 vertex id a red color.
                                                 So we see the
                                                 difference in the viewport.
        diff_vertx_ws_pos(bool): Gives back the vertices which are different
                                 in ws position in a new dict_key. If
                                 difference exist. Else None.
        diff_vertx_ws_color_on_mesh(bool): Will give the vertices with a
                                           different ws position a blue
                                           color. So we see the difference
                                           in the viewport.

    Return:
        Dict:
        {
        "vertex_count": vertex_count,
        "poly_count": poly_count,
        "poly_vertex_id_list": vertex_ids,
        "verts_ws_pos_list": vertex_ws_pos,
        "diff_poly_vertex_id": List (just if diff_poly_vertex_id flag is
                                     enabled)
        "diff_verts_ws_pos": List (just if diff_vertx_ws_pos flag is enabled)
        }

    """
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
    poly_vertex_np_data = numpy.load(
        poly_vertex_id_list_file, allow_pickle=True
    )
    verts_ws_pos_np_data = numpy.load(
        verts_ws_pos_list_file, allow_pickle=True
    )
    mesh_data_dict["poly_vertex_id_list"] = poly_vertex_np_data.tolist()
    mesh_data_dict["verts_ws_pos_list"] = verts_ws_pos_np_data.tolist()
    if not pymel.core.objExists(base_obj):
        _LOGGER.error("{} not exist. Abort mesh data check.".format(base_obj))
        return False
    mfn_mesh_obj = OpenMaya.MFnMesh(openmaya_utils.get_m_object(base_obj))
    current_mesh_data = get_mesh_data(mfn_mesh_obj)
    compare_mesh_data_dict = _compare_mesh_data(
        mesh_data_dict, current_mesh_data
    )
    compare_mesh_data_dict = _diff_mesh_data(
        diff_poly_vertex_id,
        diff_poly_vertex_id_color_on_mesh,
        diff_vertx_ws_pos,
        diff_vertx_ws_color_on_mesh,
        compare_mesh_data_dict,
        mesh_data_dict,
        current_mesh_data,
        base_obj,
    )
    return compare_mesh_data_dict


def check_mesh_data(
    source_mesh,
    target_mesh,
    diff_poly_vertex_id=False,
    diff_poly_vertex_id_color_on_mesh=False,
    diff_vertx_ws_pos=False,
    diff_vertx_ws_color_on_mesh=False,
):
    """
    Check two meshes with each other.

    Args:
        source_mesh(str): The source mesh shape node.
        target_mesh(str): The target mesh shape node.
        diff_poly_vertex_id(bool): Gives back the vertex ids which are
                                   different in a new dict_key. If a difference
                                   exist. Else None.
        diff_poly_vertex_id_color_on_mesh(bool): Will give the vertices with a
                                                 different vertex id a red
                                                 color. So we see the
                                                 difference in the viewport.
        diff_vertx_ws_pos(bool): Gives back the vertices which are different
                                 in ws position in a new dict_key. If
                                 difference exist. Else None.
        diff_vertx_ws_color_on_mesh(bool): Will give the vertices with a
                                           different ws position a blue color.
                                           So we see the difference in the
                                           viewport.

    Return:
        Dict:
        {
        "vertex_count": vertex_count,
        "poly_count": poly_count,
        "poly_vertex_id_list": vertex_ids,
        "verts_ws_pos_list": vertex_ws_pos,
        "diff_poly_vertex_id": List (just if diff_poly_vertex_id flag is
                                     enabled)
        "diff_verts_ws_pos": List (just if diff_vertx_ws_pos flag is enabled)
        }

    """
    source_mesh = pymel.core.PyNode(source_mesh)
    target_mesh = pymel.core.PyNode(target_mesh)
    if source_mesh.nodeType() == "transform":
        source_mesh = source_mesh.getShape().name(long=None)
    if target_mesh.nodeType() == "transform":
        target_mesh = target_mesh.getShape()
    source_mfn_mesh = OpenMaya.MFnMesh(openmaya_utils.get_m_object(source_mesh))
    target_mfn_mesh = OpenMaya.MFnMesh(openmaya_utils.get_m_object(target_mesh))
    mesh_data_dict_0 = get_mesh_data(source_mfn_mesh)
    mesh_data_dict_1 = get_mesh_data(target_mfn_mesh)
    compare_mesh_data_dict = _compare_mesh_data(
        mesh_data_dict_0, mesh_data_dict_1
    )
    compare_mesh_data_dict = _diff_mesh_data(
        diff_poly_vertex_id,
        diff_poly_vertex_id_color_on_mesh,
        diff_vertx_ws_pos,
        diff_vertx_ws_color_on_mesh,
        compare_mesh_data_dict,
        mesh_data_dict_0,
        mesh_data_dict_0,
        target_mesh,
    )
    return compare_mesh_data_dict


@DECORATORS.x_timer
def _diff_two_arrays(source_list, target_list, use_order_index=False):
    """
    Find the difference of two arrays.

    Args:
        source_list(List): The source list.
        target_list(List): The target list to compare.
        use_order_index(bool): Will take the index of the list object with
                               the difference

    Return:
        List: Filled with the difference of the two arrays.

    """
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
    """
    Shows the vertex differences in the viewport.

    Args:
        diff_list(List): List with vertex numbers.
        target_mesh(str): The mesh for coloring.
        color_tuple(tuple): The color rgb values.

    """
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
    """
    Diff the mesh data arrays and gives back the updated given compare data
    dict.

    Args:
        compare_mesh_data_dict(dict): The dict with the result of the mesh
                                      comparison. Will be used to store the
                                      result in a given dict key.
        mesh_data_dict_0(dict): The source mesh data dict.
        mesh_data_dict_1(dict): The target mesh data dict.
        array_name(str): The key in the data dict.
                         So we can get the array we want to compare.
        result_dict_key(str): Key name to store the result in the
                              compare_mesh_data_dict.
        use_order_index(bool): Will take the index of the list object with
                               the difference.

    Return:
        Dict:
        {
        "vertex_count": vertex_count,
        "poly_count": poly_count,
        "poly_vertex_id_list": vertex_ids,
        "verts_ws_pos_list": vertex_ws_pos,
        "result_dict_key": diff_list
        }

    """
    diff_list = None
    if not compare_mesh_data_dict.get(array_name):
        diff_list = _diff_two_arrays(
            mesh_data_dict_0.get(array_name),
            mesh_data_dict_1.get(array_name),
            use_order_index,
        )
    compare_mesh_data_dict[result_dict_key] = diff_list
    return compare_mesh_data_dict


def _diff_mesh_data(
    diff_poly_vertex_id,
    diff_poly_vertex_id_color_on_mesh,
    diff_vertx_ws_pos,
    diff_vertx_ws_color_on_mesh,
    compare_mesh_data_dict,
    mesh_data_dict_0,
    mesh_data_dict_1,
    target_mesh,
):
    """
    Will differentiate the mesh data.

    Args:
        diff_poly_vertex_id(bool): Gives back the vertex ids which are
                                   different in a new dict_key. If a difference
                                   exist. Else None.
        diff_poly_vertex_id_color_on_mesh(bool): Will give the vertices with a
                                                 different vertex id a red
                                                 color. So we see the
                                                 difference in the viewport.
        diff_vertx_ws_pos(bool): Gives back the vertices which are different
                                 in ws position in a new dict_key. If
                                 difference exist. Else None.
        diff_vertx_ws_color_on_mesh(bool): Will give the vertices with a
                                           different ws position a blue color.
                                           So we see the difference in the
                                           viewport.
        compare_mesh_data_dict(dict): The dict with the result of the mesh
                                      comparison. Will be used to store the
                                      result in a given dict key.
        mesh_data_dict_0(dict): Source mesh data dict.
        mesh_data_dict_1(dict): Target mesh data dict.
        target_mesh(str): The mesh which will get vertex color if
                          diff_poly_vertex_id_color_on_mesh or
                          diff_vertx_ws_color_on_mesh is set..

    Return:
        Dict:
        {
        "vertex_count": vertex_count,
        "poly_count": poly_count,
        "poly_vertex_id_list": vertex_ids,
        "verts_ws_pos_list": vertex_ws_pos,
        "diff_poly_vertex_id": List,
        "diff_verts_ws_pos": List,
        }
    """
    if diff_poly_vertex_id:
        compare_mesh_data_dict = _diff_mesh_data_arrays(
            compare_mesh_data_dict,
            mesh_data_dict_0,
            mesh_data_dict_1,
            "poly_vertex_id_list",
            "diff_poly_vertex_id",
        )
        if diff_poly_vertex_id_color_on_mesh:
            if compare_mesh_data_dict.get("diff_poly_vertex_id"):
                _diff_color_on_mesh_func(
                    compare_mesh_data_dict.get("diff_poly_vertex_id"),
                    target_mesh,
                    (1.0, 0.0, 0.0),
                )
    if diff_vertx_ws_pos:
        if (
            compare_mesh_data_dict.get("vertex_count")
            and compare_mesh_data_dict.get("poly_count")
            and compare_mesh_data_dict.get("poly_vertex_id_list")
        ):
            compare_mesh_data_dict = _diff_mesh_data_arrays(
                compare_mesh_data_dict,
                mesh_data_dict_0,
                mesh_data_dict_1,
                "verts_ws_pos_list",
                "diff_verts_ws_pos",
                True,
            )
            if diff_vertx_ws_color_on_mesh:
                if compare_mesh_data_dict.get("diff_verts_ws_pos"):
                    _diff_color_on_mesh_func(
                        compare_mesh_data_dict.get("diff_verts_ws_pos"),
                        target_mesh,
                        (0.0, 0.0, 1.0),
                    )
    return compare_mesh_data_dict

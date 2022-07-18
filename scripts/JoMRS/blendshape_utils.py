# Import python standart import
from functools import wraps
import logging
import os
import json
import numpy
import itertools

# Import Maya specific modules
import pymel.core
import maya.cmds as cmds
from maya import OpenMaya
from maya import OpenMayaAnim

# define logger variables
_LOGGER = logging.getLogger(__name__ + ".py")
_LOGGER.setLevel(logging.INFO)
DEBUG = False

# define local variables
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


def x_timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        start = pymel.core.timerX()
        result = func(*args, **kwargs)
        total_time = pymel.core.timerX(st=start)
        if DEBUG:
            _LOGGER.setLevel(logging.DEBUG)
        _LOGGER.debug(
            "Func/Method: {}(). Executed in [{}]".format(func_name, total_time)
        )
        return result

    return wrapper


def get_m_object(node):
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


@x_timer
def get_mesh_data(base_obj):
    num_vertices = base_obj.numVertices()
    num_polys = base_obj.numPolygons()
    poly_vertex_id_list = []
    for x in range(num_polys):
        m_int_array = OpenMaya.MIntArray()
        base_obj.getPolygonVertices(x, m_int_array)
        poly_vertex_id_list.append(list(m_int_array))
    return {
        "base_obj_name": base_obj.name(),
        "num_vertices": num_vertices,
        "num_polys": num_polys,
        "poly_vertex_id_list": poly_vertex_id_list,
    }


def get_blendshape_node_infos(blendshape_node):
    blendshape_fn = get_blendshape_fn(blendshape_node)
    return {
        "name": blendshape_node,
        "history_location": blendshape_fn.historyLocation(),
        "origin": blendshape_fn.origin(),
    }


def get_weight_connections_data(blendshape_node):
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


def get_m_obj_array(objects):
    """
    returns the objects as MObjectArray
    :param objects:
    :return: <OpenMaya.MObjectArray>
    """
    m_array = OpenMaya.MObjectArray()
    for idx, obj in enumerate(objects):
        m_array.insert(get_m_object(obj), idx)
    return m_array


def rename_node(object_name, new_name):
    m_dag_mod = OpenMaya.MDagModifier()
    m_dag_mod.renameNode(get_m_object(object_name), new_name)
    m_dag_mod.doIt()
    return new_name


def get_blendshape_nodes(node, as_string=True, as_pynode=False, as_fn=False):
    if isinstance(node, str):
        node = pymel.core.PyNode(node)
    bshp_nodes = node.listHistory(typ="blendShape")
    if as_pynode:
        return bshp_nodes
    if as_fn:
        return [get_blendshape_fn(node.nodeName()) for node in bshp_nodes]
    if as_string:
        return [node.nodeName() for node in bshp_nodes]


def is_blendshape_node(node):
    m_object = get_m_object(node)
    return bool(m_object.hasFn(OpenMaya.MFn.kBlendShape))


def get_blendshape_fn(blendshape_node):
    m_object = get_m_object(blendshape_node)
    if is_blendshape_node(m_object):
        return OpenMayaAnim.MFnBlendShapeDeformer(m_object)


def get_weight_indexes(blendshape_node):
    blendshape_fn = get_blendshape_fn(blendshape_node)
    m_int_array = OpenMaya.MIntArray()
    blendshape_fn.weightIndexList(m_int_array)
    return m_int_array


def get_base_objects(blendshape_node):
    if not isinstance(blendshape_node, pymel.core.PyNode):
        bshp_node = pymel.core.PyNode(blendshape_node)
    base_objects_list = bshp_node.getBaseObjects()
    base_object_tuple = tuple([node.__apimfn__() for node in base_objects_list])
    return base_object_tuple


def get_weight_names(blendshape_node):
    weight_names = []
    blendshape_fn = get_blendshape_fn(blendshape_node)
    weight_plug = blendshape_fn.findPlug("weight")
    for x in range(weight_plug.numElements()):
        plug = weight_plug.elementByPhysicalIndex(x)
        weight_names.append(plug.partialName(False, False, False, True))
    return tuple(weight_names)


def target_index_exists(blendshape_node, index):
    indexes = get_weight_indexes(blendshape_node)
    if index in indexes:
        return True
    return False


def get_weight_name_from_index(
    blendshape_node, index, partial_name=False, as_m_object_attr=False
):
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
    base_m_object = get_m_object(str(base_obj.name()))
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
    mesh_shape_m_obj_array = get_m_obj_array(mesh_shape_nd_name)
    bshp_fn = OpenMayaAnim.MFnBlendShapeDeformer()
    bshp_fn.create(
        mesh_shape_m_obj_array,
        BLENDSHAPE_INFO_DICT.get("origin")[origin_enum],
        BLENDSHAPE_INFO_DICT.get("historyLocation")[history_location_enum],
    )
    if name:
        rename_node(bshp_fn.object(), name)


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


@x_timer
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


@x_timer
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


@x_timer
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


@x_timer
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


@x_timer
def save_deltas_as_shp_file(blendshape_node, name, save_directory):
    shp_file_path = os.path.normpath("{}/{}.shp".format(save_directory, name))
    cmds.blendShape(blendshape_node, ep=shp_file_path, edit=True)
    return shp_file_path


def save_blenshape_data(
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
    base_obj = get_base_objects(blendshape_node)[0]
    mesh_data_dict = get_mesh_data(base_obj)
    poly_vertex_id_array = numpy.array(
        mesh_data_dict.get("poly_vertex_id_list"), dtype=object
    )
    mesh_data_dict["poly_vertex_id_list"] = "{}.npy".format(
        poly_vertex_id_npy_name
    )
    data["blendshape_node_info"] = get_blendshape_node_infos(blendshape_node)
    data["mesh_data"] = mesh_data_dict
    data["weights_connections_data"] = get_weight_connections_data(
        blendshape_node
    )
    poly_vertex_id_npy_dir = os.path.normpath(
        "{}/{}".format(package_dir, poly_vertex_id_npy_name)
    )
    numpy.save(poly_vertex_id_npy_dir, poly_vertex_id_array)
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
    return {
        "vertex_count": vertex_count,
        "poly_count": poly_count,
        "poly_vertex_id_list": vertex_ids,
    }


def check_mesh_data_from_json(
    json_file_path, diff_poly_vertex_id=False, diff_color_on_mesh=False
):
    base_name = os.path.basename(json_file_path)
    data_dir = os.path.normpath(json_file_path.split(base_name)[0])
    with open(json_file_path, "r") as json_file:
        data_dict = json.load(json_file)
        mesh_data_dict = data_dict.get("mesh_data")
    poly_vertex_id_list_file = os.path.join(
        data_dir, mesh_data_dict.get("poly_vertex_id_list")
    )
    base_obj = mesh_data_dict.get("base_obj_name")
    mesh_data_dict["poly_vertex_id_list"] = list(
        numpy.load(poly_vertex_id_list_file, allow_pickle=True)
    )
    if not pymel.core.objExists(base_obj):
        _LOGGER.error("{} not exist. Abort mesh data check.".format(base_obj))
        return False
    mfn_mesh_obj = OpenMaya.MFnMesh(get_m_object(base_obj))
    current_mesh_data = get_mesh_data(mfn_mesh_obj)
    compare_mesh_data_dict = compare_mesh_data(
        mesh_data_dict, current_mesh_data
    )
    if diff_poly_vertex_id:
        compare_mesh_data_dict = diff_poly_vertex_id_func(
            compare_mesh_data_dict, mesh_data_dict, current_mesh_data
        )
        if diff_color_on_mesh:
            print(compare_mesh_data_dict)
            diff_vertex_id_list_color_on_mesh(
                compare_mesh_data_dict.get("diff_poly_vertex_id"), base_obj
            )
    return compare_mesh_data_dict


def check_mesh_data(
    source_mesh,
    target_mesh,
    diff_poly_vertex_id=False,
    diff_color_on_mesh=False,
):
    source_mfn_mesh = OpenMaya.MFnMesh(get_m_object(source_mesh))
    target_mfn_mesh = OpenMaya.MFnMesh(get_m_object(target_mesh))
    mesh_data_dict_0 = get_mesh_data(source_mfn_mesh)
    mesh_data_dict_1 = get_mesh_data(target_mfn_mesh)
    compare_mesh_data_dict = compare_mesh_data(
        mesh_data_dict_0, mesh_data_dict_1
    )
    if diff_poly_vertex_id:
        compare_mesh_data_dict = diff_poly_vertex_id_func(
            compare_mesh_data_dict, mesh_data_dict_0, mesh_data_dict_1
        )
        if diff_color_on_mesh:
            diff_vertex_id_list_color_on_mesh(
                compare_mesh_data_dict.get("diff_poly_vertex_id"), target_mesh
            )
    return compare_mesh_data_dict


@x_timer
def diff_poly_vertex_id_list(source_list, target_list):
    diff_list = []
    for id_source_list, id_target_list in itertools.zip_longest(
        source_list, target_list
    ):
        if (
            id_source_list != id_target_list
            and id_source_list
            and id_target_list
        ):
            diff_list.extend(id_target_list)
    return diff_list


def diff_vertex_id_list_color_on_mesh(diff_list, target_mesh):
    color_list = [
        "{}.vtx[{}]".format(target_mesh, vtx_id) for vtx_id in diff_list
    ]
    cmds.select(color_list)
    cmds.polyColorPerVertex(rgb=(1.0, 0.0, 0.0))
    pymel.core.mel.eval("PaintVertexColorToolOptions;")


def diff_poly_vertex_id_func(
    compare_mesh_data_dict, mesh_data_dict_0, mesh_data_dict_1
):
    if not compare_mesh_data_dict.get("poly_vertex_id_list"):
        diff_list = diff_poly_vertex_id_list(
            mesh_data_dict_0.get("poly_vertex_id_list"),
            mesh_data_dict_1.get("poly_vertex_id_list"),
        )
        compare_mesh_data_dict["diff_poly_vertex_id"] = diff_list
        return compare_mesh_data_dict


DEBUG = 1
result = check_mesh_data_from_json(
    r"/home/johanneswolz/Schreibtisch/maya_testing_files/blendShape1"
    r"/blendShape1.json",
    True,
    True,
)
# result = check_mesh_data("pSphereShape2", "pSphere3Shape", True, True)
print(result)
# save_blenshape_data(
#     "blendShape1", r"/home/johanneswolz/Schreibtisch/maya_testing_files",
# )

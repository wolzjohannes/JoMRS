# Import python standart import
from functools import wraps
import logging

# Import Maya specific modules
import pymel.core
import maya.cmds as cmds
from maya import OpenMaya as OpenMaya
from maya import OpenMayaAnim as OpenMayaAnim

# define local variables
origin = OpenMayaAnim.MFnBlendShapeDeformer.kLocalOrigin
world_origin = OpenMayaAnim.MFnBlendShapeDeformer.kWorldOrigin
front_of_chain = OpenMayaAnim.MFnBlendShapeDeformer.kFrontOfChain
normal_chain = OpenMayaAnim.MFnBlendShapeDeformer.kNormal

_LOGGER = logging.getLogger(__name__ + ".py")


def x_timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        start = pymel.core.timerX()
        result = func(*args, **kwargs)
        total_time = pymel.core.timerX(st=start)
        _LOGGER.info(
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
def get_mesh_data(blendshape_node):
    base_obj = get_base_objects(blendshape_node)[0]
    num_vertices = base_obj.numVertices()
    num_polys = base_obj.numPolygons()
    poly_vertex_id_list = []
    for x in range(num_polys):
        m_int_array = OpenMaya.MIntArray()
        base_obj.getPolygonVertices(x, m_int_array)
        poly_vertex_id_list.append(m_int_array)
    return {
        "base_obj_name": base_obj.name(),
        "num_vertices": num_vertices,
        "num_polys": num_polys,
        "poly_vertex_id_list": poly_vertex_id_list,
    }


def get_weight_connections_data(blendshape_node):
    result = []
    blendshape_fn = get_blendshape_fn(blendshape_node)
    weight_plug = blendshape_fn.findPlug("weight")
    for x in range(weight_plug.numElements()):
        plug = weight_plug.elementByPhysicalIndex(x)
        if plug.isConnected():
            source_nd_name, source_plug_name = plug.source().name().split(".")
            data_tuple = ((source_nd_name, source_plug_name),
                          plug.partialName(False, False, False, True))
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


def create_blendshape_node(geo_transform, name=None):
    if isinstance(geo_transform, str):
        geo_transform = pymel.core.PyNode(geo_transform)
    mesh_shape_nd_name = [geo_transform.getShape().name(long=None)]
    mesh_shape_m_obj_array = get_m_obj_array(mesh_shape_nd_name)
    bshp_fn = OpenMayaAnim.MFnBlendShapeDeformer()
    bshp_fn.create(mesh_shape_m_obj_array, origin, normal_chain)
    if name:
        rename_node(bshp_fn.object(), name)


def get_blendshape_deltas_from_index(blendshape_node, index, bshp_port=6000):
    pt = cmds.getAttr(
        "{}.inputTarget[0].inputTargetGroup[{}].inputTargetItem["
        "{}].inputPointsTarget".format(blendshape_node, index, bshp_port)
    )
    ct = cmds.getAttr(
        "{}.inputTarget[0].inputTargetGroup[{}].inputTargetItem["
        "{}].inputComponentsTarget".format(blendshape_node, index, bshp_port)
    )
    return (pt, ct)


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


def get_inbetween_plug(blendshape_node, index):
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


# print(get_mesh_data("blendShape1"))
# create_blendshape_node("pSphere2")
print(get_weight_connections_data("blendShape1"))

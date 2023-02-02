from api import dbo, logger
from ariadne import ScalarType, ObjectType
from bson import ObjectId
from bson.dbref import DBRef
from src.test import users

from src.nodes.object.object import Manager as OM
from src.nodes.sketch.sketch import Manager as SM
from src.nodes.user.user_manager import Manager as UM

cached_references = {
    'object': OM,
    'sketch': SM,
    'users': UM,
}

ID = ScalarType("ID")
DBREF = ScalarType("DBREF")

@DBREF.value_parser
def DBREF_v_parser(value):
    if value.get('_id') and value.get('type'):
        return DBRef(value['type'], ObjectId(value['_id']))
    raise ValueError("Invalid DBRef. Must have _id and type fields.")

@ID.serializer
def ID_serializar(value):
    if isinstance(value, ObjectId): return str(value)
    return value

@ID.value_parser
def ID_v_parser(value):
    if value:
        return ObjectId(value)
    return value

@ID.literal_parser
def ID_l_parser(ast):
    return ID_v_parser(str(ast.value))

def dereference_field(obj, info):
    if isinstance(obj.get(info.field_name), DBRef):
        ref = obj[info.field_name]
        if ref.collection in cached_references:
            result = cached_references[ref.collection].get_item(_id=ref.id, user=users['dev'])
            logger.debug(f"Reference for {ref.collection}:{ref.id} found in cache")
            if not isinstance(result, dict):
                return result.__dict__
            return result
        logger.debug(f"Reference for {ref.collection}:{ref.id} not found in cache, getting from database")
        return dbo.dbo.dereference(ref, projection={'password':0})

def create_object_type_with_ref_resolver(name, fields):
    object_type = ObjectType(name)
    for field in fields:
        object_type.field(field)(dereference_field)
    return object_type

base_ref_field= ['created_by', 'edited_by']
process_ref_fields = ['object', 'sketch'] + base_ref_field
object_ref_fields = base_ref_field
sketch_ref_field = base_ref_field

process_gql = create_object_type_with_ref_resolver("process", process_ref_fields)
object_gql = create_object_type_with_ref_resolver("object", object_ref_fields)
sketch_gql = create_object_type_with_ref_resolver("sketch", sketch_ref_field)

custom_types = [ID, DBREF, object_gql, process_gql, sketch_gql]

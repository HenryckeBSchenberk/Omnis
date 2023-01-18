import unittest
from bson import ObjectId as new_id
from src.nodes.object.object import Object, Manager
from src.utility.crud.user import User

def OBJECT_Parser(value, reference=False):
    sequence = value['value'].split('.')
    obj = Manager.get_by_id(value['_id'])

    for attr in sequence:
        obj = getattr(obj, attr)

    return [obj] if reference else obj

class BasicOperations(unittest.TestCase):
    def setUp(self):
        self.object = Object({"name": "object_name", "type": "object_test"})
    
    def test_AccessAsAttribute(self):
        self.assertEqual(self.object.name, "object_name")
        self.assertEqual(self.object.type, "object_test")

    def test_AccessAsDict(self):
        self.assertEqual(self.object["name"], "object_name")
        self.assertEqual(self.object["type"], "object_test")
    
    def test_SetAsAttribute(self):
        self.object.name = "new_name"
        self.assertEqual(self.object.name, "new_name")
    
    def test_SetAsDict(self):
        self.object["name"] = "new_name"
        self.assertEqual(self.object["name"], "new_name")

class UseCases(unittest.TestCase):
    def setUp(self):

        self.A_id = new_id()
        self.B_id = new_id()

        self.A = Object({"name": "object_A"}, self.A_id )
        self.B = Object({"name": "object_B", "parent": self.A}, self.B_id)


        self.options = {
            "A":{
                "name": {
                    "type":"object",
                    "_id": self.A_id,
                    "value": "name"
                },
            },
            "B":{
                "name": {
                    "type":"object",
                    "_id": self.B_id,
                    "value": "name"
                },
                "parent_id": {
                    "type":"object",
                    "_id": self.B_id,
                    "value": "parent._id"
                },
            }
        }

    def test_AutoSubscribeOnManager(self):
        self.assertTrue(Manager.get_by_id(self.A_id) is self.A)
        self.assertTrue(Manager.get_by_id(self.B_id) is self.B)

    def test_ParserSimpleAttribute(self):
        self.assertEqual(OBJECT_Parser(self.options['A']['name']), self.A.name)

    def test_ParserComplexAttribute(self):
        self.assertEqual(OBJECT_Parser(self.options['B']['parent_id']), self.A_id)

    def test_IntegrityBetweenInstances(self):
        _id = new_id()
        object1 = Object({"name": "object_name1", "type": "object_test"}, _id)
        self.assertEqual(object1.name, "object_name1")

        object2 = Object({"name": "object_name2", "type": "object_test"}, _id)
        self.assertTrue(object1.name is object2.name)

        new_name = "SampleText"
        object1.name = new_name
        self.assertTrue(object1.name is object2.name is new_name)

class CRUD_Object(unittest.TestCase):
    def setUp(self):
        self.object = Object({"name": "object_name", "type": "object_test"})
        self.object_id = self.object._id
        self.user=User('omnis','process','developer','')
    
    def test_Export(self):
        self.assertEqual(self.object.export(), {'_id': self.object_id, 'name': 'object_name', 'type': 'object_test'})
    
    def test_Load(self):
        self.object.load({"name": "new_name", "type": "new_type"})
        self.assertEqual(self.object.export(), {'_id': self.object_id, 'name': 'new_name', 'type': 'new_type'})
    
    def test_CRUD(self):
        exported = self.object.export()
        create = Manager.create(input=exported, _id=self.object_id, user=self.user)
        get = Manager.get_item(_id=create, user=self.user)
        self.assertEqual(exported, get)
        
        duplicate_id = Manager.duplicate(_id=self.object_id, user=self.user)
        get_duplicate = Manager.get_item(_id=duplicate_id, user=self.user, filter={'name':1})
        self.assertEqual(get_duplicate['name'], "object_name - copy")
        self.assertTrue(get_duplicate['_id'] != self.object_id)

        updated_id = Manager.update(_id=self.object_id, input={"name": "new_name", "type": "new_type"}, user=self.user)
        get_updated = Manager.get_item(_id=updated_id, user=self.user, filter={"name": 1, "type": 1})
        self.assertEqual(get_updated, {"_id": updated_id, "name": "new_name", "type": "new_type"})

        delete_original_id = Manager.delete(_id=self.object_id, user=self.user)
        delete_duplicate_id = Manager.delete(_id=duplicate_id, user=self.user)
        
        deleted_original = Manager.get_item(_id=delete_original_id, user=self.user)
        deleted_duplicate = Manager.get_item(_id=delete_duplicate_id, user=self.user)
        self.assertTrue(deleted_duplicate is deleted_original is None)
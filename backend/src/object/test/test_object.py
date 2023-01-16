from src.object.object import Object, Manager
import unittest

Skip = False
def OBJECT_Parser(value, reference=False):
    sequence = value['value'].split('.')
    obj = Manager.get_by_id(value['_id'])

    for attr in sequence:
        obj = getattr(obj, attr)

    print("Objeto:",obj)

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

        self.A = Object({"name": "object_A"},'A')
        self.B = Object({"name": "object_B", "parent": self.A},'B')

        self.A_id = self.A._id
        self.B_id = self.B._id

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
        self.object1 = Object({"name": "object_name1", "type": "object_test"}, 'A')
        self.assertEqual(self.object1.name, "object_name1")

        self.object2 = Object({"name": "object_name2", "type": "object_test"}, 'A')
        self.assertTrue(self.object1.name is self.object2.name)

        new_name = "SampleText"
        self.object1.name = new_name
        self.assertTrue(self.object1.name is self.object2.name is new_name)

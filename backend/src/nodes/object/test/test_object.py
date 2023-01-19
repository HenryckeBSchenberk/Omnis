import unittest
from bson import ObjectId as new_id
from src.nodes.object.object import Object, Manager
from src.utility.crud.user import User


class BasicOperations(unittest.TestCase):
    def setUp(self):
        self.object = Object(**{"name": "object_name", "type": "object_test"})

    def tearDown(self):
        Manager.remove_by_id(self.object._id)
        self.assertFalse(Manager.store)

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

        self.A = Object(self.A_id, **{"name": "object_A"})
        self.B = Object(self.B_id, **{"name": "object_B", "parent": self.A})

        self.options = {
            "A": {
                "name": {
                    "type": "object",
                    "_id": self.A_id,
                    "value": "name"
                },
            },
            "B": {
                "name": {
                    "type": "object",
                    "_id": self.B_id,
                    "value": "name"
                },
                "parent_id": {
                    "type": "object",
                    "_id": self.B_id,
                    "value": "parent._id"
                },
            }
        }

    def tearDown(self):
        Manager.remove_by_id(self.A_id)
        Manager.remove_by_id(self.B_id)
        self.assertFalse(Manager.store)

    def test_AutoSubscribeOnManager(self):
        self.assertTrue(Manager.get_by_id(self.A_id) is self.A)
        self.assertTrue(Manager.get_by_id(self.B_id) is self.B)

    def test_IntegrityBetweenInstances(self):
        object1 = Object(
            self.A_id, **{"name": "object_name1", "type": "object_test"}
        )
        self.assertEqual(object1.name, "object_name1")

        object2 = Object(
            self.A_id, **{"name": "object_name2", "type": "object_test"}
        )
        self.assertTrue(object1.name is object2.name)

        new_name = "SampleText"
        object1.name = new_name
        self.assertTrue(object1.name is object2.name is new_name)

    def test_ObjectParser(self):
        payload = "${object_A.name}"

        static_value, obj, key = Manager.parser(payload)
        self.assertIs(obj, self.A)
        self.assertEqual(static_value, self.A.name)

        self.A.name = "new_name"
        # Static_value not change;
        self.assertNotEqual(static_value, self.A.name)
        self.assertEqual(obj[key], self.A.name)

    def test_ParserException(self):
        payload = "${object_A.name"
        with self.assertRaises(ValueError):
            Manager.parser(payload)


class CRUD_Object(unittest.TestCase):
    def setUp(self):
        self.object = Object(**{"name": "object_name", "type": "object_test"})
        self.object_id = self.object._id
        self.user = User('omnis', 'process', 'developer', '')

    def tearDown(self):
        Manager.remove_by_id(self.object_id)
        self.assertFalse(Manager.store)

    def test_Export(self):
        self.assertEqual(self.object.export(), {
                         '_id': self.object_id, 'content': {'name': 'object_name', 'type': 'object_test'}})

    def test_Load(self):
        self.object.load(**{"name": "new_name", "type": "new_type"})
        self.assertEqual(self.object.export(), {
                         '_id': self.object_id, 'content': {'name': 'new_name', 'type': 'new_type'}})

    def test_CRUD(self):
        exported = self.object.export()
        create = Manager.create(
            input=exported, _id=self.object_id, user=self.user)
        get = Manager.get_item(_id=create, user=self.user)
        self.assertEqual(exported, get)

        duplicate_id = Manager.duplicate(_id=self.object_id, user=self.user)
        get_duplicate = Manager.get_item(
            _id=duplicate_id, user=self.user)

        duplicated_object = Object(**get_duplicate)

        self.assertEqual(duplicated_object['name'], self.object.name)
        self.assertTrue(duplicated_object['_id'] != self.object_id)

        Manager.remove_by_id(duplicate_id)

        updated_id = Manager.update(
            _id=self.object_id,
            input={
                "content": {
                    "name": "new_name",
                    "type": "new_type"
                }
            },
            user=self.user
        )
        get_updated = Manager.get_item(
            _id=updated_id,
            user=self.user
        )
        self.assertEqual(
            get_updated["content"],
            {"name": "new_name", "type": "new_type"}
        )

        delete_original_id = Manager.delete(_id=self.object_id, user=self.user)
        delete_duplicate_id = Manager.delete(_id=duplicate_id, user=self.user)

        deleted_original = Manager.get_item(
            _id=delete_original_id,
            user=self.user
        )
        deleted_duplicate = Manager.get_item(
            _id=delete_duplicate_id,
            user=self.user
        )

        self.assertTrue(deleted_duplicate is deleted_original is None)

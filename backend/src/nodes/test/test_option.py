import unittest
from src.nodes.option import Option
from src.nodes.object.object import Object, Manager

class TestOption(unittest.TestCase):
    def setUp(self):
        self.object = Object(**{"name": "test_object", "type": "object_test"})
        self.option = Option({"type": "${test_object.type}", "color": "red"})
    
    def tearDown(self):
        Manager.remove_by_id(self.object._id)
    
    def test_AccessAsAttribute(self):
        self.assertEqual(self.option.type, "object_test")
        self.assertEqual(self.option.color, "red")

    def test_ObjectBinder(self):
        self.object.type = "new_type"
        self.assertEqual(self.option.type, "new_type")
    
    def test_OptionBinder(self):
        self.option.type = "blue"
        self.assertEqual(self.object.type, "blue")
    
    def test_ObjectParser(self):
        payload = "${test_object.name}"

        static_value, obj, key = self.option.parser(payload)
        self.assertIs(obj, self.object)
        self.assertEqual(static_value, self.object.name)

        self.object.name = "new_name"
        # Static_value not change;
        self.assertNotEqual(static_value, self.object.name)
        self.assertEqual(obj[key], self.object.name)

    def test_ParserException(self):
        payload = "${test_object.name"
        with self.assertRaises(ValueError):
            self.option.parser(payload)
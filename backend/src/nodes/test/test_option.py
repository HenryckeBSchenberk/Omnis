import unittest
from src.nodes.option import Option
from src.nodes.object.object import Object, Manager
from src.utility.crud.user import User

class TestOption(unittest.TestCase):
    def setUp(self):
        self.user = User('omnis', 'process', 'developer', '')
        self.object = Object(**{"name": "test_option_object", "type": "object_test"})
        self.option = Option({"type": "${test_option_object.type}", "color": "red"})
    
    def tearDown(self):
        Manager.delete(_id=self.object._id, user=self.user)
    
    def test_option_access_atribute(self):
        """[OPTION] Acessando atributo"""
        self.assertEqual(self.option.type, "object_test")
        self.assertEqual(self.option.color, "red")
    
    def test_option_set_attribute(self):
        """[OPTION] Setando atributo"""
        self.option.type = "blue"
        self.assertEqual(self.object.type, "blue")
    
    def test_option_parser_valid_data(self):
        """[OPTION] Passando parâmentro válido para o parser"""
        payload = "${test_option_object.name}"

        static_value, obj, key = self.option.parser(payload)
        self.assertIs(obj, self.object)
        self.assertEqual(static_value, self.object.name)

    def test_option_parser_invalid_data(self):
        """[OPTION] Passando parâmentro inválido para o parser"""
        payload = "${test_option_object.name"
        with self.assertRaises(ValueError):
            self.option.parser(payload)
    
    def test_option_with_object_as_argument(self):
        """[OPTION] Passando instanciade objeto como parâmentro"""
        obj = Object(**{"name": "another_test", "type": "object_test_check"})
        option = Option({"type": "${type}", "color": "red"}, obj)
        self.assertEqual(option.type, "object_test_check")
        self.assertEqual(option.color, "red")
        Manager.delete(_id=obj._id, user=self.user)
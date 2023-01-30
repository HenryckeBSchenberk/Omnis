import unittest
from bson import ObjectId
from src.crud import CRUD
from src.test import users

class TestCRUD(unittest.TestCase):
    @classmethod
    def setUpClass(cls):        
        cls.crud = CRUD('test_crud', 'developer')

    def tearDown(self) -> None:
        self.crud.delete(_id=self._id, user=users['dev'])
        
    def setUp(self):
        self._id = ObjectId()

    def test_create(self):
        self.crud.create(_id=self._id, input={'name': 'test'}, user=users['dev'])
        item = self.crud.get_item(_id=self._id, user=users['dev'], cache=False)
        self.assertEqual(item['_id'], self._id)
        self.assertEqual(item['name'], 'test')

        cached_item = self.crud.get_item(_id=self._id, user=users['dev'])
        self.assertEqual(cached_item, item)
    
    def test_update(self):
        entropy = ObjectId()
        self.crud.create(_id=self._id, input={'name': 'test'}, user=users['dev'])
        self.crud.update(_id=self._id, input={'name': 'updated', 'entropy':entropy}, user=users['dev'])
        item = self.crud.get_item(_id=self._id, user=users['dev'], cache=False)
        self.assertEqual(item['_id'], self._id)
        self.assertEqual(item['name'], 'updated')
        self.assertEqual(item['entropy'], entropy)
        
        cached_item = self.crud.get_item(_id=self._id, user=users['dev'])
        self.assertEqual(cached_item, item)

    def test_delete(self):
        self.crud.create(_id=self._id, input={'name': 'test'}, user=users['dev'])
        self.crud.delete(_id=self._id, user=users['dev'])
        with self.assertRaises(KeyError):
            self.crud.get_item(_id=self._id, user=users['dev'], cache=False)

        with self.assertRaises(KeyError):
            self.crud.get_item(_id=self._id, user=users['dev'])
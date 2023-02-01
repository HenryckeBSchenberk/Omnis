import unittest
from bson import ObjectId
from src.crud import CRUD
from src.test import users

class TestCRUD(unittest.TestCase):
    @classmethod
    def setUpClass(cls):        
        cls.crud = CRUD('test_crud', 'developer')

    @classmethod
    def tearDownClass(cls):
        cls.crud.cache_manager.clear_cache()

    def tearDown(self) -> None:
        self.crud.delete(_id=self._id, user=users['dev'])
        
    def setUp(self):
        self._id = ObjectId()

    def test_crud_create(self):
        """[CRUD] Criando documento"""
        self.crud.create(_id=self._id, input={'name': 'test'}, user=users['dev'])
        item = self.crud.get_item(_id=self._id, user=users['dev'], cache=False)
        self.assertEqual(item['_id'], self._id)
        self.assertEqual(item['name'], 'test')

        cached_item = self.crud.get_item(_id=self._id, user=users['dev'])
        self.assertEqual(cached_item, item)
    
    def test_crud_update(self):
        """[CRUD] Atualizando documento"""
        entropy = ObjectId()
        self.crud.create(_id=self._id, input={'name': 'test'}, user=users['dev'])
        self.crud.update(_id=self._id, input={'name': 'updated', 'entropy':entropy}, user=users['dev'])
        item = self.crud.get_item(_id=self._id, user=users['dev'], cache=False)
        self.assertEqual(item['_id'], self._id)
        self.assertEqual(item['name'], 'updated')
        self.assertEqual(item['entropy'], entropy)
        
        cached_item = self.crud.get_item(_id=self._id, user=users['dev'])
        self.assertEqual(cached_item, item)

    def test_crud_delete(self):
        """[CRUD] Deletando documento"""
        self.crud.create(_id=self._id, input={'name': 'test'}, user=users['dev'])
        self.crud.delete(_id=self._id, user=users['dev'])
        with self.assertRaises(KeyError):
            self.crud.get_item(_id=self._id, user=users['dev'], cache=False)

        with self.assertRaises(KeyError):
            self.crud.get_item(_id=self._id, user=users['dev'])
    
    def test_crud_get_list(self):
        """[CRUD] Listando documentos"""
        _oid = ObjectId()
        self.crud.create(_id=self._id, input={'name': 'test_list'}, user=users['dev'], cache=False)
        self.crud.create(_id=_oid, input={'name': 'test_list'}, user=users['dev'], cache=False)

        items = self.crud.get_list(user=users['dev'], ref=False)
        self.assertEqual(items[0]['_id'], self._id)
        self.assertEqual(items[1]['_id'], _oid)
        self.crud.delete(_id=_oid, user=users['dev'], cache=False)
        
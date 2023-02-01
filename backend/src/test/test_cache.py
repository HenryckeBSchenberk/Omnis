import unittest
from bson.objectid import ObjectId
from src.cache import CacheManager

class TestCacheManager(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.cache_manager = CacheManager("test_cache")
        cls.cache_manager.clear()

    def setUp(self):
        self.cache_manager.clear_cache()

    def tearDown(self):
        self.cache_manager.clear_cache()

    def test_cache_manager_add_document(self):
        """[CACHE_MANAGER] Adicionando documento"""
        document = {"name": "John Doe", "age": 30}
        _id = self.cache_manager.add_document(document)
        self.assertIsInstance(_id, ObjectId)

        document_from_cache = self.cache_manager.get_document(_id)
        self.assertEqual(document, document_from_cache)

    def test_cache_manager_get_document(self):
        """[CACHE_MANAGER] Procurando documento"""
        document = {"name": "Jane Doe", "age": 25}
        _id = ObjectId()
        self.cache_manager.add_document(document, _id)

        document_from_cache = self.cache_manager.get_document(_id)
        self.assertEqual(document, document_from_cache)

    def test_cache_manager_document_with_id(self):
        """[CACHE_MANAGER] Adicionando documento com _id definido"""
        document = {"_id": ObjectId(), "name": "John Doe", "age": 30}
        _id = self.cache_manager.add_document(document)
        self.assertEqual(document["_id"], _id)

        document_from_cache = self.cache_manager.get_document(_id)
        self.assertEqual(document, document_from_cache)
    
    def test_cache_manager_get_all_documents(self):
        """[CACHE_MANAGER] Procurando todos os documentos"""
        documents = [{"name": f"John {i}"} for i in range(3)]
        [self.cache_manager.add_document(doc) for doc in documents]
        all_docs = self.cache_manager.get_all_documents()
        self.assertEqual(len(all_docs), len(documents))

    def test_cache_manager_update_document(self):
        """[CACHE_MANAGER] Atualizando documento"""
        _id = self.cache_manager.add_document({"name": "John"})
        self.cache_manager.update_document({"name": "Jane"}, _id)
        document_from_cache = self.cache_manager.get_document(_id)
        self.assertEqual(document_from_cache["name"], "Jane")

    def test_cache_manager_update_add_field(self):
        """[CACHE_MANAGER] Atualizando documento com novo campo"""
        _id = self.cache_manager.add_document({"name": "John"})
        self.cache_manager.update_document({"age": 30}, _id)
        document_from_cache = self.cache_manager.get_document(_id)
        self.assertEqual(document_from_cache["age"], 30)
        self.assertEqual(document_from_cache["name"], "John")
    
    def test_cache_manager_remove_document(self):
        """[CACHE_MANAGER] Removendo documento"""
        _id = self.cache_manager.add_document({"name": "John"})
        self.cache_manager.remove_document(_id)
        self.assertEqual(self.cache_manager.get_document(_id), None)
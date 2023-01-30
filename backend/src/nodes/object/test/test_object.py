import unittest
from src.nodes.object.object import Object, Manager
from src.utility.crud.user import User, DBRef, ObjectId

def _object_pattern_test(self, example):

    # Check for object pattern
    self.assertIsInstance(self.item, Object)
    self.assertIsInstance(self.item.created_by, DBRef)
    self.assertIsInstance(self.item._id, ObjectId)

    # Check_for_cache and LocalStore on Manager
    self.assertEqual(self.item.export(), Manager.crud.cache_manager.get_document(example["_id"]))
    self.assertEqual(self.item, Manager.store.get(example["_id"], 'Fail to get item from store'))


class ObjectLocal(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.user = User('object_test', 'local', 'developer', '')

    def setUp(self):
        Manager.crud.cache_manager.clear_cache()

    def tearDown(self):
        Manager.delete(_id=self.item._id, user=self.user)
        del self.item
    
    def test_get_local(self):
        EXAMPLE = {"content":{"name": "DB+CACHE+LOCAL", "type": "object_test"}}

        # Create an objecto on main dbo, cache and localy
        Manager.create(input=EXAMPLE, user=self.user)

        # Assert that the object is on cache and localy
        self.assertEqual(Manager.crud.cache_manager.get_document(EXAMPLE["_id"]), EXAMPLE)
        self.assertIsInstance(Manager.store.get(EXAMPLE["_id"], None), Object)

        # Call get_item and let it resolve the object
        self.item = Manager.get_item(_id=EXAMPLE["_id"], user=self.user)

        _object_pattern_test(self, EXAMPLE)

        #Check if the object is the same created on main dbo
        self.assertEqual(self.item.export(), EXAMPLE)
    
    def test_update_local(self):
        EXAMPLE = {"content":{"name": "DB+CACHE+LOCAL", "type": "INITIAL_VALUE"}}
        UPDATED_EXAMPLE = {"content":{"name": "DB+CACHE+LOCAL", "type": "UPDATED_VALUE"}}

        Manager.create(input=EXAMPLE, user=self.user)
        Manager.update(_id=EXAMPLE["_id"], input=UPDATED_EXAMPLE, user=self.user)

        # Assert that the object is on cache and localy
        self.assertTrue(Manager.crud.cache_manager.get_document(EXAMPLE["_id"]))
        self.assertIsInstance(Manager.store.get(EXAMPLE["_id"], None), Object)

        # Call get_item and let it resolve the object
        self.item = Manager.get_item(_id=EXAMPLE["_id"], user=self.user)

        _object_pattern_test(self, EXAMPLE)

        #Check if the object was updated
        self.assertEqual(self.item.type, UPDATED_EXAMPLE['content']['type'])

class ObjetUncached(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.user = User('object_test', 'uncached', 'developer', '')

    def setUp(self):
        Manager.crud.cache_manager.clear_cache()

    def tearDown(self):
        Manager.delete(_id=self.item._id, user=self.user)
        del self.item
    
    def test_get_uncached(self):
        
        EXAMPLE = {"content":{"name": "only_db", "type": "object_test"}}
        # Create an objecto on main dbo, whiout add localy or to cache
        Manager.crud.create(input=EXAMPLE, user=self.user, cache=False) 

        # Assert that the object is not on cache or localy
        self.assertEqual(Manager.crud.cache_manager.get_document(EXAMPLE["_id"]), None)
        self.assertEqual(Manager.store.get(EXAMPLE["_id"], None), None)

        # Call get_item and let it resolve the object
        self.item = Manager.get_item(_id=EXAMPLE["_id"], user=self.user)

        _object_pattern_test(self, EXAMPLE)

        #Check if the object is the same created on main dbo
        self.assertEqual(self.item.export(), EXAMPLE)
    
    def test_update_uncached(self):
        EXAMPLE = {"content":{"name": "only_db", "type": "INITIAL_VALUE"}}
        UPDATED_EXAMPLE = {"content":{"name": "only_db", "type": "UPDATED_VALUE"}}

        Manager.crud.create(input=EXAMPLE, user=self.user, cache=False)
        Manager.crud.update(_id=EXAMPLE["_id"], input=UPDATED_EXAMPLE, user=self.user, cache=False)

        # Assert that the object is not on cache or localy
        self.assertEqual(Manager.crud.cache_manager.get_document(EXAMPLE["_id"]), None)
        self.assertEqual(Manager.store.get(EXAMPLE["_id"], None), None)

        # Call get_item and let it resolve the object
        self.item = Manager.get_item(_id=EXAMPLE["_id"], user=self.user)

        _object_pattern_test(self, EXAMPLE)

        #Check if the object was updated
        self.assertEqual(self.item.type, UPDATED_EXAMPLE['content']['type'])

class ObjectCached(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.user = User('object_test', 'cached', 'developer', '')

    def setUp(self):
        Manager.crud.cache_manager.clear_cache()

    def tearDown(self):
        Manager.delete(_id=self.item._id, user=self.user)
        del self.item
    
    def test_update_cached(self):
        EXAMPLE = {"content":{"name": "DB+CACHE", "type": "INITIAL_VALUE"}}
        UPDATED_EXAMPLE = {"content":{"name": "DB+CACHE", "type": "UPDATED_VALUE"}}

        Manager.crud.create(input=EXAMPLE, user=self.user, cache=True)
        Manager.crud.update(_id=EXAMPLE["_id"], input=UPDATED_EXAMPLE, user=self.user, cache=True)

        # Assert that the object is on cache but not localy
        self.assertTrue(Manager.crud.cache_manager.get_document(EXAMPLE["_id"]))
        self.assertEqual(Manager.store.get(EXAMPLE["_id"], None), None)
        
        # Call get_item and let it resolve the object
        self.item = Manager.get_item(_id=EXAMPLE["_id"], user=self.user)

        _object_pattern_test(self, EXAMPLE)

        #Check if the object was updated
        self.assertEqual(self.item.type, UPDATED_EXAMPLE['content']['type'])
    
    def test_get_cached(self):
        EXAMPLE = {"content":{"name": "DB+CACHE", "type": "object_test"}}
        # Create an objecto on main dbo and cache, whiout add localy
        Manager.crud.create(input=EXAMPLE, user=self.user, cache=True)
        
        # Assert that the object is on cache but not localy
        self.assertEqual(Manager.crud.cache_manager.get_document(EXAMPLE["_id"]), EXAMPLE)
        self.assertEqual(Manager.store.get(EXAMPLE["_id"], None), None)

        # Call get_item and let it resolve the object
        self.item = Manager.get_item(_id=EXAMPLE["_id"], user=self.user)

        _object_pattern_test(self, EXAMPLE)
        
        #Check if the object is the same created on main dbo
        self.assertEqual(self.item.export(), EXAMPLE)
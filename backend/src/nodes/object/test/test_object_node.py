import unittest
# ! Import NodeRegistry register all NodeClass, try whiout this will fail with circular import error.
from src.nodes.node_registry import NodeRegistry
from src.nodes.object.object_node import ObjectNode, ObjectManager
from src.utility.crud.user import User
from bson import ObjectId as new_id
import asyncio


class TestObjectNode(unittest.TestCase):
    def setUp(self):
        _static_id = new_id()
        self.user = User('omnis', 'test_case', 'developer', '')
        self.object_id = ObjectManager.create(
            input={"name": "default_name", "type": "object_test"}, _id=_static_id, user=self.user)
        self.loop = asyncio.new_event_loop()

    def test_ExecutionDataIntegrity(self):
        node = ObjectNode("UnitTest_ObjectNode", self.object_id, {"_id": self.object_id, "content": {
                          "name": "object_name", "type": "object_test"}}, [], [])

        old_pointer = node.object.export()
        old_contet = old_pointer['content'].copy()

        executer = node.execute({"name": "updated_node"})
        self.loop.run_until_complete(executer)
        new_pointer = node.object.export()
        new_content = new_pointer['content']

        self.assertIsNot(old_pointer, new_pointer)    # different object
        # same content, because it's the content is the same, since is a internal dict updated.
        self.assertEqual(old_pointer, new_pointer)

        self.assertIsNot(old_contet, new_content)    # different object
        # different content, because old_content use ".copy()" to create a new dict.
        self.assertNotEqual(old_contet, new_content)

        # same content, because is a internal dict updated.
        self.assertEqual(old_pointer['content'], new_pointer['content'])

    def test_ExecutionDataSyncDBO(self):
        node = ObjectNode("UnitTest_ObjectNode", self.object_id, {"_id": self.object_id, "content": {
                          "name": "object_name", "type": "object_test"}, "sync": True}, [], [])
        excuter = node.execute({"name": "updated_node_sync"})
        self.loop.run_until_complete(excuter)

        get_node = ObjectManager.get_item(_id=self.object_id, user=self.user)
        self.assertEqual(get_node['content'], node.object.export()['content'])

    def tearDown(self):
        self.loop.close()
        ObjectManager.delete(_id=self.object_id, user=self.user)

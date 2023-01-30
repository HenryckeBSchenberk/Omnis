import redis
import pickle
from bson.objectid import ObjectId

class RedisConnection:
    def __init__(self, host="cache", port=6379):
        """
        This class is responsible to create a connection with the Redis database.
        
        :param host: The host of the Redis server (default: "cache")
        :type host: str
        :param port: The port of the Redis server (default: 6379)
        :type port: int
        :param db: The database number (default: 0)
        :type db: int
        """
        self.cache = redis.Redis(host=host, port=port)

    def clear(self):
        """
        This method is responsible for clearing the cache.
        """
        self.cache.flushdb()

class CacheManager(RedisConnection):
    def __init__(self, collection_name):
        """
        This class is responsible for managing the cache.
        
        :param collection_name: The name of the collection to be cached.
        :type collection_name: str
        """
        super().__init__()
        self.collection_name = collection_name
        self.cache.sadd("collections", collection_name)

    def add_document(self, document, _id=None):
        """
        This method is responsible for adding a document to the cache.
        
        :param document: The document to be cached.
        :type document: dict
        :param _id: The id of the document (default: None)
        :type _id: str
        :return: The id of the document
        :rtype: str
        """
        _id = ObjectId(document.get('_id', _id))
        key = f"{self.collection_name}:{_id}"
        self.cache.hsetnx(self.collection_name, key, pickle.dumps(document))
        self.cache.rpush(self.collection_name+'s', str(_id))
        return _id

    def get_document(self, _id):
        """
        This method is responsible for retrieving a document from the cache.
        
        :param _id: The id of the document.
        :type _id: str
        :return: The document
        :rtype: dict
        """
        key = f"{self.collection_name}:{str(_id)}"
        
        document = self.cache.hget(self.collection_name, key)
        if document is not None:
            return pickle.loads(document)
    
    def get_all_documents(self):
        """
        This method is responsible for retrieving all documents from the cache.
        
        :return: A list of documents
        :rtype: list
        """
        ids = self.cache.lrange(f"{self.collection_name}s", 0, -1)
        keys = [f"{self.collection_name}:{_id.decode()}" for _id in ids]
        documents = self.cache.hmget(self.collection_name, keys, "")
        return [pickle.loads(doc) for doc in documents if doc]
    
    def update_cache(self, document, _id=None):
        _id = ObjectId(document.get('_id', _id))
        key = f"{self.collection_name}:{_id}"
        atual_document = self.get_document(_id)
        atual_document.update(document)
        self.cache.hset(self.collection_name, key, pickle.dumps(atual_document))

    def remove_document(self, _id):
        """
        This method is responsible for removing a document from the cache.
        
        :param _id: The id of the document.
        :type _id: str
        """
        key = f"{self.collection_name}:{_id}"
        self.cache.hdel(self.collection_name, key)
        self.cache.lrem(self.collection_name+'s', 0, str(_id))

    def clear_cache(self):
        """
        This method is responsible for clearing the cache.
        """
        self.cache.delete(self.collection_name)
        self.cache.delete(self.collection_name+'s')
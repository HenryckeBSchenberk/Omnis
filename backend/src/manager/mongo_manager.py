from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from os import environ, getenv
from api import logger, exception, levels, lvl, custom_handler
from api.decorators import for_all_methods
from api.log import custom_handler, DEBUG
from pandas import DataFrame

from numpy import integer, floating, ndarray
from json import loads, dumps, JSONEncoder
from bson.errors import InvalidDocument
from bson import DBRef, ObjectId
from threading import Event

load_dotenv()
load_dotenv(f'.env.{environ.get("NODE_ENV")}')

url = (
    f"mongodb://{getenv('DB_HOST', '0.0.0.0')}:{environ.get('DB_PORT', '27017')}/"
    if environ.get("DB_MODE") != "cloud"
    else f"mongodb+srv://{getenv('DB_USER')}:{getenv('DB_PASS')}@cluster0.diykb.mongodb.net/test?retryWrites=true&w=majority"
)

_db = None


@exception(logger)
def getDb():
    global _db
    if _db is None:
        _db = MongoOBJ(environ.get("DB_NAME"), url)
        custom_handler(logger, "mongo", "json",  _db, levels[lvl]) #! Works?
    return _db


@exception(logger)
def connectToMongo(database="Teste"):
    getDb()
    for collectionName, default_value in {"users":[{'username':'admin', 'first_name':'DELETE THIS USER', 'last_name':'', 'email':'', 'level':'developer'}],
    'serial-manager':[{
  "_id": "6244b0ad3a8338aceae46cf1",
  "name": "OMNIS_CNC",
  "port": "/dev/OMNIS_OCTOPUS",
  "baudrate": 250000,
  "is_gcode": True,
  "disabled": False
}]}.items() :
        if collectionName not in _db.list_collection_names():
            _db.create_collection(collectionName)
            _db.insert_many(collectionName, default_value)

# @for_all_methods(exception(logger))
class CustomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, integer):
            return int(obj)
        elif isinstance(obj, floating):
            return float(obj)
        elif isinstance(obj, ndarray):
            return obj.tolist()
        elif isinstance(obj, ObjectId):
            return str(obj)
        else:
            return super(CustomEncoder, self).default(obj)





# @for_all_methods(exception(logger))
class MongoOBJ:
    def __init__(self, db_name, db_url):
        self.dbo = self.connect(db_name, db_url)
        self.closed = Event()

    def connect(self, db_name, db_url):
        try:
            logger.debug(f"Connecting to MongoDB using url: {db_url}")
            self.client = MongoClient(db_url)
            self.client.admin.command("ismaster")
        except ConnectionFailure:
            logger.error(f"Could not connect to MongoDB using url: {db_url}")
            raise
        else:
            logger.info("Connected to MongoDB")
            return self.client.get_database(db_name)

    def getDB(self):
        return self.dbo

    def list_collection_names(self):
        return self.dbo.list_collection_names()

    def get_collection(self, collectionName):
        return self.dbo.get_collection(collectionName)

    def create_collection(self, collectionName):
        return self.dbo.create_collection(collectionName)

    def insert_one(self, collection_name, data):
        return self.dbo[collection_name].insert_one(data)

    def insert_many(self, collection_name, data):
        return self.dbo[collection_name].insert_many(data)

    def resolve_ref(self, cursor):
        if isinstance(cursor, (dict, list, DBRef)):
            if isinstance(cursor, DBRef):
                return self.find_one(cursor.collection, {'_id':cursor.id}, ref=True)
            for key, value in (cursor.items() if isinstance(cursor, dict) else enumerate(cursor)):
                if key in ['object', 'matrix','sketch', 'variable', 'created_by', 'edited_by']:
                    if isinstance(value, DBRef):
                        cursor[key] = self.find_one(value.collection, {'_id':value.id}, ref=True)
                    if isinstance(value, list):
                        cursor[key] = map(self.resolve_ref, value)
        return cursor


    def find_one(self, collection_name, query={}, data={}, **kwargs):
        if kwargs.get('ref'):
            return self.resolve_ref(dict(self.dbo[collection_name].find_one(query, data)))
        return self.dbo[collection_name].find_one(query, data)

    def find_many(self, collection_name, query={}, data={}, **kwargs):
        if kwargs.get('ref'):
            return [self.resolve_ref(dict(value)) for value in self.dbo[collection_name].find(query, data)]
        return self.dbo[collection_name].find(query, data)

    def update_one(self, collection_name, query, data, options={}):
        try:
            return self.dbo[collection_name].update_one(query, data, **options)
        except InvalidDocument:
            return self.dbo[collection_name].update_one(
                query, loads(dumps(data, cls=CustomEncoder)), **options
            )

    def update_many(self, collection_name, query, data):
        return self.dbo[collection_name].update_many(query, data)

    def delete_one(self, collection_name, query={}):
        return self.dbo[collection_name].delete_one(query)

    def delete_many(self, collection_name, query={}):
        return self.dbo[collection_name].delete_many(query)

    def find_one_and_update(self, collection_name, query, data):
        return self.dbo[collection_name].find_one_and_update(query, data)

    def find_one_and_delete(self, collection_name, query={}):
        return self.dbo[collection_name].find_one_and_delete(query)

    def find_one_and_replace(self, collection_name, query, data):
        return self.dbo[collection_name].find_one_and_replace(query, data)

    def distinct(self, collection_name, query="_id"):
        return self.dbo[collection_name].distinct(query)

    def collection2csv(self, collection):
        arr = self.find_many(collection)
        variables = arr[0].keys()
        df = DataFrame([[i.get(j) for j in variables] for i in arr], columns=variables)
        return df.to_csv(index=False)

    def close(self):
        if not self.closed.is_set():
            logger.info("Database connection Closed.")
            self.client.close()
            self.closed.set()

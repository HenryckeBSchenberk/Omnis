from api import dbo, auth, logger
from api.mutations import mutation
from api.queries import query
from bson import ObjectId
from datetime import datetime
from src.utility.crud.user import User
from src.cache import CacheManager

def cache_sync_with_kwargs(cache_manager_func_name):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            if kwargs.pop('cache', True):
                if hasattr(self, 'cache_manager') and callable(getattr(self.cache_manager, cache_manager_func_name)):
                    getattr(self.cache_manager, cache_manager_func_name)(kwargs.get('input', {}), kwargs.get('_id'))
            return result
        return wrapper
    return decorator

def cache_sync_with_id(cache_manager_func_name):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if kwargs.pop('cache', True):
                if hasattr(self, 'cache_manager') and callable(getattr(self.cache_manager, cache_manager_func_name)):
                    result = getattr(self.cache_manager, cache_manager_func_name)(kwargs.get('_id'))
                    if cache_manager_func_name != 'remove_document':
                        if result is not None:
                            return result
                        logger.warning(f"[{kwargs.get('_id')}] document is not cached yet, fetching from database...")
                else:
                    logger.warning(f"Cache manager not found for {self.collection} or {cache_manager_func_name} is not a callable.")
            result = func(self, *args, **kwargs)
            if cache_manager_func_name == 'get_document':
                if result is not None:
                    logger.warning(f"Adding document to cache: {kwargs.get('_id')}")
                    self.cache_manager.add_document(result, kwargs.get('_id'))
                else:
                    raise KeyError(f"Document not found: {kwargs.get('_id')}")
            return result
        return wrapper
    return decorator

class CRUD:
    def __init__(self, collection, auth_level):
        self.collection = collection
        self.auth_level = auth_level
        self.cache_manager = CacheManager(collection)
        if auth_level is None: 
            self.auth_level = 'developer'
            logger.warning(f"Auth level not set for {collection}_CRUD, defaulting to {self.auth_level}")
            
        self.user = User(f'{collection}', 'CRUD', self.auth_level, '')

        self.create = (
            (auth(self.auth_level))(self.create) if self.auth_level else self.create
        )
        mutation.set_field(f"create_{self.collection}", self.create)

        self.update = (
            (auth(self.auth_level))(self.update) if self.auth_level else self.update
        )
        mutation.set_field(f"update_{self.collection}", self.update)

        self.delete = (
            (auth(self.auth_level))(self.delete) if self.auth_level else self.delete
        )
        mutation.set_field(f"delete_{self.collection}", self.delete)

        self.duplicate = (
            (auth(self.auth_level))(self.duplicate)
            if self.auth_level
            else self.duplicate
        )
        mutation.set_field(f"duplicate_{self.collection}", self.duplicate)

        self.get_list = (
            (auth(self.auth_level))(self.get_list) if self.auth_level else self.get_list
        )
        query.set_field(f"get_{self.collection}_list", self.get_list)

        self.get_item = (
            (auth(self.auth_level))(self.get_item) if self.auth_level else self.get_item
        )
        query.set_field(f"get_{self.collection}_item", self.get_item)

    @cache_sync_with_kwargs('add_document')
    def create(self, *args, **kwargs):
        logger.debug(f"Creating [{kwargs.get('_id')}] in database.")
        _id = ObjectId(kwargs.get("_id"))
        kwargs["input"].update(
            {
                "created_by": kwargs["user"].dbref,
                "created_at": datetime.utcnow().timestamp(),
                "_id": _id,
            }
        )
        dbo.insert_one(
            kwargs.get("collection", self.collection), kwargs.get("input", {})
        )
        return _id

    @cache_sync_with_kwargs('update_cache')
    def update(self, *args, **kwargs):
        logger.debug(f"Updating [{kwargs.get('_id')}] in database.")
        _id = ObjectId(kwargs.get("_id"))
        kwargs.get("input", {"input":{}}).update ({
            "edited_by": kwargs["user"].dbref,
            "updated_at": datetime.utcnow().timestamp(),
        })

        dbo.update_one(
            kwargs.get("collection", self.collection),
            {"_id": _id},
            {"$set": kwargs.get("input", {})},
        )
        return _id

    def duplicate(self, *args, **kwargs):
        logger.debug(f"Duplicating [{kwargs.get('_id')}] from database.")
        item = self.get_item(*args, **kwargs)
        item.pop("_id")
        kwargs.pop("_id")
        if item.get("name"):
            item.update({"name": item["name"] + " - copy"})
        new_id = self.create(*args, **kwargs, input=item)
        self.update(*args, **kwargs, _id=new_id) #???
        return new_id

    @cache_sync_with_id('remove_document')
    def delete(self, *args, **kwargs):
        logger.debug(f"Deleting [{kwargs.get('_id')}] from database.")
        _id = ObjectId(kwargs.get("_id"))
        dbo.delete_one(kwargs.get("collection", self.collection), {"_id": _id})


    # @cache_sync_with_id('get_all_documents') #How resolve Refs?
    def get_list(self, *args, **kwargs):
        logger.debug(f"Fetching [{self.collection}] from database.")
        return dbo.find_many(kwargs.get("collection", self.collection), kwargs.get("filter", {}), ref=kwargs.get("ref", True))

    @cache_sync_with_id('get_document')
    def get_item(self, *args, **kwargs):
        logger.debug(f"Fetching [{kwargs.get('_id')}] from database.")
        return dbo.find_one(
            collection_name=kwargs.get("collection", self.collection),
            query=kwargs.get("query", {"_id": ObjectId(kwargs.get("_id"))}),
            data=kwargs.get("filter", {}),
        )


class SSPR(CRUD):
    """
    # Base class for mutations pattern
    S[tart], S[top], P[ause] and R[esume].

    All the mutations are defined as (function_{alias}), and need has the same authenticate level
    """

    def __init__(self, alias, auth_level, **kwargs):
        if kwargs.get("collection"):
            super().__init__(**kwargs, auth_level=auth_level)
        self.alias = alias
        self.auth_level = auth_level

        self.start = (auth(self.auth_level))(self.start)
        mutation.set_field(f"start_{self.alias}", self.start)

        self.stop = (auth(self.auth_level))(self.stop)
        mutation.set_field(f"stop_{self.alias}", self.stop)

        self.pause = (auth(self.auth_level))(self.pause)
        mutation.set_field(f"pause_{self.alias}", self.pause)

        self.resume = (auth(self.auth_level))(self.resume)
        mutation.set_field(f"resume_{self.alias}", self.resume)

        self.select = (auth(self.auth_level))(self.select)
        mutation.set_field(f"select_{self.alias}", self.select)

    def start(self, *args, **kwargs):
        raise TypeError("start not implemented")

    def stop(self, *args, **kwargs):
        raise TypeError("stop not implemented")

    def pause(self, *args, **kwargs):
        raise TypeError("pause not implemented")

    def resume(self, *args, **kwargs):
        raise TypeError("resume not implemented")

    def select(self, *args, **kwargs):
        raise TypeError("resume not implemented")

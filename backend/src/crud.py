from api import dbo, auth, logger
from api.mutations import mutation
from api.queries import query
from bson import ObjectId
from datetime import datetime
from src.cache import CacheManager
from src.user import User


def ExecutarNoCache(cache_name: str, source_before: bool):
    """
    Decorador para sincronizar o cache com o banco de dados.
    
    Arguments:
        cache_name (str): Nome da função do cache a ser utilizada.
        source_before (bool): Se deve executar a função base antes ou depois da chamada ao cache.
    
    Returns:
        decorator: Decorador que pode ser aplicado a uma função.
    """
    def decorator(func):
        """
        Decorador a ser aplicado à função base.
        
        Arguments:
            func (function): Função base a ser sincronizada com o cache.
        
        Returns:
            wrapper: Função envoltória que realiza a sincronização do cache com a função base.
        """
        def wrapper(self, *args, **kwargs):
            """
            Função envoltória que realiza a sincronização do cache com a função base.
            
            Arguments:
                self (object): Referência à instância que está sendo invocada.
                *args (tuple): Tupla de argumentos passados à função base.
                **kwargs (dict): Dicionário de argumentos nomeados passados à função base.
            
            Keyword Arguments:
                cache (bool): Deverá executar o cache? (default: True)
                _id (str): Identificador do documento.
                input (dict): Conteúdo do documento.
            
            Returns:
                result: Resultado da sincronização do cache com a função base.
            """
            cache = kwargs.pop('cache', True)                      # Devera executar o cache?
            cache_func = getattr(self.cache_manager, cache_name)   # Define qual afunção do cache
            if source_before:                                      # Verifica se deve executar a função base antes ou depois
                result = func(self, *args, **kwargs)
                if cache:
                    #? O ideal seria passar **kwargs??, mas isso afeta a definição da função do cache :c
                    cache_func(kwargs.get('input', {}), kwargs.get('_id'))
                return result   # Retorna o valor do banco, (já está em memória mesmo)
            
            elif cache: # Se não for pra executar antes, mas tiver que usar o cache.
                #? O ideal seria passar **kwargs??, mas isso afeta a definição da função do cache :c
                result = cache_func(kwargs.get('_id'))
                #! Função de remoção deve ser executada no source, sempre!
                if cache_name != 'remove_document':
                    if result:
                        return result   # Retorna o valor do cache
                    if kwargs.get('_id'):
                        logger.warning(f"[{self.cache_manager.collection_name}:{kwargs.get('_id')}] not found on cache or expired.")
            # Caso o cache não tenha retornado nada
            result = func(self, *args, **kwargs)    # Executa a função base
            # if cache_name=='get_all_documents':
            if not source_before and cache_name in ['get_document', 'get_all_documents']:
                if result is not None:
                    logger.warning(f"Adding to cache: {kwargs.get('_id')}")

                    # Atualiza o cache
                    #? O ideal seria passar **kwargs??, mas isso afeta a definição da função do cache :c
                    if cache_name == 'get_all_documents':
                        for item in result:
                            self.cache_manager.add_document(item, item.get('_id'))
                            logger.debug(f"[{item.get('_id')}] stored on cache.")
                        if not isinstance(result, list): result.rewind()
                    else:
                        self.cache_manager.add_document(result, kwargs.get('_id'))
                        logger.debug(f"[{kwargs.get('_id')}] stored on cache.")
                else:
                    raise KeyError(f"Document not found: {kwargs.get('_id')}")
            return result
        return wrapper
    return decorator

def ValidadorDeParâmetros(required_params, optional_params=[]):
    def decorator(func):
        def wrapper(self, **kwargs):
            for param in required_params:
                assert kwargs.get(param, False), f'"{param}" parameter cannot be empty'
            #remove all kwags that no in required_params or optional_params
            for param in list(kwargs.keys()):
                if param not in required_params and param not in optional_params:
                    kwargs.pop(param)
            return func(self, **kwargs)
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
            (auth(self.auth_level))(self.create)
        )
        mutation.set_field(f"create_{self.collection}", self.create)

        self.update = (
            (auth(self.auth_level))(self.update)
        )
        mutation.set_field(f"update_{self.collection}", self.update)

        self.delete = (
            (auth(self.auth_level))(self.delete)
        )
        mutation.set_field(f"delete_{self.collection}", self.delete)

        self.duplicate = (
            (auth(self.auth_level))(self.duplicate)
            if self.auth_level
            else self.duplicate
        )
        mutation.set_field(f"duplicate_{self.collection}", self.duplicate)

        self.get_list = (
            (auth(self.auth_level))(self.get_list)
        )
        query.set_field(f"get_{self.collection}_list", self.get_list)

        self.get_item = (
            (auth(self.auth_level))(self.get_item)
        )
        query.set_field(f"get_{self.collection}_item", self.get_item)

    @ExecutarNoCache('add_document', True)
    @ValidadorDeParâmetros(['input', 'user'], ['_id', 'collection'])
    def create(self, input, user, _id=None, collection=None):
        logger.debug(f"Creating [{_id}] in database.")
        _id = ObjectId(_id or input.get('_id'))
        input.update(
            {
                "created_by": user.dbref,
                "created_at": self.now(),
                "_id": _id,
            }
        )
        dbo.insert_one(
            collection or self.collection, input or {}
        )
        return _id

    @ExecutarNoCache('update_document', True)
    @ValidadorDeParâmetros(['input', 'user'], ['_id', 'collection'])
    def update(self, input, user, _id=None, collection=None):
        logger.debug(f"Updating [{_id}] in database.")
        _id = ObjectId(_id or input.get('_id'))
        (input or {}).update ({
            "edited_by": user.dbref,
            "updated_at": self.now(),
        })

        dbo.update_one(
            collection or self.collection,
            {"_id": _id},
            {"$set": input or {}},
        )
        return _id

    #! Não é necessário executar nada no cache, pois o "create" já faz isso
    @ValidadorDeParâmetros(['user', '_id'])
    def duplicate(self, _id, user):
        logger.debug(f"Duplicating [{_id}] from database.")
        item = self.get_item(_id=_id, user=user)
        item.pop("_id")
        if item.get("name"):
            item.update({"name": item["name"] + " - copy"})
        new_id = self.create(_id=ObjectId(),  user=user ,input=item)
        return new_id

    @ExecutarNoCache('remove_document', False)
    @ValidadorDeParâmetros(['_id'], ['collection'])
    def delete(self, _id, collection=None):
        logger.debug(f"Deleting [{_id}] from database.")
        _id = ObjectId(_id)
        dbo.delete_one(collection or self.collection, {"_id": _id})

    @ExecutarNoCache('get_all_documents', False)
    @ValidadorDeParâmetros([], ['collection', 'query', 'filter'])
    def get_list(self, collection=None, query={}, filter={}):
        logger.debug(f"Fetching [{self.collection}] from database.")
        return dbo.find_many(
            collection_name=collection or self.collection,
            query= query,
            data=filter,
        )

    @ExecutarNoCache('get_document', False)
    @ValidadorDeParâmetros(['_id'], ['collection', 'query', 'filter', 'ref'])
    def get_item(self, _id, collection=None, query=None, filter={}):
        logger.debug(f"Fetching [{_id}] from database.")
        return dbo.find_one(
            collection_name=collection or self.collection,
            query=query or {"_id": ObjectId(_id)},
            data=filter,
        )

    def now(self):
        return datetime.utcnow().replace(microsecond=0).timestamp()

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

#{'_id': ObjectId('63dbeff87894945139dfaa4b'), 'content': {'name': 'DB+CACHE+LOCAL', 'type': 'object_test'}, 'created_by': DBRef('users', ObjectId('63dbeff77894945139dfa94d'))                                } 
#{'_id': ObjectId('63dbeff87894945139dfaa4b'), 'content': {'name': 'DB+CACHE+LOCAL', 'type': 'object_test'}, 'created_by': DBRef('users', ObjectId('63dbeff77894945139dfa94d')), 'created_at': 1675358200.68123}

#{'_id': ObjectId('63dbf17392003387cfc8c751'), 'content': {'name': 'DB+CACHE+LOCAL', 'type': 'object_test'}, 'created_by': DBRef('users', ObjectId('63dbf17292003387cfc8c653')), 'created_at': 1675358520.0}
#{'_id': ObjectId('63dbf17392003387cfc8c751'), 'content': {'name': 'DB+CACHE+LOCAL', 'type': 'object_test'}, 'created_by': DBRef('users', ObjectId('63dbf17292003387cfc8c653')), 'created_at': 1675358520.0}
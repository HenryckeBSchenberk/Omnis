from src.crud import CRUD

def sync(crud_operation):
    """
    Decorador para sincronizar operações CRUD com o gerenciador de coleção
    :param crud_operation: Operação CRUD a ser sincronizada
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if not kwargs.get('user', False):
                raise KeyError('User not found')
            result = getattr(self.crud, crud_operation)(*args, **kwargs)
            return func(self, *args, **kwargs) or result
        return wrapper
    return decorator


class Manager:
    """
    Inicializa uma instância de Manager
    :param collection: Nome da coleção
    :param auth_level: Nível de autorização para operações CRUD
    """
    def __init__(self, collection, auth_level):
        self.crud = CRUD(collection, auth_level)
    
    @sync('update')
    def update(self, *args, **kwargs):
        """
        Atualiza um item na coleção.
        :param args: Argumentos passados para a função
        :param kwargs: Parâmetros nomeados passados para a função
        :raises: NotImplementedError
        """
        raise NotImplementedError
    
    @sync('create')
    def create(self, *args, **kwargs):
        """
        Cria um item na coleção.
        :param args: Argumentos passados para a função
        :param kwargs: Parâmetros nomeados passados para a função
        :raises: NotImplementedError
        """
        raise NotImplementedError

    @sync('delete')
    def delete(self, *args, **kwargs):
        """
        Deleta um item na coleção.
        :param args: Argumentos passados para a função
        :param kwargs: Parâmetros nomeados passados para a função
        :raises: NotImplementedError
        """
        raise NotImplementedError
    
    @sync('duplicate')
    def duplicate(self, *args, **kwargs):
        """
        Método para duplicar um item na coleção.
        :param *args: argumentos posicionais
        :param **kwargs: argumentos nomeados
        """
        raise NotImplementedError

    @sync('get_item')
    def get_item(self, *args, **kwargs):
        """
        Método para obter um item específico da coleção.
        :param *args: argumentos posicionais
        :param **kwargs: argumentos nomeados
        """
        raise NotImplementedError
    
    @sync('get_list')
    def get_list(self, *args, **kwargs):
        """
        Método para obter uma lista de itens da coleção.
        :param *args: argumentos posicionais
        :param **kwargs: argumentos nomeados
        """
        raise NotImplementedError
from bson import ObjectId
from src.nodes.manager import Manager as BaseManager, ExecutarNoCrud as sync


class Object:
    out_attrs = ['created_by', 'created_at', 'edited_by', 'updated_at']

    def __init__(self, _id=None, unsync_instances=False, **content):
        """
        A classe "Object" serve para armazenar valores que são compartilhados entre instancias com o mesmo '_id'.

        :param _id: (opcional) ID a ser atribuído ao objeto. Se não for passado, um ID será gerado automaticamente.
        :type _id: int or str
        :param unsync_instances: (opcional) Se True, o objeto será automaticamente registrado no ObjectManager. Padrão: True
        :type unsync_instances: bool
        :param **content: (opcional) Atributos e valores a serem adicionados ao objeto.
        """
        self.__dict__['_id'] = ObjectId(_id)
        self.__dict__['content'] = {}
        if self._id not in Manager.store:
            if not unsync_instances:
                Manager.store[self._id] = self
            else:
                self.__dict__['unsync_instances'] = unsync_instances
        self.__update(**content)

    def __getattr__(self, name):
        return self.__get(name)

    def __setattr__(self, name, value):
        self.__set(name, value)

    def __setitem__(self, name, value):
        self.__set(name, value)

    def __getitem__(self, name):
        return self.__get(name)

    def __get(self, name):
        """
        Método privado que busca uma informação específica do objeto.
        :param name: Nome da informação a ser buscada.
        :return: Valor da informação buscada ou None caso não exista.
        """
        try:
            content = self.pointer["content"]
            if name == "content":
                return content
            return content.get(name, None)
        except KeyError:
            raise KeyError("Object not found locally")

    def __set(self, name, value):
        """
        Método privado que atribui um valor para uma informação específica do objeto.
        :param name: Nome da informação a ser atribuída.
        :param value: Valor a ser atribuído.
        """
        try:
            self.pointer["content"][name] = value
        except KeyError:
            raise KeyError("Object not found locally")

    def load(self, **data):
        """
        Método que carrega informações para o objeto.
        :param data: Dicionário de informações a serem carregadas.
        """
        self.__update(**data)

    def export(self):
        """
        Método que exporta as informações do objeto.
        :return: Dicionário com as informações do objeto.
        """
        return {'_id': self._id, **self.pointer}

    def __update(self, **content):
        """
        Método privado que atualiza as informações do objeto.
        :param content: Dicionário de informações a serem atualizadas.
        """
        try:
            public_atributes = content.pop("content", {})
            self.pointer["content"].update(public_atributes or content)
            for k, v in {k: v for k, v in content.items() if k in Object.out_attrs}.items():
                self.pointer[k] = v
        except KeyError:
            raise KeyError("Object not found locally")

    @property
    def pointer(self):
        """
        Retorna o ponteiro do objeto, ou seja, a instancia com mesmo _id armazenada no manager.
        :return: Ponteiro do objeto.
        """
        if self.__dict__.get('unsync_instances',False):
            return self.__dict__
        return Manager.store[self._id].__dict__

    def __str__(self):
        return str(self.export())

    def __repr__(self):
        return self.__str__()


class Object_Manager(BaseManager):
    """
    A classe Object_Manager é uma classe que herda de BaseManager e é responsável por gerenciar os objetos do tipo Object na aplicação. Ela possui os seguintes métodos:

    `create(self, *args, **kwargs)`: cria um novo objeto do tipo Object com os dados especificados em `kwargs['input']`. Este método é decorado com a função `sync('create')`
    `update(self, *args, **kwargs):` atualiza os dados de um objeto existente com os dados especificados em `kwargs['input']`. O objeto é identificado pelo _id especificado em kwargs. Este método é decorado com a função `sync('update')`
    `get_item(self, *args, **kwargs):` retorna o objeto identificado pelo `_id` especificado em kwargs. Este método é decorado com a função `sync('get_item')`
    `get_list(self, *args, **kwargs):` retorna uma lista com todos os objetos gerenciados pela classe. Este método é decorado com a função `sync('get_list')`
    `delete(self, *args, **kwargs):` remove o objeto identificado pelo `_id` especificado em kwargs da lista de objetos gerenciados pela classe. Este método é decorado com a função `sync('delete')`
    """
    def __init__(self) -> None:
        super().__init__("object", 'operator')
        self.store = {}

    def get_by_name(self, name):
        """
            Busca um objeto pelo nome
        :param name: nome do objeto
        """
        for obj in self.store.values():
            if obj.name == name:
                return obj

    @sync('create')
    def create(self, input, user):
        """
            Cria um objeto
        :param input: dicionário com dados do objeto
        :param user: usuário autorizado

        :_id: É opcional e será gerado automaticamente caso não seespecificado. Instancias com o mesmo _id serão consideradas a mesma instancia.
        """
        _id = Object(**input, created_by=user.dbref, created_at=self.now())._id
        input.update({'_id':_id })     # Export _id for CRUD sync
        

    @sync('duplicate')
    def duplicate(self, *args, **kwargs):
        pass

    @sync('update')
    def update(self, _id, input, user):
        """
            Atualiza um objeto
        :param _id: id do objeto a ser atualizado
        :param user: usuário autorizado
        :param input: dicionário com dados do objeto
        """
        # _id = kwargs.get('_id')
        obj = self.store.get(_id, None)
        if obj:
            obj.load(**input, edited_by=user.dbref, updated_at=self.now())
        else:
            raise KeyError("Object not found locally")

    @sync('get_item')
    def get_item(self, *args, **kwargs):
        """
            Busca um objeto pelo id
        :param _id: id do objeto
        :param user: usuário autorizado
        :return: objeto encontrado ou None
        """
        return self.store.get(kwargs.get('_id'), None)

    @sync('get_list')
    def get_list(self, *args, **kwargs):
        """
            Lista todos os objetos
        :param user: usuário autorizado
        :return: lista de objetos
        """
        return self.store.values()

    @sync('delete')
    def delete(self, *args, **kwargs):
        """
            Deleta um objeto pelo id
        :param _id: id do objeto
        :param user: usuário autorizado
        :return: None
        """
        _id = kwargs.get('_id')
        if _id in self.store:
            self.store.pop(_id)

    def set_from_cached(self, cached):
        if isinstance(cached, dict):
            if all([item in cached for item in['_id', 'content']]):
                return Object(**cached) # add to store automatically
        return cached
    

Manager = Object_Manager()

from bson import ObjectId
from bson.dbref import DBRef

class Person:
    def __init__(self, first_name, last_name) -> None:
        self.__first_name = first_name
        self.__last_name = last_name

    @property
    def first_name(self):
        return self.__first_name.lower()

    @property
    def full_name(self):
        return (self.__first_first_name + " " + self.__last_name).lower()

    @property
    def last_name(self):
        return self.__last_name.lower()


class Role:
    USER = 0
    VIEWER = USER + 1
    OPERATOR = USER + 8
    MAINTENANCE = OPERATOR + 8
    MANAGER = MAINTENANCE + 8
    DEVELOPER = MANAGER + 8
    SUDO = DEVELOPER + 8


class User(Person):
    def __init__(
        self,
        first_name,
        last_name,
        level,
        email,
        avatar_image=None,
        _id=None,
        **kwargs
    ) -> None:
        super().__init__(first_name, last_name)
        self.email = email
        self.avatar_image = avatar_image
        self.__level = level
        self._id = ObjectId(_id)
        self.dbref = DBRef("users", self._id)

    @property
    def level(self):
        return User.__normalize_level(self.__level)

    def __normalize_level(level):
        return getattr(Role, level.upper(), None)

    def __ge__(self, other):
        return self.level >= User.__normalize_level(other)

    def __eq__(self, other):
        return self.level == User.__normalize_level(other)

    def __le__(self, other):
        return self.level <= User.__normalize_level(other)

    def __ne__(self, other):
        return self.level != User.__normalize_level(other)

    def __str__(self) -> str:
        return str(vars(self))
    
    @property
    def json(self):
        return {
        'first_name':self.first_name,
        'last_name':self.last_name,
        'level':self.__level,
        'email':self.email,
        'avatar_image':self.avatar_image,
        '_id':str(self._id),
        }


if __name__ == "__main__":
    user = User(
        "Henrycke",
        "Bozza Schenberk",
        "developer",
        "henrycke.bozza@test.com.br",
    )
    print(user.level, user._id, user >= "developer", user.json)

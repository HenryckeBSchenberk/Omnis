from os import environ
from platform import system
from dotenv import load_dotenv
from .log import logger, exception, custom_handler, logger, levels, lvl
from .decorators import for_all_methods
import jwt
from graphql.type import GraphQLResolveInfo
from graphql.error import GraphQLError

from src.manager.mongo_manager import connectToMongo, getDb

load_dotenv()
load_dotenv(f'.env.{environ.get("NODE_ENV")}')
environ.setdefault("SO", system())

connectToMongo()
dbo = getDb()

key_context = dbo.find_one("keys")
if key_context is None: key_context = {"path":'../.ssh/key', "pass":""}
from cryptography.hazmat.primitives.serialization import load_ssh_private_key, load_ssh_public_key
# try
with open(key_context["path"], "r") as private, open(key_context["path"]+'.pub', "r") as public:
    private_key = load_ssh_private_key(private.read().encode(), key_context["pass"].encode())
    public_key =  load_ssh_public_key(public.read().encode(), key_context["pass"].encode())
# except

from src.utility.crud.user import User

def auth(lvl=None):
    def decorator(resolver):
        def wrapper(obj=None, info: GraphQLResolveInfo=None, logged=None, *args, **kwargs):
            try:
                if not kwargs.get('user'):
                    token = info.context["request"].headers.get('authorization').split(' ')[-1]
                    header_data = jwt.get_unverified_header(token)
                    token = jwt.decode(token, key=public_key, algorithms=[header_data['alg']])
            except Exception as e:
                logger.debug(f"Acess Denied, invalid or missing token: {e}.")
                raise GraphQLError("Invalid credential")
            else:
                user = User(**token) if not kwargs.get('user') else kwargs.get('user')
                if user >= lvl:
                    logger.debug(f"User: {user.json} requesting {resolver.__name__}")
                    kwargs.update({'user':user})
                    return resolver(*args, **kwargs)
                    # return resolver(obj, info, *args, **kwargs)
                logger.debug(f"User: {user.json} don't has permissions to request {resolver.__name__}")
                raise GraphQLError('Permission Denied')
        return wrapper
    return decorator
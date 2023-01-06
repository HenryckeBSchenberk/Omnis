from os import environ, makedirs, path
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

## A function to create a pair of public and private keys for JWT authentication, using ed25519 algorithm
def generate_keys_bytes():
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization

    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_bytes, public_bytes

## Try to load the keys from the correspondent files, if it doesn't exist, create a new pair and save it to the files
keys_path = "./keys"

try:
    with open(f'{keys_path}/priv', 'rb') as private_key_file, open(f'{keys_path}/pub', 'rb') as public_key_file:
        private_key = private_key_file.read()
        public_key = public_key_file.read()
except (FileNotFoundError, IOError):
    private_key, public_key = generate_keys_bytes()
    makedirs(path.dirname(f'{keys_path}/priv'), exist_ok=True)
    makedirs(path.dirname(f'{keys_path}/pub'), exist_ok=True)
    with open(f'{keys_path}/priv', 'wb') as private_key_file, open(f'{keys_path}/pub', 'wb') as public_key_file:
        private_key_file.write(private_key)
        public_key_file.write(public_key)


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
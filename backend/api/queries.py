from bson import ObjectId
from .models import  grok
from ariadne import QueryType
query = QueryType()

from src.nodes.node_manager import NodeManager
from src.nodes.node_registry import NodeRegistry
from threading import enumerate as thread_enumerate
from src.manager.camera_manager import CameraManager
from src.nodes.serial.manager import Manager as SerialManager
# from src.nodes.calibration.camera_calibration import CameraCalibration #! docker build fails to install aruco module

from api import dbo, logger, environ, auth, private_key
from datetime import datetime, timedelta, timezone
import jwt
from graphql.error import GraphQLError

import argon2
ph = argon2.PasswordHasher()

payload = {"success": False, "errors": None}


@query.field("allPhotos")
@auth('developer')
def resolve_allPhotos( **kwargs):
    """Get all photos from the database"""
    payload = [{"filename": "a.png", "path": "imgs/a.png"}]
    return payload


@query.field("getSerials")
@auth('viewer')
def resolve_getSerials( **kwargs):
    return {"status": True, "data": SerialManager.get()}


@query.field("getCameras")
@auth('viewer')
def resolve_getCameras( **kwargs):
    return {"status": True, "data": CameraManager.get()}


@query.field("getNodeInfo")
@auth('operator')
def resolve_getNodeInfo( node_type, **kwargs):
    """Get a Node by id and return it like a payload"""
    result = (NodeRegistry.getNodeClassByName(node_type)).get_info(
        **kwargs.get("kwargs", {})
    )
    return {"status": True, "data": result}


@query.field("getManutention")
@auth('maintenance')
def resolve_getManutention( **kwargs):
    """Get a Node by id and return it like a payload"""
    return {"status": True, "data": grok.get_url()}


@query.field("getThr")
@auth('developer')
def resolve_getThr( **kwargs):
    """Get a Node by id and return it like a payload"""
    return list([thread.name for thread in thread_enumerate()])


@query.field("calibrateCamera")
@auth('maintenance')
def resolve_calibrateCamera( **kwargs):
    # Thread(target=CameraCalibration(**kwargs.get("input", {})).calibrate).start()
    return True


@query.field("getLoadedNodes")
@auth('developer')
def resolve_getLoadedNodes( **kwargs):
    """Get a Node by id and return it like a payload"""
    return NodeManager.getActiveNodes()

@query.field("getDevicesList")
@auth('operator')
def resolve_getDevicesList( **kwargs):
    """Get a Node by id and return it like a payload"""
    temp = list(dbo.find_many("pins"))
    for i in temp:
        i["_id"] = str(i["_id"])
    return temp

@query.field("getMacrosList")
@auth('operator')
def resolve_getMacrosList( **kwargs):
    return []
@query.field("getAxisList")
@auth('operator')
def resolve_getAxisList( **kwargs):
    """Get a Node by id and return it like a payload"""
    temp = list(dbo.find_many("machine_axis"))
    for i in temp:
        i["_id"] = str(i["_id"])
    return temp

@query.field("authenticateUser")
def resolve_authUserProfile(obj, info, username=None, **kwargs):
    user = dbo.find_one("users", {"username": username}) if username else dbo.find_one("users", kwargs)
    try:
        if user:

            password = user.pop('password', None)
            payload = user.copy()

            if ph.verify(password, kwargs['password']):
                if ph.check_needs_rehash(password):
                    payload.update({'password':ph.hash(kwargs['password'])})

                payload.update({"exp": datetime.now(tz=timezone.utc) + timedelta(hours=payload.get('exp', 48)), '_id': str(payload['_id'])})

                token = jwt.encode(
                    payload,
                    key=private_key,
                    algorithm="EdDSA",
                )

                now = datetime.utcnow().timestamp()
                dbo.update_one('users', {'_id':ObjectId(user['_id'])}, {'$set':{'last_access':now}})
                user.update({'last_access': now})

                return {"user": user, "token": token}
    except argon2.exceptions.InvalidHash:
        logger.error("Invalid Hash on user: " + str(user['_id']))
    except argon2.exceptions.VerifyMismatchError:
        pass
    raise GraphQLError("Invalid Login")

@query.field("authUserProfile")
@auth('user')
def resolve_authUserProfile(user=None):
    return user.json

@query.field("getUsersList")
@auth('manager')
def  getUsersList_resolver(user=None):
    return list(dbo.find_many('users', {}, {'password':0}))

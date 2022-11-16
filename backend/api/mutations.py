from datetime import datetime
import threading
from time import sleep
from .models import ObjectId
from ariadne import MutationType
from src.nodes.alerts.alert_obj import Alert
from numpy import uint8, frombuffer
from cv2 import imdecode, imwrite
from os.path import abspath

from src.nodes.camera.custom_camera import Camera
from src.nodes.serial.client import CustomSerial as Serial

from src.manager.camera_manager import CameraManager
from src.nodes.serial.manager import Manager as SerialManager

from src.utility.system.date import set_system_date
from api import logger, auth, dbo
import os
mutation = MutationType()

def restart():
    sleep(2)
    os._exit(1)

@mutation.field("restart")
@auth('operator')
def restart_resolver(*args, **kwargs):
    try:
        logger.warning(f"User {kwargs.get('user').first_name} restarting machine at: {datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}")
    finally:
        threading.Thread(target=restart).start()
        return 15 #? How to calculate time of reboot?



@mutation.field("createAlert")
@auth("developer")
def createAlert_resolver(*args, **kwargs):
    """Create a new Alert object and return it like a payload"""
    returns = Alert(**kwargs.get('input')).items()
    return returns


@mutation.field("uploadFile")
async def uploadFile_resolver( file, **kwargs):
    """Upload a file and return it like a payload"""
    print(file)
    return {"data": file}


class Picture:
    def __init__(self, name, _id=ObjectId(), **kwargs):
        self._id = _id
        self.name = name[:-3]
        self.extension = name[-3:]
        self.path = f"/imgs/{self._id}"

    def export(self, path, img, **kwargs):
        """Export the picture to the path"""
        imwrite(path, img)
        return self.__dict__


@mutation.field("uploadPhoto")
async def uploadPhoto_resolver( **kwargs):
    name = kwargs.get("photo").filename
    p = Picture(name)
    path = f"{abspath('./src')}/{p.path}"
    img = imdecode(frombuffer(kwargs.get("photo").file.read(), uint8), 1)
    print(p.export(path, img))
    return {"filename": p.id, "path": p.path}


@mutation.field("takePhoto")
async def takePhoto_resolver(*args, **kwargs):
    camera_id = kwargs.get("camera_id")
    p = Picture(str(camera_id))
    path = f"{abspath('./src')}/{p.path}{p.name}.jpeg"
    img = CameraManager.get_by_id(camera_id).read()
    print(p.export(path, img))
    return {"filename": p._id, "path": p.path}


# *  ----------- Cameras ----------- * #
@mutation.field("createCamera")
def createCamera_resolver( **kwargs):
    """Create a new Camera object and return it like a payload"""
    returns = Camera(**kwargs.get("input", {})).to_dict()
    return {"data": returns}


@mutation.field("startCamera")
def startCamera_resolver( _id, **kwargs):
    """Start a camera by id and return it like a payload"""
    camera = CameraManager.get_by_id(_id)
    returns = camera.to_dict()
    return {"data": returns}


@mutation.field("stopCamera")
def stopCamera_resolver( _id, **kwargs):
    """Stop a camera by id and return it like a payload"""
    camera = (CameraManager.get_by_id(_id)).stop()
    returns = camera.to_dict()
    return {"data": returns}


@mutation.field("resetCamera")
def resetCamera_resolver( _id, **kwargs):
    """Reset a camera by id and return it like a payload"""
    camera = (CameraManager.get_by_id(_id)).reset()
    returns = camera.to_dict()
    return {"data": returns}


@mutation.field("setCameraProperty")
def setCameraProperty_resolver( _id, **kwargs):
    """Set a camera property by id and return it like a payload"""
    camera = CameraManager.get_by_id(_id)
    returns = camera.set_properties(kwargs.get("input", {}))
    return {"data": returns}


# *  ----------- Serial ----------- * #
@mutation.field("createSerial")
def createSerial_resolver( **kwargs):
    """Create a new Serial object and return it like a payload"""
    returns = Serial(**kwargs.get("input", {})).to_dict()
    return returns


@mutation.field("startSerial")
def startSerial_resolver( _id, **kwargs):
    """Start a serial by id and return it like a payload"""
    serial = SerialManager.get_by_id(_id)
    returns = serial.to_dict()
    return returns


@mutation.field("stopSerial")
def stopSerial_resolver( _id, **kwargs):
    """Stop a serial by id and return it like a payload"""
    serial = SerialManager.get_by_id(_id).stop()
    returns = serial.to_dict()
    return returns


@mutation.field("sendSerial")
@auth("operator")
def sendSerial_resolver( _id, payload, **kwargs):
    """Communicate a serial by id and return it like a payload"""
    serial = SerialManager.get_by_id(_id)
    serial.send(payload)
    return serial.to_dict()


@mutation.field("syncHostTime")
def syncHostTime_resolver( timestamp, **kwargs):
    """Sync the host time with the server time"""
    try:
        set_system_date(timestamp)
    except Exception:
        return False
    return True


# *  ----------- User ----------- * #
@mutation.field("registerUser")
@auth("manager")
def registerUser_resolver( **kwargs):
    dbo.insert_one("users", kwargs["newUser"])
    return True


@mutation.field("deleteUser")
@auth("manager")
def deleteUser_resolver( _id, user, **kwargs):
    dbo.delete_one("users", {"_id": ObjectId(_id)})
    return True


@mutation.field("updateUser")
@auth("manager")
def updateUser_resolver( _id, **kwargs):
    dbo.update_one("users", {"_id": ObjectId(_id)}, {"$set": kwargs["input"]})
    return True

from api import dbo, logger
from .custom_camera import Camera
logger.debug('Camera module loaded')
for config in dbo.find_many("camera-manager", {}):
    if not config.get("disabled", False):
        # Camera(**config, **config.get("options"))
        logger.info('Automatically creating camera "{}"'.format(config.get("name")))
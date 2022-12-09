def setup():
    from api import dbo, logger
    from .camera import CustomCamera as Camera
    from os import environ as env

    dbo_config = list(dbo.find_many("camera-manager")) if dbo else []
    env_config = []
    
    qtd_camreas = int(env.get('qtd_cameras', 0))
    for index in range(qtd_camreas):
        host = env.get(f'camera_host_{index}')
        port = env.get(f'camera_port_{index}')
        _id = env.get(f'camera_id_{index}')
        
        if all([host, port, _id]):
            env_config.apped(
                {
                    'host':host,
                    'port':port,
                    '_id':_id
                }
            )
    

    cameras = env_config + dbo_config 
    cameras = filter(lambda camera: camera.get('host') and camera.get('port'), cameras)
    
    logger.debug('Camera module loaded')
    for config in cameras:
        if not config.get("disabled", False):
            Camera(host=config.get('host'), port=config.get('port'), _id=config.get('_id'))
            logger.info('Automatically creating camera "{}"'.format(config.get("name")))
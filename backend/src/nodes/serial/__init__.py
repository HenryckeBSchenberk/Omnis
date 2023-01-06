def setup():
    from api import dbo, logger
    from .gcode import Client as GcodeClient
    from src.nodes.serial.pins_obj import pin
    from src.nodes.serial.axes import axis
    from src.nodes.serial.sensors import Sensor
    from src.nodes.serial.machine import Machine

    logger.info('Serial and MarlinAPI modules loaded')
    pins = [pin(**p) for p in dbo.find_many("pins")]

    pipeline = [
        {"$match": {"disabled": {"$ne": True}}},                # Only enabled axes
        {"$project": {"name": 1, "board": 1, "sensors": 1}},    # Only name, board and sensors
        {"$lookup": {                                           # Find sensors
            "from": "machine_sensors",                          # Collection to search
            "localField": "sensors.ids",                        # Field to match in the local collection
            "foreignField": "_id",                              # Field to match in the foreign collection
            "as": "sensors"                                     # Output field name (replace the refs with objects)
        }}
    ]

    axes = {
        config['name']: axis(                                   # Store the axis in a dict with the axis name as key
            sensors=[
                Sensor(**s) for s in config.pop('sensors', [])  # Remove the sensors from the config and create the objects
            ],
            **config                                            # Create the axis object whit the remaining config
        ) for config in dbo.aggregate(                          # Aggregate the collection
            "machine_axis",                                     # Collection to aggregate    
            pipeline                                            # Pipeline to execute
        )
    }

    for config in dbo.find_many("serial-manager", {}):
        if not config.get("disabled", False):
            parser = GcodeClient(
                host=config.get("host"),
                port=config.get("service_port"),
                _id=config.get("_id")
            )
            Machine(parser, axes, pins,  config.get("_id"))

def setup():
    from api import dbo, logger
    from .gcode import Client as GcodeClient
    from src.nodes.serial.pins_obj import pin
    from src.nodes.serial.axes import axis
    from src.nodes.serial.machine import Machine

    logger.info('Serial and MarlinAPI modules loaded')
    pins = [pin(**p) for p in dbo.find_many("pins")]
    axes = {
        a['name'].upper(): axis(**a)
        for a in dbo.find_many(
            "machine_axis", data={"_id": 1, "name": 1, "board": 1, "setup": 1}
        )
    }
    for config in dbo.find_many("serial-manager", {}):
        if not config.get("disabled", False):
            parser = GcodeClient(host=config.get("host"), port=config.get("service_port"), _id=config.get("_id"))
            Machine(parser, axes, pins,  config.get("_id"))

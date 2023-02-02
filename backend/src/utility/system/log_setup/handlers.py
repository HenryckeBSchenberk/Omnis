from logging.handlers import TimedRotatingFileHandler
from logging import StreamHandler, FileHandler, Handler
from time import gmtime
from datetime import datetime


def handlers_factory(handler):
    def wrapper(level, formatter, destination):
        h = handler(destination)
        h.setLevel(level)
        h.formatter = formatter
        h.formatter.converter = gmtime
        h.namer = lambda name: name.replace(".json", "") + ".json"
        return h

    return wrapper


@handlers_factory
def stream_handler(destination):
    return StreamHandler(destination)


@handlers_factory
def file_handler(destination):
    return FileHandler(destination)


@handlers_factory
def time_file_handler(destination):
    return TimedRotatingFileHandler(
        destination, when="midnight", interval=1, backupCount=7
    )


@handlers_factory
def mongo_handler(destination):
    return MongoHandler(destination)


class MongoHandler(Handler):
    """
    A logging handler that will record messages to a (optionally capped)
    MongoDB collection.
    >>> connection = pymongo.Connection()
    >>> collection = connection.db.log
    >>> logger = logging.getLogger("mongotest")
    >>> logger.addHandler(MongoHandler(drop=True))
    >>> logger.error("Hello, world!")
    >>> collection.find_one()['message']
    u'Hello, world!'
    """

    def __init__(self, database, level=10, collection="log"):
        super().__init__(level)
        self.database = database
        self.collection = collection

    def emit(self, record):
        r = record.__dict__.copy()
        r["created"] = datetime.fromtimestamp(record.created)
        try:
            if not self.database.closed.is_set():
                self.database.insert_one(self.collection, r)
        except Exception as e:
            print("CustomMongoLogger [ERROR]: ", e, r)


handlers = {
    "stream": stream_handler,
    "file": file_handler,
    "time_file": time_file_handler,
    "mongo": mongo_handler,
}

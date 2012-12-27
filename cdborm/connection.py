from CodernityDB.database import Database, DatabasePathException
from cdborm.model import Model
from cdborm.index import Index

def create_db(database):
    database.create()
    Index.createAllIndexes(database)

def connec_to_database(path, set_as_default_db=False):
    database = Database(path)

    try:
        database.open()
    except DatabasePathException:
        create_db(database)

    if set_as_default_db:
        Model.database = database
    return database

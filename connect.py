import os
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

log = logging.getLogger(__name__)

def get_db():
    # aqui me conecto a mongo, si no hay variable de entorno uso localhost
    mongo_url = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    client = MongoClient(mongo_url)

    # verifico que si haya conexion
    try:
        client.admin.command('ping')
        log.info("Conexion a Mongo exitosa")
    except ConnectionFailure:
        log.error("no se pudo conectar a Mongo")
        raise

    db = client["social_analytics_db"]

    # creo los indices que necesito

    # para que no se repitan correos
    db.users.create_index("email", unique=True)

    # para buscar posts de un usuario ordenados por fecha
    db.posts.create_index([("user_id", 1), ("created_at", -1)])

    # para filtrar por hashtag
    db.posts.create_index("hashtags")

    # para buscar palabras en el contenido
    db.posts.create_index([("content", "text")])

    log.info("indices listos")
    return db

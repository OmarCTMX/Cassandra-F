"""
populate.py - meto datos de prueba a la base de datos
para correrlo: python populate.py
"""
import datetime
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from connect import get_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


# usuarios de prueba
USERS = [
    {
        "username": "Omar Profe",
        "email": "omar@profe.com",
        "password": "pass1234",
        "bio": "Cirujano amante del cafe",
        "profile_pic": "https://drarmandogarcia.com.mx/wp-content/uploads/2018/07/Cirujanos-Generales-en-MOnterrey.jpg",
    },
    {
        "username": "bob",
        "email": "bob@iteso.com",
        "password": "contraseña",
        "bio": "Desarrollador backend profesional",
        "profile_pic": "https://images.griddo.udit.es/c/cover/q/70/w/1920/h/1080/p/center/f/jpeg/desarrollador-front-end-desarrollador-de-back-end-desarrollador-full-stack-conoce-sus-diferencias-2-1920x1080",
    },
    {
        "username": "caro",
        "email": "caro@iteso.com",
        "password": "caro2026",
        "bio": "Diseñadora UX ITESO",
        "profile_pic": "https://unirfp.unir.net/wp-content/uploads/sites/23/2023/07/mujer-diseC3B1adora-que-trabaja-en-el-nuevo-proyecto-de-desarrollo-de-sitios-web.jpg_s1024x1024wisk20cLfSxCtONH5KIjhPEyVYTxV_1el8KPbncCiKh4YHvHmY.jpg",
    },
]

# posts de prueba
POSTS_TEMPLATE = [
    {
        "content": "Explorando las nuevas funciones de Python y Mongo #python #tech",
        "image": "",
        "hashtags": ["python", "tech"],
    },
    {
        "content": "MongoDB es increIble es mi pasion #mongodb #databases",
        "image": "https://example.com/imgs/mongo.png",
        "hashtags": ["mongodb", "databases"],
    },
    {
        "content": "Diseño profesional diseño diseño #ux #design",
        "image": "",
        "hashtags": ["ux", "design"],
    },
    {
        "content": "Me encanta tomar Cafe mientras opero #cafe #agujas",
        "image": "",
        "hashtags": ["medicina", "doctor"],
    },
    {
        "content": "Me encanta programar a corazon abierto",
        "image": "",
        "hashtags": ["python", "medicina"],
    },
]


def populate():
    db = get_db()

    # borro lo que habia antes para empezar limpio
    db.users.delete_many({})
    db.posts.delete_many({})
    log.info("colecciones limpiadas")

    # inserto los usuarios y guardo sus _ids en una lista
    inserted_ids = []
    for user_data in USERS:
        user_data["created_at"] = datetime.datetime.utcnow()
        result = db.users.insert_one(user_data.copy())
        inserted_ids.append(result.inserted_id)
        log.info(f"usuario insertado: {user_data['username']} -> {result.inserted_id}")

    # reparto los posts entre los usuarios de forma ciclica
    # post 0 -> usuario 0, post 1 -> usuario 1, post 2 -> usuario 2
    # post 3 -> usuario 0 (vuelve a empezar), etc.
    num_users = len(inserted_ids)
    for i, post_data in enumerate(POSTS_TEMPLATE):
        owner_id = inserted_ids[i % num_users]
        post = {
            **post_data,
            "user_id": owner_id,
            "created_at": datetime.datetime.utcnow(),
        }
        result = db.posts.insert_one(post)
        log.info(f"post insertado: '{post_data['content'][:40]}...' -> {result.inserted_id}")

    log.info("listo! base de datos poblada")


if __name__ == "__main__":
    populate()

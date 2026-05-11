import csv
import datetime
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from connect import get_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# rutas de los archivos CSV
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
USUARIOS_CSV     = os.path.join(DATA_DIR, "usuarios.csv")
POSTS_CSV        = os.path.join(DATA_DIR, "posts.csv")
INTERACCIONES_CSV = os.path.join(DATA_DIR, "interacciones.csv")


def leer_csv(ruta):
    """lee un csv y devuelve una lista de diccionarios"""
    with open(ruta, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def populate():
    db = get_db()

    # borro lo que habia antes para empezar limpio
    db.users.delete_many({})
    db.posts.delete_many({})
    log.info("colecciones limpiadas")

    # --- INSERTAR USUARIOS ---
    usuarios_csv = leer_csv(USUARIOS_CSV)
    # guardo un mapa de username -> _id para usarlo al insertar posts
    username_to_id = {}

    for row in usuarios_csv:
        user = {
            "username": row["username"],
            "email": row["email"],
            "password": row["password"],
            "bio": row.get("bio", ""),
            "profile_pic": "",
            # los interests del csv los guardo como preferencias
            "preferences": {
                "interests": row.get("interests", ""),
                "theme": "light",
                "notifications": True,
                "language": "es"
            },
            "privacy_settings": {
                "profile_visibility": "public",
                "show_email": False,
                "allow_messages": True
            },
            "created_at": datetime.datetime.utcnow()
        }
        result = db.users.insert_one(user)
        username_to_id[row["username"]] = result.inserted_id
        log.info(f"usuario insertado: {row['username']} -> {result.inserted_id}")

    # --- LEER INTERACCIONES PARA SABER QUIEN POSTEO QUE ---

    interacciones = leer_csv(INTERACCIONES_CSV)
    post_id_to_username = {}
    for row in interacciones:
        if row["relation"] == "posteo":
            post_id = row["target_id"]       
            username = row["source_id"]      
            post_id_to_username[post_id] = username

    # --- INSERTAR POSTS ---
    posts_csv = leer_csv(POSTS_CSV)

    for row in posts_csv:
        post_id = row["post_id"]

        # busco quien es el dueño de este post segun interacciones.csv
        username = post_id_to_username.get(post_id)
        if not username or username not in username_to_id:
            log.warning(f"no encontre autor para el post {post_id}, lo salto")
            continue

        # los hashtags vienen como "#cars,#civic", los limpio y separo
        hashtags_raw = row.get("hashtags", "")
        hashtags = [h.strip().lstrip("#") for h in hashtags_raw.split(",") if h.strip()]

        # el timestamp del csv lo convierto a datetime, si falla uso la fecha actual
        try:
            created_at = datetime.datetime.fromisoformat(row["timestamp"].replace("Z", ""))
        except (ValueError, KeyError):
            created_at = datetime.datetime.utcnow()

        post = {
            "user_id": username_to_id[username],
            "content": row["content"],
            "image": "",
            "hashtags": hashtags,
            "created_at": created_at
        }
        result = db.posts.insert_one(post)
        log.info(f"post insertado: '{row['content'][:40]}...' -> {result.inserted_id}")

    log.info("listo! base de datos poblada desde los CSVs")


if __name__ == "__main__":
    populate()

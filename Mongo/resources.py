import datetime
import falcon
from pymongo.errors import DuplicateKeyError

# ---------------------------------------------------------------------------
# esquemas: defino campos de cada coleccion y de que tipo deben ser
# ---------------------------------------------------------------------------

user_types = {
    "username": str,
    "email": str,
    "password": str,
    "bio": str,
    "profile_pic": str
}

post_types = {
    "user_id": str,   # aqui mando el correo del usuario
    "content": str,
    "image": str,
    "hashtags": list
}


def validate_data(data, expected_types):
    """revisa que los campos del JSON sean validos y del tipo correcto"""
    if not isinstance(data, dict):
        raise falcon.HTTPBadRequest(description="el body tiene que ser un JSON")

    for field in list(data.keys()):
        # si el campo no esta en el esquema, lo rechazo
        if field not in expected_types:
            raise falcon.HTTPBadRequest(description=f"campo no permitido: {field}")

        try:
            if expected_types[field] == list:
                # los hashtags son lista, verifico que si sea lista
                if not isinstance(data[field], list):
                    raise ValueError
                # limpio espacios de cada hashtag
                data[field] = [str(item).strip() for item in data[field]]
            else:
                # convierto el valor al tipo esperado 
                data[field] = expected_types[field](data[field])
        except ValueError:
            raise falcon.HTTPBadRequest(
                description=f"tipo de dato malo en '{field}', debe ser {expected_types[field].__name__}"
            )

    return data


def find_user_by_email(db, email):
    """busca un usuario por correo, lanza error 404 si no existe"""
    user = db.users.find_one({"email": email})
    if not user:
        raise falcon.HTTPNotFound(description=f"no encontre un usuario con el correo: {email}")
    return user


def serialize_post(post):
    """convierte un post de mongo a un dict que se puede mandar como JSON"""
    post["_id"] = str(post["_id"])
    post["user_id"] = str(post["user_id"])
    post["created_at"] = post["created_at"].isoformat()
    return post


def serialize_user(user):
    """convierte un usuario de mongo a un dict que se puede mandar como JSON"""
    user["_id"] = str(user["_id"])
    user["created_at"] = user["created_at"].isoformat()
    return user


# ---------------------------------------------------------------------------
# recursos (cada clase maneja una ruta de la API)
# ---------------------------------------------------------------------------

class UsersResource:
    """maneja POST /api/users -> registrar usuario nuevo"""

    def __init__(self, db):
        self.db = db

    async def on_post(self, req, resp):
        data = await req.media
        data = validate_data(data, user_types)

        # verifico que tenga los tres campos obligatorios
        for campo in ["username", "email", "password"]:
            if campo not in data or not data[campo]:
                raise falcon.HTTPBadRequest(description=f"falta el campo obligatorio: {campo}")

        # si no mandan bio o foto, los dejo vacios
        data.setdefault("bio", "")
        data.setdefault("profile_pic", "")
        data["created_at"] = datetime.datetime.utcnow()

        try:
            result = self.db.users.insert_one(data)
            data["_id"] = str(result.inserted_id)
            data["created_at"] = data["created_at"].isoformat()
            resp.media = data
            resp.status = falcon.HTTP_201
        except DuplicateKeyError:
            raise falcon.HTTPConflict(description="ese correo ya esta registrado")


class UserResource:
    """maneja PUT /api/users/{email} -> actualizar perfil"""

    def __init__(self, db):
        self.db = db

    async def on_put(self, req, resp, email):
        # primero busco al usuario por correo
        user = find_user_by_email(self.db, email)

        data = await req.media
        data = validate_data(data, user_types)

        # no permito cambiar el correo ni la contraseña por esta ruta
        data.pop("email", None)
        data.pop("password", None)

        if not data:
            resp.media = {"mensaje": "no mandaste nada para actualizar"}
            resp.status = falcon.HTTP_200
            return

        # actualizo solo los campos que me mandaron
        self.db.users.update_one({"_id": user["_id"]}, {"$set": data})

        # devuelvo el usuario con los datos ya actualizados
        updated_user = self.db.users.find_one({"_id": user["_id"]})
        resp.media = serialize_user(updated_user)
        resp.status = falcon.HTTP_200


class PostsResource:
    """maneja POST y GET /api/posts -> crear posts y consultarlos"""

    def __init__(self, db):
        self.db = db

    async def on_post(self, req, resp):
        # crear un post nuevo
        data = await req.media
        data = validate_data(data, post_types)

        if not data.get("user_id"):
            raise falcon.HTTPBadRequest(description="necesito el correo del usuario en 'user_id'")
        if not data.get("content", "").strip():
            raise falcon.HTTPBadRequest(description="el contenido del post no puede estar vacio")

        # busco al usuario por correo y guardo su _id en el post
        user = find_user_by_email(self.db, data["user_id"])
        data["user_id"] = user["_id"]

        data.setdefault("image", "")
        data.setdefault("hashtags", [])
        data["created_at"] = datetime.datetime.utcnow()

        result = self.db.posts.insert_one(data)
        data["_id"] = str(result.inserted_id)
        data["user_id"] = str(data["user_id"])
        data["created_at"] = data["created_at"].isoformat()

        resp.media = data
        resp.status = falcon.HTTP_201

    async def on_get(self, req, resp):
        """
        acepta estos parametros en la URL:
          ?user_id=correo   -> posts de ese usuario, del mas nuevo al mas viejo
          ?search=palabra   -> posts que contengan esa palabra
          ?hashtag=tech     -> posts con ese hashtag
          (sin parametros)  -> los ultimos 50 posts
        """
        email_param   = req.get_param("user_id")
        search_param  = req.get_param("search")
        hashtag_param = req.get_param("hashtag")

        pipeline = []

        if email_param:
            user = find_user_by_email(self.db, email_param)
            pipeline += [
                # 1. filtro solo los posts de ese usuario
                {"$match": {"user_id": user["_id"]}},
                # 2. ordeno del mas nuevo al mas viejo
                {"$sort": {"created_at": -1}},
                # 3. agrego un campo que cuenta cuantos hashtags tiene cada post
                {"$addFields": {
                    "num_hashtags": {"$size": {"$ifNull": ["$hashtags", []]}}
                }},
                # 4. agrupo para sacar estadisticas generales del usuario
                #    - total de posts
                #    - total de hashtags usados en todos sus posts
                #    - lista de posts ordenada
                {"$group": {
                    "_id": "$user_id",
                    "total_posts": {"$sum": 1},
                    "total_hashtags": {"$sum": "$num_hashtags"},
                    "posts": {"$push": {
                        "_id": "$_id",
                        "content": "$content",
                        "image": "$image",
                        "hashtags": "$hashtags",
                        "created_at": "$created_at",
                        "num_hashtags": "$num_hashtags"
                    }}
                }}
            ]

        elif search_param:
            # usa el indice de texto que cree en connect.py
            pipeline += [
                # 1. filtro posts que contengan la palabra buscada
                #    $meta: "textScore" calcula que tan relevante es cada resultado
                {"$match": {"$text": {"$search": search_param}}},
                # 2. agrego el score de relevancia como campo visible
                {"$addFields": {
                    "relevancia": {"$meta": "textScore"}
                }},
                # 3. ordeno por relevancia (el mas relevante primero)
                {"$sort": {"relevancia": -1}},
                # 4. agrupo por usuario para ver quien escribe mas sobre ese tema
                {"$group": {
                    "_id": "$user_id",
                    "total_posts": {"$sum": 1},
                    "relevancia_promedio": {"$avg": "$relevancia"},
                    "posts": {"$push": {
                        "_id": "$_id",
                        "content": "$content",
                        "hashtags": "$hashtags",
                        "created_at": "$created_at",
                        "relevancia": "$relevancia"
                    }}
                }},
                # 5. ordeno los grupos por relevancia promedio
                {"$sort": {"relevancia_promedio": -1}}
            ]

        elif hashtag_param:
            pipeline += [
                {"$match": {"hashtags": hashtag_param.strip()}},
                {"$sort": {"created_at": -1}}
            ]

        else:
            # sin filtros: devuelvo los 50 mas recientes
            pipeline += [
                {"$sort": {"created_at": -1}},
                {"$limit": 50}
            ]

        if email_param or search_param:
            # estos pipelines agrupan por usuario, la respuesta tiene otra forma
            results = []
            for group in self.db.posts.aggregate(pipeline):
                group["_id"] = str(group["_id"])
                # serializo cada post dentro del grupo
                for post in group.get("posts", []):
                    post["_id"] = str(post["_id"])
                    post["created_at"] = post["created_at"].isoformat()
                if "relevancia_promedio" in group:
                    group["relevancia_promedio"] = round(group["relevancia_promedio"], 4)
                results.append(group)
            resp.media = results
        else:
            posts = [serialize_post(p) for p in self.db.posts.aggregate(pipeline)]
            resp.media = posts
        resp.status = falcon.HTTP_200


class TrendingHashtagsResource:
    """maneja GET /api/trends -> top 10 hashtags mas usados"""

    def __init__(self, db):
        self.db = db

    async def on_get(self, req, resp):
        # pipeline de agregacion:
        # 1. separo cada hashtag en su propio documento  ($unwind)
        # 2. cuento cuantas veces aparece cada uno       ($group)
        # 3. ordeno de mayor a menor                     ($sort)
        # 4. me quedo solo con los 10 primeros           ($limit)
        pipeline = [
            {"$unwind": "$hashtags"},
            {"$group": {"_id": "$hashtags", "total": {"$sum": 1}}},
            {"$sort": {"total": -1}},
            {"$limit": 10}
        ]

        trends = [{"hashtag": item["_id"], "count": item["total"]}
                  for item in self.db.posts.aggregate(pipeline)]

        resp.media = trends
        resp.status = falcon.HTTP_200

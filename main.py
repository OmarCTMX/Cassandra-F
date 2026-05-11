import logging
import sys
import os

# agrego la carpeta Mongo al path para poder importar resources
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Mongo"))

from falcon.asgi import App
from connect import get_db
from resources import (
    UsersResource,
    UserResource,
    PostsResource,
    TrendingHashtagsResource,
    UserPreferencesResource,
    UserPrivacyResource,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# me conecto a la base de datos
db = get_db()

# creo la app
app = App()

# creo los recursos
users_resource = UsersResource(db)
user_resource = UserResource(db)
posts_resource = PostsResource(db)
trending_resource = TrendingHashtagsResource(db)
preferences_resource = UserPreferencesResource(db)
privacy_resource = UserPrivacyResource(db)

# rutas de la api
app.add_route("/api/users", users_resource)                      # registrar usuario
app.add_route("/api/users/{email}", user_resource)                # actualizar perfil
app.add_route("/api/users/{email}/preferences", preferences_resource)  # preferencias
app.add_route("/api/users/{email}/privacy", privacy_resource)     # privacidad
app.add_route("/api/posts", posts_resource)                      # crear y ver posts
app.add_route("/api/trends", trending_resource)                  # ver tendencias

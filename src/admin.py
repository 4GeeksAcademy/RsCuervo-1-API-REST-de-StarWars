import os
from flask_admin import Admin
from models import db, User, Peoples, FavoritePeoples, Planets, FavoritePlanets, Starships, FavoriteStarships
from flask_admin.contrib.sqla import ModelView


# ------------------------------------

class FavoritePeoplesModelView(ModelView):
    column_auto_select_related = True  # Carga automáticamente las relaciones
    # Columnas y relationships de mi tabla
    column_list = ['id', 'user', 'peoples', 'peoples_id', 'user_id']


class PeoplesModelView(ModelView):
    column_auto_select_related = True  # Carga automáticamente las relaciones
    # Columnas y relationships de mi tabla
    column_list = ['id', 'name', 'comment_text']

# ------------------------------


class FavoritePlanetsModelView(ModelView):
    column_auto_select_related = True  # Carga automáticamente las relaciones
    # Columnas y relationships de mi tabla
    column_list = ['id', 'user', 'planets', 'user_id', 'planets_id']


class PlanetsModelView(ModelView):
    column_auto_select_related = True  # Carga automáticamente las relaciones
    # Columnas y relationships de mi tabla
    column_list = ['id', 'name', 'comment_text']

# ------------------------------


class FavoriteStarshipsModelView(ModelView):
    column_auto_select_related = True  # Carga automáticamente las relaciones
    # Columnas y relationships de mi tabla
    column_list = ['id', 'user', 'starships', 'user_id', 'starships_id']


class StarshipsModelView(ModelView):
    column_auto_select_related = True  # Carga automáticamente las relaciones
    # Columnas y relationships de mi tabla
    column_list = ['id', 'name', 'comment_text']

# ---------------------------------


class UserModelView(ModelView):
    column_auto_select_related = True
    # Columnas y relationships de mi tabla
    column_list = ['id', 'email', 'password', 'favorites_peoples',
                   'favorites_planets', 'favorites_starships', 'is_active']

# --------------------------------


def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')

    # Add your models here, for example this is how we add a the User model to the admin
   
    admin.add_view(UserModelView(User, db.session))
    admin.add_view(PeoplesModelView(Peoples, db.session))
    admin.add_view(FavoritePeoplesModelView(FavoritePeoples, db.session))
    admin.add_view(PlanetsModelView(Planets, db.session))
    admin.add_view(FavoritePlanetsModelView(FavoritePlanets, db.session))
    admin.add_view(StarshipsModelView(Starships, db.session))
    admin.add_view(FavoriteStarshipsModelView(FavoriteStarships, db.session))
    
    # You can duplicate that line to add mew models
    # admin.add_view(ModelView(YourModelName, db.session))

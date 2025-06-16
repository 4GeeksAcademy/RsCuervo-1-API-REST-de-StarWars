"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from sqlalchemy.orm import joinedload
from models import db, User, Peoples, FavoritePeoples, Planets, FavoritePlanets, Starships, FavoriteStarships
from sqlalchemy.exc import IntegrityError
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def handle_hello():
    users = User.query.options(
        joinedload(User.favorites_peoples),
        joinedload(User.favorites_planets),
        joinedload(User.favorites_starships)
    ).all()
    print(users)

    # users_serialized = []
    # for user in users:
    # users_serialized.append(user.serialize())
    # --------------------------------------
    users_serialized = list(map(lambda user: user.serialize(), users))
    # -------------------------------------
    response_body = {
        "msg": "Hello, this is your GET /user response ",
        "users": users_serialized
    }

    return jsonify(response_body), 200

# -----GET de todos los personajes---


@app.route('/peoples', methods=['GET'])
def get_peoples():
    peoples = Peoples.query.all()
    response = [person.serialize() for person in peoples]
    return jsonify(response), 200

# ---- GET de cada personaje por su id---


@app.route('/people/<int:people_id>', methods=['GET'])
def get_people_by_id(people_id):
    people = Peoples.query.get(people_id)
    if not people:
        return jsonify({'msg': 'Personaje no encontrado'}), 404
    return jsonify(people.serialize()), 200

# ----GET de Planetas----


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planets.query.all()
    response = [planet.serialize() for planet in planets]
    return jsonify(response), 200

# -----GET de un Planeta por su Id----


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({'msg': 'Planeta no encontrado'}), 404
    return jsonify(planet.serialize()), 200

# ----GET de Starships---


@app.route('/starships', methods=['GET'])
def get_starships():
    starships = Starships.query.all()
    response = [starship.serialize() for starship in starships]
    return jsonify(response), 200

# --- GET de Starship por su ID


@app.route('/starships/<int:starship_id>', methods=['GET'])
def get_starship_by_id(starship_id):
    starship = Starships.query.get(starship_id)
    if not starship:
        return jsonify({'msg': 'Nave no encontrada'}), 404
    return jsonify(starship.serialize()), 200

# ----GET de Todos los favoritos del usuario


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"msg": "User ID es requirido"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404
    favorites = {
        "favorites_peoples": [fav.serialize() for fav in user.favorites_peoples],
        "favorites_planets": [fav.serialize() for fav in user.favorites_planets],
        "favorites_starships": [fav.serialize() for fav in user.favorites_starships]
    }
    return jsonify(favorites), 200


@app.route('/favorite/<int:user_id>', methods=['GET'])
def get_favorites(user_id):
    user = User.query.options(joinedload(User.favorites_planets), joinedload(User.favorites_peoples), joinedload(User.favorites_starships)).get(user_id)
    
    if not user:
        return jsonify({'msg': 'Usuario no encontrado'}), 404

    return jsonify(user.serialize()), 200

# ----------[POST] anadir un planeta favorito


@app.route('/favorite/planets/<int:planets_id>', methods=['POST'])
def add_favorite_planet():
    body = request.get_json()
    user_id = body.get("user_id")
    planet_id = body.get("planet_id")

    if not user_id or not planet_id:
        return jsonify({'msg': 'El campo "user_id" y "planet_id" son obligatorios'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': 'Usuario no encontrado'}), 404
    
    existing_favorite_count = FavoritePlanets.query.filter_by(user_id=user.id, planet_id=planet_id).count()
    if existing_favorite_count > 0:
        return jsonify({'msg': 'Este planeta ya está en tus favoritos'}), 400
    
    new_favorite = FavoritePlanets(user_id=user.id, planet_id=planet_id)
    db.session.add(new_favorite)

    try:
        db.session.commit()
        return jsonify({'msg': 'Planeta agregado a favoritos'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error al agregar a favoritos: {str(e)}'}), 500

# --------[POST] anadir un personaje Favorito


@app.route('/favorite/peoples/<int:peoples_id>', methods=['POST'])
def add_favorite_people(peoples_id):
    body = request.get_json()
    user_id = body.get("user_id")

    if not user_id:
        return jsonify({'msg': 'El campo "user_id" es obligatorio'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': 'Usuario no encontrado'}), 404

    # Verificar si ya existe en favoritos
    existing_favorite = FavoritePeoples.query.filter_by(user_id=user_id, peoples_id=peoples_id).first()
    if existing_favorite:
        return jsonify({'msg': 'Este personaje ya está en favoritos'}), 400

    # Agregar nuevo favorito con manejo de errores
    new_favorite = FavoritePeoples(user_id=user_id, peoples_id=peoples_id)
    db.session.add(new_favorite)
    
    try:
        db.session.commit()
        return jsonify({'msg': 'Personaje añadido a favoritos exitosamente'}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'msg': 'Este personaje ya está en favoritos (integridad de datos)'}, 400)

# ------[POST] anadir una nave espacial favorita


@app.route('/favorite/starships/<int:starships_id>', methods=['POST'])
def add_favorite_starship(starships_id):
    body = request.get_json()
    user_id = body.get("user_id")
    if not user_id:
        return jsonify({'msg': 'El campo "user_id" es obligatorio'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': 'Usuario no encontrado'}), 404

    favorite = FavoriteStarships(user_id=user_id, starships_id=starships_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({'msg': 'Nave espacial añadida a favoritos exitosamente'}), 201

# ------[DELETE]


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    body = request.get_json()
    user_id = body.get("user_id")
    if not user_id:
        return jsonify({'msg': 'El campo "user_id" es obligatorio'}), 400

    favorite = FavoritePlanets.query.filter_by(
        user_id=user_id, planet_id=planet_id).first()
    if not favorite:
        return jsonify({'msg': 'Favorito no encontrado'}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({'msg': 'Planeta eliminado de favoritos exitosamente'}), 200


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    body = request.get_json()
    user_id = body.get("user_id")
    if not user_id:
        return jsonify({'msg': 'El campo "user_id" es obligatorio'}), 400

    favorite = FavoritePeoples.query.filter_by(
        user_id=user_id, peoples_id=people_id).first()
    if not favorite:
        return jsonify({'msg': 'Favorito no encontrado'}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({'msg': 'Personaje eliminado de favoritos exitosamente'}), 200


@app.route('/favorite/starship/<int:starship_id>', methods=['DELETE'])
def delete_favorite_starship(starship_id):
    body = request.get_json()
    user_id = body.get("user_id")
    if not user_id:
        return jsonify({'msg': 'El campo "user_id" es obligatorio'}), 400

    favorite = FavoriteStarships.query.filter_by(
        user_id=user_id, starships_id=starship_id).first()
    if not favorite:
        return jsonify({'msg': 'Favorito no encontrado'}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({'msg': 'Nave espacial eliminada de favoritos exitosamente'}), 200

# -------------------------------


@app.route('/user', methods=['POST'])
def create_user():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'Debes enviar informacion en el body'})
    if 'email' not in body:
        return jsonify({'msg': 'El campo "email" es obligatorio'}), 400
    if 'password' not in body:
        return jsonify({'msg': 'El campo "password" es obligatorio'}), 400

    new_user = User(email=body['email'], password=body['password'], is_active=True)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'msg': 'ok'})


'''
@app.route('/get-favorites', methods=['GET'])
def get_favorites():
    user = User.query.get()
    print(user.favorite_peoples)
    print(user.favorite_planets)
    print(user.favorite_starships)
    return jsonify({'msg': 'ok'})
'''


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

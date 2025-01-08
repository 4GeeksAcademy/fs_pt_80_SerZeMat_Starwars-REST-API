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
from models import db, Users, Planets, Favorites, People
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
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

#@app.route('/user', methods=['GET'])
#def handle_hello():
#
#    response_body = {
#        "msg": "Hello, this is your GET /user response "
#    }
#
#     return jsonify(response_body), 200


# Devolvemos todos los usuarios del Blog SW de la DB
@app.route('/users', methods=['GET'])
def get_users():
    users = Users.query.all()
    return jsonify([user.serialize() for user in users]), 200

# Mostramos todos los favoritos que pertenecen al usuario actual
@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = 1  # Simulación de usuario actual
    favorites = Favorites.query.filter_by(user_id=user_id).all()
    return jsonify([favorite.serialize() for favorite in favorites])

# Devolvemos todas la personas del Blog SW de la DB
@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    return jsonify([person.serialize() for person in people]), 200

# Mostramos la información de un solo personaje según su id
@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    try:
        data = People.query.get(people_id)
        if data is None:
            raise Exception("Person not found")
        return jsonify(data.serialize())
    except Exception as e:
        return jsonify({'error': str(e)}), 404

#Devolvemos todos los planetas del Blog SW de la DB
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planets.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

# Mostramos la información de un solo planeta según su id
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    try:
        data = Planets.query.get(planet_id)
        if data is None:
            raise Exception("Planet not found")
        return jsonify(data.serialize())
    except Exception as e:
        return jsonify({'error': str(e)}), 404

# Añadimos un nuevo planet favorito al usuario actual con el id = planet_id.
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    try:
        data = request.json
        if not data or 'user_id' not in data:
            raise Exception("Data missing: 'user_id' is required")

        favorite = Favorites(
            user_id = data['user_id'],
            planet_id = planet_id
            )
        db.session.add(favorite)
        db.session.commit()
        return jsonify(favorite.serialize()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Añadimos un nuevo persoanje favorito al usuario actual con el id = people_id.
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_person(people_id):
    try:
        data = request.json
        if not data or 'user_id' not in data:
            raise Exception("Data missing: 'user_id' is required")

        favorite = Favorites(
            user_id = data['user_id'],
            people_id = people_id
            )
        db.session.add(favorite)
        db.session.commit()
        return jsonify(favorite.serialize()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Eliminamos un planet favorito con el id = planet_id.
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    try:
        data = request.json

        # Data validation
        if not data or 'user_id' not in data:
            raise Exception("Missing data: 'user_id' is required")

        favorite = Favorites.query.filter_by(user_id=data['user_id'], planet_id=planet_id).first()
        if favorite is None:
            raise Exception("Favorite planet not found with the provided ID")

        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'msg': 'Favorite successfully deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404

# Eliminamos un personaje favorito con el id = people_id.
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_person(people_id):
    try:
        data = request.json

        # Data validation
        if not data or 'user_id' not in data:
            raise Exception("Missing data: 'user_id' is required")

        favorite = Favorites.query.filter_by(user_id=data['user_id'], people_id=people_id).first()
        if favorite is None:
            raise Exception("Favorite person not found with the provided ID")

        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'msg': 'Favorite successfully deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

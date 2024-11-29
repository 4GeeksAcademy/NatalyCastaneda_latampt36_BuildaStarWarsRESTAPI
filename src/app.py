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
from models import db, User, Planets, People, Favorites
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


def get_all_users():
    users = User.query.all()
    return [user.serialize() for user in users]


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['POST'])
def sign_up():
    data = request.json
    user_name = data.get("user_name")
    email = data.get("email")
    password = data.get("password")

    if None in [user_name, email, password]:
        return jsonify({
            "message": "user_name, email and password are required"
        }), 400

    try:

        new_user = User(user_name=user_name, email=email, password=password)

        db.session.add(new_user)
        db.session.commit()

        return jsonify(new_user.serialize()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500


@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify({
        'id': user.id,
        'user_name': user.user_name,
        'email': user.email
    })


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'user_name': user.user_name,
        'email': user.email
    } for user in users])


@app.route('/people', methods=['POST'])
def add_person():
    data = request.json
    name = data.get('name')
    gender = data.get('gender')
    height = data.get('height')
    hair_color = data.get('hair_color')
    skin_color = data.get('skin_color')
    homeworld_id = data.get('homeworld_id')

    if not all([name, gender, height, hair_color, skin_color]):
        return jsonify({"message": "All fields are required"}), 400

    if homeworld_id and not Planets.query.get(homeworld_id):
        return jsonify({"message": "Homeworld not found"}), 404

    new_person = People(
        name=name,
        gender=gender,
        height=height,
        hair_color=hair_color,
        skin_color=skin_color,
        homeworld_id=homeworld_id
    )
    db.session.add(new_person)
    db.session.commit()
    return jsonify(new_person.serialize()), 201


@app.route('/people', methods=['GET'])
def get_all_people():
    people = People.query.all()
    return jsonify([person.serialize() for person in people])


@app.route('/people/<int:person_id>', methods=['PUT'])
def update_person(person_id):
    data = request.json
    person = People.query.get(person_id)
    if not person:
        return jsonify({"message": "Person not found"}), 404

    person.name = data.get('name', person.name)
    person.gender = data.get('gender', person.gender)
    person.height = data.get('height', person.height)
    person.hair_color = data.get('hair_color', person.hair_color)
    person.skin_color = data.get('skin_color', person.skin_color)
    person.homeworld_id = data.get('homeworld_id', person.homeworld_id)

    db.session.commit()
    return jsonify(person.serialize()), 200


@app.route('/people/<int:person_id>', methods=['DELETE'])
def delete_person(person_id):
    person = People.query.get(person_id)
    if not person:
        return jsonify({"message": "Person not found"}), 404

    db.session.delete(person)
    db.session.commit()
    return jsonify({"message": "Person deleted successfully"}), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get(people_id)
    if not person:
        return jsonify({"message": "Person not found"}), 404
    return jsonify(person.serialize())


@app.route('/planets', methods=['POST'])
def add_planet():
    data = request.json
    name = data.get('name')
    terrain = data.get('terrain')
    climate = data.get('climate')
    population = data.get('population')

    if not all([name, terrain, climate, population]):
        return jsonify({"message": "All fields are required"}), 400

    new_planet = Planets(
        name=name,
        terrain=terrain,
        climate=climate,
        population=population
    )
    db.session.add(new_planet)
    db.session.commit()
    return jsonify(new_planet.serialize()), 201


@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planets.query.all()
    return jsonify([planet.serialize() for planet in planets])


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({"message": "Planet not found"}), 404
    return jsonify(planet.serialize())


@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    data = request.json
    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({"message": "Planet not found"}), 404

    try:
        planet.name = data.get('name', planet.name)
        planet.terrain = data.get('terrain', planet.terrain)
        planet.climate = data.get('climate', planet.climate)
        planet.population = data.get('population', planet.population)

        db.session.commit()
        return jsonify(planet.serialize()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500


@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({"message": "Planet not found"}), 404

    db.session.delete(planet)
    db.session.commit()
    return jsonify({"message": "Planet deleted successfully"}), 200


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = request.headers.get("User-ID")
    if not user_id:
        return jsonify({"message": "User ID is required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify([favorite.serialize() for favorite in user.favorites])


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    try:
        user_id = request.headers.get("User-ID")
        if not user_id:
            return jsonify({"message": "User ID is required"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        planet = Planets.query.get(planet_id)
        if not planet:
            return jsonify({"message": "Planet not found"}), 404

        new_favorite = Favorites(
            user_id=user.id, type="planets", reference_id=planet.id)
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({"message": "Favorite added successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    user_id = request.headers.get("User-ID")
    if not user_id:
        return jsonify({"message": "User ID is required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    person = People.query.get(people_id)
    if not person:
        return jsonify({"message": "Person not found"}), 404

    new_favorite = Favorites(
        user_id=user.id, type="people", reference_id=person.id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"message": "Favorite added successfully"}), 201


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = request.headers.get("User-ID")
    if not user_id:
        return jsonify({"message": "User ID is required"}), 400

    favorite = Favorites.query.filter_by(
        user_id=user_id, type="planets", reference_id=planet_id).first()
    if not favorite:
        return jsonify({"message": "Favorite not found"}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": "Favorite deleted successfully"}), 200


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    user_id = request.headers.get("User-ID")
    if not user_id:
        return jsonify({"message": "User ID is required"}), 400

    favorite = Favorites.query.filter_by(
        user_id=user_id, type="people", reference_id=people_id).first()
    if not favorite:
        return jsonify({"message": "Favorite not found"}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": "Favorite deleted successfully"}), 200


    # this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

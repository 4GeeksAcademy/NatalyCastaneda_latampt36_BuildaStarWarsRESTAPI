from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import foreign
from sqlalchemy import Enum

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    is_active = db.Column(db.Boolean(), nullable=False)

    favorites = db.relationship('Favorites', back_populates='user')

    def __init__(self, user_name, email, password):
        self.user_name = user_name
        self.email = email
        self.password = password
        self.is_active = True

    def __repr__(self):
        return '<User %r>' % self.user_name

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
        }


class Planets(db.Model):
    __tablename__ = 'planets'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), unique=False, nullable=False)
    terrain = db.Column(db.String(120), unique=False, nullable=False)
    climate = db.Column(db.String(120), unique=False, nullable=False)
    population = db.Column(db.Integer, unique=False, nullable=False)

    residents = db.relationship('People', back_populates='planet')
    favorites = db.relationship(
        'Favorites',
        primaryjoin="and_(foreign(Favorites.reference_id) == Planets.id, Favorites.type == 'planets')",
        viewonly=True
    )

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "terrain": self.terrain,
            "climate": self.climate,
            "population": self.population,
            "residents": [resident.serialize() for resident in self.residents],
        }


class People(db.Model):
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    gender = db.Column(Enum('male', 'female', 'n/a',
                       name="gender_enum"), nullable=False)
    height = db.Column(db.Integer, unique=False, nullable=False)
    hair_color = db.Column(db.String(120), nullable=False)
    skin_color = db.Column(db.String(120), nullable=False)
    homeworld_id = db.Column(db.Integer, db.ForeignKey('planets.id'))

    planet = db.relationship('Planets', back_populates='residents')
    favorites = db.relationship(
        'Favorites',
        primaryjoin="and_(foreign(Favorites.reference_id) == People.id, Favorites.type == 'people')",
        viewonly=True
    )

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "height": self.height,
            "hair_color": self.hair_color,
            "skin_color": self.skin_color,
            "homeworld": self.planet.serialize() if self.planet else None,
        }


class Favorites(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(
        Enum('planets', 'people', name="type_enum"), nullable=False)
    reference_id = db.Column(db.Integer, nullable=False)
    user = db.relationship('User', back_populates='favorites')

    planet = db.relationship(
        'Planets',
        primaryjoin="and_(foreign(Favorites.reference_id) == Planets.id, Favorites.type == 'planets')",
        back_populates="favorites",
        viewonly=True
    )

    people = db.relationship(
        'People',
        primaryjoin="and_(foreign(Favorites.reference_id) == People.id, Favorites.type == 'people')",
        back_populates="favorites",
        viewonly=True
    )

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type,
            "reference_id": self.reference_id
            }
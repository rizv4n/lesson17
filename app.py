# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Str()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


movie_schema = MovieSchema()
director_schema = DirectorSchema()
genre_schema = GenreSchema()

movies_schema = MovieSchema(many=True)

api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('director')
genre_ns = api.namespace('genre')


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        if request.args.get(key='director_id') and request.args.get(key='genre_id') is not None:
            did = request.args.get(key='director_id')
            gid = request.args.get(key='genre_id')
            movie = db.session.query(Movie).filter(Movie.director_id == did, Movie.genre_id == gid).all()
            return movies_schema.dump(movie), 200
        elif request.args.get(key='director_id') is not None:
            did = request.args.get(key='director_id')
            movie = db.session.query(Movie).filter(Movie.director_id == did).all()
            return movies_schema.dump(movie), 200
        elif request.args.get(key='genre_id') is not None:
            gid = request.args.get(key='genre_id')
            movie = db.session.query(Movie).filter(Movie.genre_id == gid).all()
            return movies_schema.dump(movie), 200
        else:
            movies = db.session.query(Movie).all()
            return movies_schema.dump(movies), 200


@movie_ns.route('/<int:mid>')
class MoviesView(Resource):
    def get(self, mid: int):
        try:
            movie = db.session.query(Movie).filter(Movie.id == mid).one()
            return movie_schema.dump(movie), 200
        except Exception as e:
            return str(e), 404


@director_ns.route('/')
class DirectorView(Resource):
    def post(self):
        req_json = request.json
        new_director = Director(**req_json)
        with db.session.begin():
            db.session.add(new_director)
        return "", 201


@director_ns.route('/<int:did>')
class DirectorView(Resource):
    def put(self, did):
        director = db.session.query(Director).get(did)
        req_json = request.json

        director.name = req_json.get("name")

        db.session.add(director)
        db.session.commit()

        return "", 204

    def delete(self, did):
        director = db.session.query(Director).get(did)

        db.session.delete(director)
        db.session.commit()

        return "", 204


@genre_ns.route('/')
class GenreView(Resource):
    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)
        with db.session.begin():
            db.session.add(new_genre)
        return "", 201


@genre_ns.route('/<int:did>')
class GenreView(Resource):
    def put(self, gid):
        genre = db.session.query(Genre).get(gid)
        req_json = request.json

        genre.name = req_json.get("name")

        db.session.add(genre)
        db.session.commit()

        return "", 204

    def delete(self, did):
        genre = db.session.query(Genre).get(did)

        db.session.delete(genre)
        db.session.commit()

        return "", 204


if __name__ == '__main__':
    app.run(debug=True)

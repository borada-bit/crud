from email import header
import mimetypes
from wsgiref import headers
from xxlimited import new
from flask import Flask, request, jsonify, json, Response
import jsonschema
from jsonschema import validate
import random
import pymongo.errors
from pymongo import MongoClient
from bson import json_util

app = Flask(__name__)

client = MongoClient("mongodb://mongo:27017")
client.drop_database('movie_database')
db = client.movie_database
db.create_collection('movie_collection', validator={
    '$jsonSchema': {
            'bsonType': 'object',
            'additionalProperties': True,
            'required': ['title', 'year', 'genre', 'director', 'runtime'],
            'properties': {
                'title': {
                    'bsonType': 'string'
                },
                'director': {
                    'bsonType': 'string',
                    'description': 'Set to default value'
                },
                'genre': {
                    'bsonType': 'string'
                },
                'year': {
                    'bsonType': 'int',
                    'minimum': 1920,
                    'maximum': 2022
                },
                'runtime': {
                    'bsonType': 'int',
                    'minimum': 1,
                    'maximum': 500,
                    'description': "must be an integer in [ 2017, 3017 ] and is required"
                },
                'comment': {
                    'bsonType': [ "string" ],
                    'description': 'must be a string if the field exists'
                }
            }
        }
    })


data_1 = {
    "id": 1,
    "title": "Dune",
    "year": 2021,
    "genre": "sci-fi",
    "director": "Dennis Villenueve",
    "runtime": 150,
    "comment": ""
        }

data_2 = {
    "id": 2,
    "title": "Batman",
    "year": 2022,
    "genre": "action",
    "director": "Matt Reeves",
    "runtime": 176,
    "comment": ""
        }

data_3 = {
    "id": 3,
    "title": "Forrest Gump",
    "year": 1994,
    "genre": "drama",
    "director": "Robert Zemeckis",
    "runtime": 144,
    "comment": ""
        }

data_4 = {
    "id": 4,
    "title": "Inception",
    "year": 2010,
    "genre": "action",
    "director": "Christopher Nolan",
    "runtime": 148,
    "comment": ""
        }


data_5 = {
    "id": 5,
    "title": "Joker",
    "year": 2019,
    "genre": "crime",
    "director": "Todd Phillips",
    "runtime": 122,
    "comment": ""
        }

data_6 = {
    "title": "Joker",
    "year": 2019,
    "director": "Todd Phillips",
    "runtime": 122,
        }


def add_to_coll(coll, data):
    try:
        coll.insert_one(data)
    except pymongo.errors.WriteError as e:
        print('Error inserting. Wrong schema')


@app.route('/')
def hello():
    return ('Hello!')


@app.route('/movies/', methods=['GET'])
def get_movie():
    movies = list(db.movie_collection.find({}, {'_id': 0}))
    return Response(json_util.dumps(movies), status=200, mimetype='application/json')


@app.route('/movies/<int:movie_id>', methods=['GET'])
def get_all_movies(movie_id):
    movie = db.movie_collection.find_one({'id': movie_id}, {'_id': 0}) 
    if movie is None:
        return Response(json.dumps({'Error': 'No such id exists'}),status=404, mimetype="application/json")
    # 200 OK
    return Response(json_util.dumps(movie), status=200, mimetype="application/json")


# Content-location /api/movies/80
# kazkas tokio
# pakeist visur responsus i tinkama locationa
@app.route('/movies/', methods=['POST'])
def create_movie():
    movie_data = json.loads(request.data)
    ## validating json
    try:
        validate(instance=movie_data, schema=schema)
    except jsonschema.exceptions.ValidationError as e:
        # 422 UNPROCESSABLE ENTITY
        return Response(json.dumps({'Error': 'Wrong schema'}), status=422, mimetype="application/json")
    
    ## assign random 
    while True:
        generated_id = random.randint(0, 1000)
        movie_data['id'] = generated_id

        all_movies = list(db.movie_collection.find({}))
        for obj in all_movies:
            if movie_data['id'] == obj['id']:
                continue
        break
             
    ## ALL CHECKS HAVE PASSED
    db.movie_collection.insert_one(movie_data)
    # 201 CREATED
    resp = Response(json_util.dumps(movie_data), status=201, mimetype="application/json")
    resp.headers['Content-Location'] = "/movies/"+str(movie_data['id'])
    return resp


# 200 status code netinka paupdatinus
@app.route('/movies/<int:movie_id>', methods=['PUT'])
def update_movie(movie_id):
    # CHECK IF JSON IS OF GOOD FORMAT
    new_movie_data = json.loads(request.data)
    try:
        validate(instance=new_movie_data, schema=schema)
    except jsonschema.exceptions.ValidationError as e:
        return Response(json.dumps({'Error': 'Wrong schema'}), status=422, mimetype="application/json")

    # GET OLD MOVIE DATA
    old_movie_data = list(db.movie_collection.find({'id':movie_id}, {'_id': 0}))
    
    # UPDATING
    query_filter = {'id': movie_id}
    query_values = {'$set': new_movie_data}
    # return json.dumps(str(query_filter) + str(new_movie_data))
    db.movie_collection.update_one(query_filter, query_values)

    # 200 OK
    resp = Response(json.dumps(str('old movie data ') + str(old_movie_data)+str('    new movie data ') + str(new_movie_data)), status=200, mimetype="application/json")
    resp.headers['Content-Location'] = "/movies/"+str(movie_id)
    return resp


# paduodi objekta kuriame yra laukai kurios reikia keisti
@app.route('/movies/<int:movie_id>', methods=['PATCH'])
def patch_movie(movie_id):
    new_movie_data = json.loads(request.data)
    
    cursor = db.movie_collection.find_one({'id': movie_id})

    if cursor is None:
        return Response(json.dumps({'Error': 'No such id exists'}),status=404, mimetype="application/json")
    else:
        try:
            validate(instance=new_movie_data, schema=schema)
        except jsonschema.exceptions.ValidationError as e:
            return Response(json.dumps({'Error': 'Wrong schema'}), status=422, mimetype="application/json")

        old_movie_data = list(cursor)

        query_filter = {'id': movie_id}
        query_values = {'$set': new_movie_data}
        db.movie_collection.update_one(query_filter, query_values)

        # 200 OK
        resp = Response(json.dumps(str('old movie data ') + str(old_movie_data)+str('    new movie data ') + str(new_movie_data)), status=200, mimetype="application/json")
        resp.headers['Content-Location'] = "/movies/"+str(movie_id)
        return resp


# IDEMPOTENT
@app.route('/movies/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    cursor = db.movie_collection.find_one({'id':movie_id}, {'_id':0}) 
    if cursor is None:
        # 404 NOT FOUND
        return Response(json.dumps({'Error': 'No such id exists'}),status=404, mimetype="application/json")
    else: 
        movie_data = cursor.copy()
        db.movie_collection.delete_one({'id':movie_id})
        # 200 OK
        return Response(json_util.dumps(movie_data),status=200, mimetype="application/json")
    



if __name__=='__main__':
    add_to_coll(db.movie_collection, data_1)
    add_to_coll(db.movie_collection, data_2)
    add_to_coll(db.movie_collection, data_3)
    add_to_coll(db.movie_collection, data_4)
    add_to_coll(db.movie_collection, data_5)
    add_to_coll(db.movie_collection, data_6)
    app.run(host="0.0.0.0", debug = True, port=80)
 

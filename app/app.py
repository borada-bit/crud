from cgitb import text
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

db = client.movie_database
db.movie_collection


schema = {
    "type": "object",
    "properties":{
        "id": {
            "type": "integer"
        },
        "title": {
            "type": "string"
            },
        "year": {
            "type": "integer",
            "maximum": 2022
            },   
        "genre": {
            "type": "string"
            },
        "director": {
            "type": "string"
            },
        "runtime": {
            "type": "integer"
            },
        "comment": {
            "type": "string"
        }
        },
    "required":[
        "title",
        "year",
        "genre",
        "director",
        "runtime"
        ]
    }


# dictlist = [data_1, data_2, data_3, data_4, data_5]
# {'id': 1, 'title': 'Dune', 'year': 2021, 'genre': 'sci-fi', 'director': 'Dennis Villenueve', 'runtime': 150, 'comment': '', '_id': ObjectId('624bf126ef9ed9e0ec5c0436')}
# print(dictlist[0])

#db.my_collection.insert_one(data_1)
#db.my_collection.insert_one(data_2).inserted_id
#db.my_collection.insert_one(data_3).inserted_id
#db.my_collection.insert_one(data_4).inserted_id
#db.my_collection.insert_one(data_5).inserted_id



@app.route('/')
def hello():
    return ('Hello!')


@app.route('/movies/', methods=['GET'])
def get_movie():
    # buvo tiesiog jsonify(dictlist)
    movies = list(db.movie_collection.find({}, ))
    return Response(json_util.dumps(movies), status=200, mimetype='application/json')
    return jsonify(dictlist)


@app.route('/movies/<int:movie_id>', methods=['GET'])
def get_all_movies(movie_id):
    if movie_id == 50:
        movies = db.my_collection.find_one()
        print(movies)
        return Response(json_util.dumps(movies),status=200, mimetype="application/json")
    for i in dictlist:
        if i['id'] == movie_id:
            # 200 OK
            return i
            # return Response(json.dumps(i), status=200, mimetype="application/json")
    return Response(json.dumps({'Error': 'No such id exists'}),status=404, mimetype="application/json")


@app.route('/movies/', methods=['POST'])
def create_movie():
    movie_data = json.loads(request.data)
    ## validating json
    try:
        validate(instance=movie_data, schema=schema)
    except jsonschema.exceptions.ValidationError as e:
        # 422 UNPROCESSABLE ENTITY
        return Response(json.dumps({'Error': 'Wrong schema'}), status=422, mimetype="application/json")
    
    ## check if json has id attached to it and assign random if not
    if 'id' not in movie_data:
        while True:
            generated_id = random.randint(0, 1000)
            movie_data['id'] = generated_id

            for obj in dictlist:
                if movie_data['id'] == obj['id']:
                    continue
            break
    else:
        for obj in dictlist:
            if movie_data['id'] == obj['id']:
                # 422 UNPROCESSABLE ENTITY
                temp_id = movie_data['id']
                return Response(json.dumps({'Error': str(temp_id) + ' id already exists'}), status=422, mimetype="application/json")
             
    # ALL CHECKS HAVE PASSED
    dictlist.append(movie_data)
    # 201 CREATED
    resp = Response(json.dumps(movie_data), status=201, mimetype="application/json")
    resp.headers['Location'] = "http://localhost:80/movies/"+str(movie_data['id'])
    return resp
    # return Response(json.dumps(movie_data), status=201, mimetype="application/json")


@app.route('/movies/<int:movie_id>', methods=['PUT'])
def update_movie(movie_id):
    # CHECK IF JSON IS OF GOOD FORMAT
    new_movie_data = json.loads(request.data)
    try:
        validate(instance=new_movie_data, schema=schema)
    except jsonschema.exceptions.ValidationError as e:
        return Response(json.dumps({'Error': 'Wrong schema'}), status=422, mimetype="application/json")

    #CHECK IF ID EXISTS and CHANGE IT
    old_movie_data = ""
    index_in_list = 0
    for i in range(len(dictlist)):
        if dictlist[i]['id'] == movie_id:
            old_movie_data = dictlist[i]
            index_in_list = i
    
    # 200 OK
    dictlist[index_in_list] = new_movie_data
    dictlist[index_in_list]['id'] = movie_id
    resp = Response(json.dumps(str(old_movie_data)+str(new_movie_data)), status=200, mimetype="application/json")
    resp.headers['Location'] = "http://localhost:80/movies/"+str(movie_id)
    return resp


# ka keicia i ka
@app.route('/movies/<int:movie_id>', methods=['PATCH'])
def patch_movie(movie_id):
    for i in range(len(dictlist)):
        if dictlist[i]['id'] == movie_id:
            new_movie_data = json.loads(request.data)
            new_keys = list(new_movie_data.keys())
            old_movie_data = dictlist[i].copy()
            for j in range(len(new_keys)):
                dictlist[i][new_keys[j]] = new_movie_data[new_keys[j]]
            ##CHECKING IF PATCHED DICT IS GOOD FORMAT
            try:
                validate(instance=dictlist[i], schema=schema)
            except jsonschema.exceptions.ValidationError as e:
                dictlist[i] = old_movie_data
                return Response(json.dumps({'Error': 'Wrong schema'}), status=422, mimetype="application/json")

            resp = Response(json.dumps(str(old_movie_data)+str(" CHANGED TO ")+str(dictlist[i])),status=404, mimetype="application/json")
            resp.headers['Location'] = "http://localhost:80/movies/"+str(movie_id)
            return resp
        else:
            return Response(json.dumps({'Error': 'No such id exists'}),status=404, mimetype="application/json")


# IDEMPOTENTAS jeigu istrini id 1 kiti nepasistumia
@app.route('/movies/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    for i in range(len(dictlist)):
        if dictlist[i]['id'] == movie_id:
            movie = dictlist[i]
            del dictlist[i]
            return Response(json.dumps(movie),status=200, mimetype="application/json")
    
    # 404 NOT FOUND
    return Response(json.dumps({'Error': 'No such id exists'}),status=404, mimetype="application/json")


def add_to_coll(coll, data):
    try:
        coll.insert_one(data)
    except pymongo.errors.DuplicateKeyError:
        print('Error inserting. This id already exist')


if __name__=='__main__':
    app.run(host="0.0.0.0", debug = True, port=80)

    # Add movie
 #   collection = db_movies.movie
  #  temp_data = {
   #     '_id': 6,
    #    'title': "Inception",
     #   'year': 2010,
      #  'genre': 'sci-fi',
       # 'reviews': []
    #}
    #add_to_coll(collection, temp_data)
	

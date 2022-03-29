from flask import Flask, request, jsonify, json
from flask import Response
import jsonschema
from jsonschema import validate

app = Flask(__name__)

schema = {
    "type": "object",
    "properties":{
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


data_1 = {
    "title": "Dune",
    "year": 2021,
    "genre": "sci-fi",
    "director": "Dennis Villenueve",
    "runtime": 150
        }

data_2 = {
    "title": "Batman",
    "year": 2022,
    "genre": "action",
    "director": "Matt Reeves",
    "runtime": 176
        }

data_3 = {
    "title": "Forrest Gump",
    "year": 1994,
    "genre": "drama",
    "director": "Robert Zemeckis",
    "runtime": 144
        }

data_4 = {
    "title": "Inception",
    "year": 2010,
    "genre": "action",
    "director": "Christopher Nolan",
    "runtime": 148
        }


data_5 = {
    "title": "Joker",
    "year": 2019,
    "genre": "crime",
    "director": "Todd Phillips",
    "runtime": 122
        }


dictlist = [data_1, data_2, data_3, data_4, data_5]


@app.route('/')
def hello():
    return (f'Hello!')


@app.route('/movies', methods=['GET'])
def read():
    return jsonify(dictlist)


@app.route('/movies/<int:movie_id>', methods=['GET'])
def get_all_movies(movie_id):
    try:
        dictlist[movie_id]
        return jsonify(dictlist[movie_id])
    except:
        return Response(json.dumps({'Error': 'No such id exists'}),status=404, mimetype="application/json")


@app.route('/movies', methods=['POST'])
def create():
    movie_data = json.loads(request.data)
    try:
        validate(instance=movie_data, schema=schema)
        dictlist.append(movie_data)
        return jsonify(movie_data)
    except jsonschema.exceptions.ValidationError as e:
        return Response(jsonify(movie_data), status=422, mimetype="application/json")


@app.route('/movies/<int:movie_id>', methods=['PUT'])
def update_movie(movie_id):
    try:
        dictlist[movie_id]
        movie_data = json.loads(request.data)
        dictlist[movie_id] = movie_data
        return jsonify(movie_data)
    except:
        return Response(json.dumps({'Error': 'No such id exists'}),status=404, mimetype="application/json")


@app.route('/movies/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    try:
        dictlist[movie_id]
        movie = dictlist[movie_id]
        del dictlist[movie_id]
        return jsonify(movie)
    except:
        return Response(json.dumps({'Error': 'No such id exists'}),status=404, mimetype="application/json")


if __name__=='__main__':
    app.run(host="0.0.0.0", debug = True, port=80)
	

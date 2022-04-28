import py_compile
from flask import Flask, request, json, Response
from pymongo import MongoClient, errors
from bson import json_util
import my_data
import my_mongo
import random


### FLASK
app = Flask(__name__)


###  MONGO CLIENT
g_client = MongoClient("mongodb://mongo:27017")


# DATABASE NAME movie_database
g_database_name = "movie_database"
# COLLECTION NAME movie_collection
g_collection_name = "movie_collection"


# DROPS IF ALREADY EXISTS
g_client.drop_database("movie_database")
g_db = g_client[g_database_name]


### MONGO VALIDATOR BEFORE INSERTING
g_db.create_collection(
    g_collection_name,
    validator={
        "$jsonSchema": {
            "bsonType": "object",
            "additionalProperties": True,
            "required": ["title", "year", "genre", "director", "runtime"],
            "properties": {
                "title": {"bsonType": "string"},
                "director": {
                    "bsonType": "string",
                    "description": "Set to default value",
                },
                "genre": {"bsonType": "string"},
                "year": {"bsonType": "int", "minimum": 1920, "maximum": 2022},
                "runtime": {
                    "bsonType": "int",
                    "minimum": 1,
                    "maximum": 500,
                    "description": "must be an integer in [ 2017, 3017 ] and is required",
                },
                "comment": {
                    "bsonType": ["string"],
                    "description": "must be a string if the field exists",
                },
            },
        }
    },
)

g_collection = g_db[g_collection_name]


### REST/API METHODS BELOW
@app.route("/")
def index():
    return "Welcome!"


@app.route("/movies/", methods=["GET"])
def get_movie():
    movies = my_mongo.get_all_movies(g_collection)
    return Response(json.dumps(list(movies)), status=200, mimetype="application/json")


@app.route("/movies/<int:movie_id>", methods=["GET"])
def get_all_movies(movie_id):
    movie = my_mongo.get_movie(g_collection, movie_id)
    if movie is None:
        # 404 NOT FOUND
        return Response(
            json.dumps({"Error": "No such id exists"}),
            status=404,
            mimetype="application/json",
        )
    # 200 OK
    return Response(json_util.dumps(movie), status=200, mimetype="application/json")


@app.route("/movies/", methods=["POST"])
def create_movie():
    movie_data = json.loads(request.data)

    # assign random id
    while True:
        generated_id = random.randint(0, 1000)
        movie_data["id"] = generated_id

        all_movies = list(g_db.movie_collection.find({}))
        for obj in all_movies:
            if movie_data["id"] == obj["id"]:
                continue
        break

    ## ALL CHECKS HAVE PASSED
    added = my_mongo.mongo_add_movie(g_collection, movie_data)
    if added is True:
        # 201 CREATED
        resp = Response(
            json_util.dumps(movie_data), status=201, mimetype="application/json"
        )
        resp.headers["Content-Location"] = "/movies/" + str(movie_data["id"])
        return resp
    else:
        # 422 UNPROCESSABLE ENTITY
        resp = Response(
            json_util.dumps(movie_data), status=422, mimetype="application/json"
        )
        return resp


# 200 status code netinka paupdatinus
# Padavus json kuris nepraeina verification, siuncia kad 200, nors nieko neideda
# Toks pat bug kaip Patch kai kableliu truksta tada html errro
# jeigu neegzistuoja toks ID tada reikia insert, o jeigu exist tada update, nes update_one neideda naujos reiksmes
@app.route("/movies/<int:movie_id>", methods=["PUT"])
def update_movie(movie_id):
    # CHECK IF JSON IS OF GOOD FORMAT
    new_movie_data = json.loads(request.data)
    new_movie_data["id"] = movie_id
    # GET OLD MOVIE DATA
    old_movie_data = my_mongo.get_movie(g_collection, movie_id)
    # NO MOVIE WITH SUCH ID EXISTS YET, SO PERFORMING MONGO_ADD INSTEAD OF MONGO UPDATE
    if old_movie_data is None:
        my_mongo.add_movie(g_collection, new_movie_data)
    else:
        # UPDATING
        query_filter = {"id": movie_id}
        query_value = {"$set": new_movie_data}
        my_mongo.update_movie(g_collection, movie_id, query_filter, query_value)

    response_data = {"old_movie_data": old_movie_data, "new_movie_data": new_movie_data}
    # 200 OK
    resp = Response(
        json_util.dumps(response_data), status=200, mimetype="application/json"
    )
    resp.headers["Content-Location"] = "/movies/" + str(movie_id)
    return resp


# paduodi objekta kuriame yra laukai kurios reikia keisti
# parodo new vs old pilnus objektus
# BUGS kai paduodi netvarkinga json( be kableliu)
# BUGS kai paduodi movie_id bloga
@app.route("/movies/<int:movie_id>", methods=["PATCH"])
def patch_movie(movie_id):
    new_movie_data = json.loads(request.data)

    cursor = my_mongo.get_movie(g_collection, movie_id)

    if cursor is None:
        return Response(
            json.dumps({"Error": "No such id exists"}),
            status=404,
            mimetype="application/json",
        )
    else:
        # query filters for mongo_db
        query_filter = {"id": movie_id}
        query_values = {"$set": new_movie_data}
        # saving old movie data for output
        old_movie_data = g_db.movie_collection.find_one(query_filter, {"_id": 0})
        # updating
        try:
            g_db.movie_collection.update_one(query_filter, query_values)
        # VALIDATION FAILED
        except errors.WriteError:
            # 422 UNPROCESSABLE ENTITY
            return Response(
                json_util.dumps(new_movie_data), status=422, mimetype="application/json"
            )
        # getting updated movie data for output
        new_movie_data = g_db.movie_collection.find_one(query_filter, {"_id": 0})

        # output
        response_data = {
            "old_movie_data": old_movie_data,
            "new_movie_data": new_movie_data,
        }

        # 200 OK
        resp = Response(
            json.dumps(response_data), status=200, mimetype="application/json"
        )
        resp.headers["Content-Location"] = "/movies/" + str(movie_id)
        return resp


# IDEMPOTENT
@app.route("/movies/<int:movie_id>", methods=["DELETE"])
def delete_movie(movie_id):
    cursor = my_mongo.get_movie(g_collection, movie_id)
    if cursor is None:
        # 404 NOT FOUND
        return Response(
            json.dumps({"Error": f"No such id:{movie_id} exists"}),
            status=404,
            mimetype="application/json",
        )
    else:
        movie_data = cursor.copy()
        my_mongo.delete_movie(g_collection, movie_id)
        # 200 OK
        return Response(
            json_util.dumps(movie_data), status=200, mimetype="application/json"
        )


## MAIN
def main():
    for json_obj in my_data.data:
        my_mongo.add_movie(g_collection, json_obj)

    app.run(host="0.0.0.0", debug=True, port=80)


if __name__ == "__main__":
    main()

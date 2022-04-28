import py_compile
from flask import Flask, request, json, Response
import my_data
import my_mongo
import random


### FLASK
app = Flask(__name__)


### REST/API METHODS BELOW
@app.route("/")
def index():
    return "Welcome!"


@app.route("/movies/", methods=["GET"])
def get_movie():
    movies = my_mongo.get_all_movies()
    return Response(json.dumps(list(movies)), status=200, mimetype="application/json")


@app.route("/movies/<int:movie_id>", methods=["GET"])
def get_all_movies(movie_id):
    movie = my_mongo.get_movie(movie_id)
    if movie is None:
        # 404 NOT FOUND
        return Response(
            json.dumps({"Error": "No such id exists"}),
            status=404,
            mimetype="application/json",
        )
    # 200 OK
    return Response(json.dumps(movie), status=200, mimetype="application/json")


@app.route("/movies/", methods=["POST"])
def create_movie():
    movie_data = json.loads(request.data)

    # assign random id
    while True:
        generated_id = random.randint(0, 1000)
        movie_data["id"] = generated_id

        # all_movies = list(g_db.movie_collection.find({}))
        all_movies = list(my_mongo.get_all_movies())
        for obj in all_movies:
            if movie_data["id"] == obj["id"]:
                continue
        break

    ## ALL CHECKS HAVE PASSED
    # passing copy of movie data so it does not add mongo _id field and can return response with json dumps
    added = my_mongo.add_movie(movie_data.copy())
    if added is True:
        # 201 CREATED
        resp = Response(json.dumps(movie_data), status=201, mimetype="application/json")
        # Somehow make this header below fit into Response constructor?
        resp.headers["Content-Location"] = "/movies/" + str(movie_data["id"])
        return resp
    else:
        # 422 UNPROCESSABLE ENTITY
        resp = Response(json.dumps(movie_data), status=422, mimetype="application/json")
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
    old_movie_data = my_mongo.get_movie(movie_id)
    # NO MOVIE WITH SUCH ID EXISTS YET, SO PERFORMING MONGO_ADD INSTEAD OF MONGO UPDATE
    if old_movie_data is None:
        my_mongo.add_movie(new_movie_data)
    else:
        # UPDATING
        query_filter = {"id": movie_id}
        query_value = {"$set": new_movie_data}
        my_mongo.update_movie(movie_id, query_filter, query_value)

    response_data = {"old_movie_data": old_movie_data, "new_movie_data": new_movie_data}
    # 200 OK
    resp = Response(json.dumps(response_data), status=200, mimetype="application/json")
    resp.headers["Content-Location"] = "/movies/" + str(movie_id)
    return resp


# paduodi objekta kuriame yra laukai kurios reikia keisti
# parodo new vs old pilnus objektus
# BUGS kai paduodi netvarkinga json( be kableliu)
# BUGS kai paduodi movie_id bloga
@app.route("/movies/<int:movie_id>", methods=["PATCH"])
def patch_movie(movie_id):
    new_movie_data = json.loads(request.data)

    cursor = my_mongo.get_movie(movie_id)

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
        # old_movie_data = g_db.movie_collection.find_one(query_filter, {"_id": 0})
        old_movie_data = my_mongo.get_movie(movie_id)
        # updating
        try:
            # g_db.movie_collection.update_one(query_filter, query_values)
            my_mongo.update_movie(movie_id, query_filter, query_values)
        # VALIDATION FAILED
        except:
            # 422 UNPROCESSABLE ENTITY
            return Response(
                json.dumps(new_movie_data), status=422, mimetype="application/json"
            )
        # getting updated movie data for output
        # new_movie_data = g_db.movie_collection.find_one(query_filter, {"_id": 0})
        new_movie_data = my_mongo.get_movie(movie_id)

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
    cursor = my_mongo.get_movie(movie_id)
    if cursor is None:
        # 404 NOT FOUND
        return Response(
            json.dumps({"Error": f"No such id:{movie_id} exists"}),
            status=404,
            mimetype="application/json",
        )
    else:
        movie_data = cursor.copy()
        my_mongo.delete_movie(movie_id)
        # 200 OK
        return Response(json.dumps(movie_data), status=200, mimetype="application/json")


## MAIN
def main():
    for json_obj in my_data.data:
        my_mongo.add_movie(json_obj)

    app.run(host="0.0.0.0", debug=True, port=80)


if __name__ == "__main__":
    main()

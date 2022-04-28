# Returns True if adding succesffuly
# some better implemenation?
def add_movie(collection, data):
    # seems bad
    try:
        collection.insert_one(data)
        return True
    except:
        print("Error inserting.")
        return False


# returns cursor object of all movies
def get_all_movies(collection):
    return collection.find({}, {"_id": 0})


# returns cursor object of found(None if no movie found with such id) movie
def get_movie(collection, movie_id: int):
    return collection.find_one({"id": movie_id}, {"_id": 0})


# Something with error handling because now this func does nothing more than update_one
def update_movie(collection, movie_id: int, query_filter, query_value):
    collection.update_one(query_filter, query_value)


def delete_movie(collection, movie_id: int):
    collection.delete_one({"id": movie_id})

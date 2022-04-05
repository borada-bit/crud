FROM mongo
COPY data.csv /data.csv
CMD mongoimport --uri mongodb://mongodb:27017/movie_database --collection movie_collection --type csv --file /data.csv --headerline


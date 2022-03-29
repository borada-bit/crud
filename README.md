# crud web service
Sample Web Service CRUD application Movie database


## Requirements:
docker


## To launch:

`docker build -t crud .`

`docker run -d -p 80:80 --name crud_test crud`

OR
`chmod +x run.sh`

`./run.sh` starts app in detached mode, `docker logs crud_test` to see output


Restful service address `localhost:80/movies`


Movie json structure {

	"title": string,
	
	"year": integer,
	
	"genre": string,
	
	"director": string,
	
	"runtime": integer
}


## RESTFUL API:

`curl is a command-line tool for transferring data using various network protocols`


(CREATE)
POST http://localhost:80/movies

Example: `curl -i -H "Content-Type: application/json" -X POST -d '{"title":"Avengers", "year": 2012, "genre": "action", "director": "Josh Whedon", "runtime": 143}' http://localhost:80/movies/`


(READ)
GET http://localhost:80/movies/<movie_id>

Example: `curl http://localhost:80/movies/1 -X GET`


(READ ALL)
GET http://localhost:80/movies/

Example: `curl http://localhost:80/movies/ -X GET`

(UPDATE)
PUT http://localhost:80/movies/

Example: `curl -i -H "Content-Type: application/json" -X PUT -d '{"title":"The Batman Begins", "year": 2005, "genre": "action", "director": "Christopher Nolan", "runtime": 140}' http://localhost:80/movies/1`

(DELETE)
DELETE http://localhost:80/movies/<movie_id>

Example: `curl http://localhost:80/movies/1 -X DELETE`


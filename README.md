# API for Movie Database
Simple Web Service CRUD application movie database 

## Requirements:
* docker
* git

## To launch:
```bash
git clone https://github.com/borada-bit/crud.git
cd crud
docker-compose build
docker-compose up
```

## Usage
Test the API with [Postman](https://www.postman.com/).

### Example JSON

```JSON
[ 
	{
	"title": "Avengers",
	"year": 2012,
	"genre": "Action",
	"director": "Josh Whedon",
	"runtime": 143,
	"comment": "Amazing action movie!"
	}
]
```

## RESTFUL API:
### POST 

`http://localhost:80/movies/`

### GET
#### Get a movie by id:

`http://localhost:80/movies/<movie_id>`

#### Get all movies:

`http://localhost:80/movies/`

### PUT
#### Update movie by id:

`http://localhost:80/movies/<movie_id>`

### PATCH
#### Modify movie fields by id:

`http://localhost:80/movies/<movie_id>`

### DELETE 
#### Delete movie by id:

`http://localhost:80/movies/<movie_id>`

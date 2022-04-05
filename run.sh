#!/bin/bash

docker-compose rm -f
docker rmi crud_web
docker rmi crud_mongo_seed
docker-compose build
docker-compose up


#!/bin/bash

docker stop crud_test
docker rm crud_test
docker image rm crud
docker build -t crud .
docker run -d -p 80:80 --name crud_test crud  

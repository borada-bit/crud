# crud
Sample CRUD application

Requirements:
docker

To launch:
docker build -t crud . 
docker run -d -p 80:80 --name crud_test crud
OR
chmod +x run.sh
./run.sh  // starts app in detached mode, `docker logs crud_test` to see output

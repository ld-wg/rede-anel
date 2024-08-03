#!/bin/bash

# Navigate to the directory containing the Dockerfile
cd ~/Documents/rede-anel

# Build the Docker image
docker build -t my_python_app_image .

# Stop and remove previous processes
docker stop $(docker ps -q) && docker rm $(docker ps -a -q)

# Run Docker commands in separate Terminal windows
osascript -e 'tell application "Terminal" to do script "cd ~/Documents/rede-anel; docker run --net mynetwork --ip 192.168.0.2 -it my_python_app_image"'
osascript -e 'tell application "Terminal" to do script "cd ~/Documents/rede-anel; docker run --net mynetwork --ip 192.168.0.3 -it my_python_app_image"'
osascript -e 'tell application "Terminal" to do script "cd ~/Documents/rede-anel; docker run --net mynetwork --ip 192.168.0.4 -it my_python_app_image"'
osascript -e 'tell application "Terminal" to do script "cd ~/Documents/rede-anel; docker run --net mynetwork --ip 192.168.0.5 -it my_python_app_image"'

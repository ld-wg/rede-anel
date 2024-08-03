# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any necessary dependencies (assuming you may need them)
# RUN pip install --no-cache-dir

# Make port 20001-20004 available to the world outside this container
EXPOSE 20001 20002 20003 20004

# Run main.py when the container launches
CMD ["python", "main.py"]

# Build the Docker Image
# Navigate to the directory containing your Dockerfile and run the following command to build your Docker image:
# docker build -t my_python_app_image .

# Create a Docker Network
# Before running your containers, create a Docker network that will allow the containers to communicate with each other:
# docker network create --subnet=192.168.0.0/24 mynetwork

# Run the Docker Containers
# Now, you can start your containers, each with a specific IP address from your config.json:
# docker run --net mynetwork --ip 192.168.0.2 -it my_python_app_image
# docker run --net mynetwork --ip 192.168.0.3 -it my_python_app_image
# docker run --net mynetwork --ip 192.168.0.4 -it my_python_app_image
# docker run --net mynetwork --ip 192.168.0.5 -it my_python_app_image

# Stop and remove all dockers
# docker stop $(docker ps -q) && docker rm $(docker ps -a -q)

# Log in
# docker exec -it [container_id] /bin/bash
# ping google.com  # or another internal IP to test
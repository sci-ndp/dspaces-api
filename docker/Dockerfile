# Dockerfile to package dspaces-api

# Use the existing base image
FROM philipdavis/dspaces-build:v22082024

# Set up a working directory
WORKDIR /app

# Copy the entire application code into the container
COPY . /app

# Ensure start.sh is executable
RUN chmod +x ./start.sh

# The CMD will execute your start.sh script
CMD ["./start.sh"]
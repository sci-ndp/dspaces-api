# Use the existing base image
FROM philipdavis/dspaces-build:v22082024

# Set up a working directory
WORKDIR /app

# Ensure start.sh is executable
# We don't need to COPY files since we're using a volume mount in docker-compose.yml

# The CMD will execute your start.sh script
CMD ["./start.sh"]

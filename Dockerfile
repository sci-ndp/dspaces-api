# Use the existing base image
FROM philipdavis/dspaces-build:v22082024

# Set up a working directory
WORKDIR /app

# Copy the application code
COPY . /app/

# Create empty data directory for newly ingested datasets only
RUN mkdir -p /data

# Install Python dependencies
RUN pip install -r requirements.txt

# Ensure start.sh is executable
RUN chmod +x start.sh

# Expose the port (will be set by environment variable)
EXPOSE 8000

# The CMD will execute your start.sh script
CMD ["./start.sh"]

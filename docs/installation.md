## Installation

Follow these steps to install and set up the sciDX API on your local machine:

### Prerequisites

Make sure you have the following installed on your system:

- **Python 3.8+**
- **Docker** and **Docker Compose**(if you plan to use the Docker setup). 
- **Git**

### Clone the Repository

Clone the DataSpaces API repository from GitHub:

```bash
git clone https://github.com/sci-ndp/dspaces-api
cd dspaces-api
```

### Environment Configuration

1. Copy the example environment files and adjust the configuration as needed:

   ```bash
   cp ./env_variables/env_dspaces.example ./env_variables/.env_dspaces
   cp ./env_variables/env_api.example ./env_variables/.env_api
   ```

2. Edit the `.env` files to match your local environment or deployment needs.

### Running the Application

Start the application using one of the following methods:

- **With Docker**:

  ```bash
  docker-compose up
  ```

### Accessing the API

Once the application is running, you can access the DataSpaces API at:

- **Local environment**: `http://127.0.0.1:8001`
- **Docker environment**: `http://localhost:8001`

Return to [README](../README.md).

# DataSpaces Configuration
Configuration can be passed to the DataSpaces server itself using the `dspaces.toml` file.

# Enable Unsafe DataSpaces Operations
To enable remote execution via the DataSpaces API, add the environement variable `DSPACES_UNSAFE_ENDPOINTS=True` to `.env_dspaces`. This enables public endpoints that execute Python code on the DataSpaces server, with all the privileges of the user running DataSpaces. This is a security and privacy risk, and should not be enabled on a shared or public installation.

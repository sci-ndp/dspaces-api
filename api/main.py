from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import api.routes as routes
from .config import swagger_settings
from .configure_services import configure_services

# Create a FastAPI app instance with custom Swagger UI settings
app = FastAPI(
    title=swagger_settings.swagger_title,
    description=swagger_settings.swagger_description,
    version=swagger_settings.swagger_version,
)

# Add CORS middleware to allow cross-origin requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define an event handler for the 'startup' event to configure services on app
# startup
@app.on_event("startup")
async def startup_event():
    await configure_services()

app.include_router(routes.default_router, include_in_schema=False)
app.include_router(routes.dspaces_router, tags=["DataSpaces"], prefix="/dspaces")
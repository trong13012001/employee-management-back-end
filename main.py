from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from Routers import  login, user,employee
from sockets import sio_app

# Create FastAPI app instance
app = FastAPI()

# Define CORS origins
origins = [
    "http://localhost",
    "http://localhost:8080", 
    "http://localhost:3000",
    "http://localhost:8081", 

]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static files
app.mount("/images", StaticFiles(directory="images"), name="images")

# Include FastAPI routers at the root path
app.include_router(login.router, tags=['Login Controller'])
app.include_router(user.router, tags=['User Controller'])
app.include_router(employee.router, tags=['Employee Controller'])
# app.include_router(position.router, tags=['Position Controller'])
# app.include_router(status.router, tags=['Status Controller'])
# app.include_router(task.router, tags=['Task Controller'])
# app.include_router(tag.router, tags=['Tag Controller'])
# app.include_router(comment.router, tags=['Comment Controller'])

# Mount Socket.IO app at a sub-path
app.mount('/', sio_app)

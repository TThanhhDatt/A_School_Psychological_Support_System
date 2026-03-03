from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from app.routes import routes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins (e.g., ["http://localhost:3000"]) in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Include OPTIONS
    allow_headers=["Content-Type", "Action"],  # Allow custom Action header
)

app.include_router(routes.router)

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8080)
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.routes.auth import router as auth_router
from app.routes.chat import router as chat_router
from app.routes.websocket import router as ws_router
from app.routes.upload import router as upload_router
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Realtime Chat Backend")

# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Serve frontend files
app.mount("/static", StaticFiles(directory="frontend", html=True), name="static")

@app.get("/")
async def root():
    return RedirectResponse(url="/static/login.html")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(ws_router)
app.include_router(upload_router)



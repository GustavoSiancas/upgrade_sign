from fastapi import FastAPI

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers.sign import router as sign_router
from controllers.resize_images import router as resize_router
from controllers.carnet import router as carnet_router

app = FastAPI(
    title="Upgrade Sign API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sign_router)
app.include_router(resize_router)
app.include_router(carnet_router)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, bookings, public, schedules

app = FastAPI(title="SlotBook API")

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"CORS allow_origins: {settings.cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(schedules.router)
app.include_router(bookings.router)
app.include_router(public.router)


@app.get("/health")
async def health():
    return {"status": "ok"}

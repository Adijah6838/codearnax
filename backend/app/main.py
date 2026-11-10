from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analytics import router as analytics_router
from app.api.assessments import router as assessments_router
from app.api.auth import router as auth_router
from app.api.challenges import router as challenges_router
from app.api.leaderboard import router as leaderboard_router
from app.api.submissions import router as submissions_router
from app.api.websockets import router as ws_router
from app.config import settings
from app.db.init import initialize_database
from app.services.queue import queue


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    await queue.start()
    yield
    await queue.stop()


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

# --- ADD THIS CORS MIDDLEWARE BLOCK ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --------------------------------------

app.include_router(auth_router)
app.include_router(challenges_router)
app.include_router(submissions_router)
app.include_router(assessments_router)
app.include_router(ws_router)
app.include_router(analytics_router)
app.include_router(leaderboard_router)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME}
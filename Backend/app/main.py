from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from .routers import activities as activities_router
from .routers import analytics as analytics_router
from .routers import auth as auth_router
from .routers import chat as chat_router
from .routers import coins as coins_router
from .routers import config as config_router
from .routers import groups as groups_router
from .routers import join as join_router
from .routers import news as news_router
from .routers import places as places_router
from .routers import questions as questions_router
from .routers import users as users_router
from .routers import wellness as wellness_router

app = FastAPI(title=settings.APP_NAME)

cors_origins = settings.get_cors_origins() or [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://uis-go-admin-dev-20251130.s3-website-us-east-1.amazonaws.com",
    "https://uis-go-admin-dev-20251130.s3-website-us-east-1.amazonaws.com",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(groups_router.router, prefix="/groups", tags=["groups"])
app.include_router(activities_router.router, prefix="/activities", tags=["activities"])
app.include_router(analytics_router.router, prefix="/analytics", tags=["analytics"])
app.include_router(coins_router.router, prefix="/coins", tags=["coins"])
app.include_router(questions_router.router, prefix="/questions", tags=["questions"])
app.include_router(news_router.router, prefix="/news", tags=["news"])
app.include_router(wellness_router.router, prefix="/wellness", tags=["wellness"])
app.include_router(places_router.router, prefix="/places", tags=["places"])
app.include_router(chat_router.router, prefix="/chat", tags=["chat"])
app.include_router(config_router.router, prefix="/config", tags=["config"])
app.include_router(join_router.router, tags=["join"])
app.include_router(users_router.router, prefix="/users", tags=["users"])


@app.get("/")
def root():
    return {"ok": True, "app": settings.APP_NAME}


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}

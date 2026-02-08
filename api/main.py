from fastapi import FastAPI
from api.routes import router

app = FastAPI(
    title="ClauseAI",
    description="AI-powered legal contract analysis",
    version="1.0"
)

app.include_router(router)

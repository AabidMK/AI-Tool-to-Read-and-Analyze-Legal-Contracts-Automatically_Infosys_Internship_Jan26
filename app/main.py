from fastapi import FastAPI

from .routes import router

app = FastAPI(title="ClauseAI Document Analyzer")
app.include_router(router)
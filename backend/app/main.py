from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.db.session import init_db
from backend.app.api.auth_routes import router as auth_router
from backend.app.api.chat_routes import router as chat_router
from backend.app.api.memory_routes import router as memory_router
from backend.app.api.task_routes import router as task_router
from backend.app.api.calendar_routes import router as calendar_router
from backend.app.api.email_routes import router as email_router
from backend.app.api.document_routes import router as document_router
from backend.app.api.research_routes import router as research_router
from backend.app.api.admin_routes import router as admin_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema on startup
    await init_db()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Enterprise AI Personal & Executive Assistant SaaS platform by Technopie Consultant Pvt. Ltd.",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(chat_router, prefix=settings.API_PREFIX)
app.include_router(memory_router, prefix=settings.API_PREFIX)
app.include_router(task_router, prefix=settings.API_PREFIX)
app.include_router(calendar_router, prefix=settings.API_PREFIX)
app.include_router(email_router, prefix=settings.API_PREFIX)
app.include_router(document_router, prefix=settings.API_PREFIX)
app.include_router(research_router, prefix=settings.API_PREFIX)
app.include_router(admin_router, prefix=settings.API_PREFIX)

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "platform": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
        "company": "Technopie Consultant Pvt. Ltd."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import get_db, engine, Base
from app.models import User, Domain, Conversation, Message
from app.config import settings
from app.routers import auth, domains, conversations, chat
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Create FastAPI application instance
app = FastAPI(
    title=settings.app_name,
    description="A multi-domain AI chatbot API",
    version="1.0.0",
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],  # Your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure the static directory exists
static_dir = os.path.join(os.getcwd(), "static")
os.makedirs(static_dir, exist_ok=True)
os.makedirs(os.path.join(static_dir, "generated_images"), exist_ok=True)

# Mount the static directory
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Register routers
app.include_router(auth.router, prefix="/api")
app.include_router(domains.router, prefix="/api")
app.include_router(conversations.router, prefix="/api")
app.include_router(chat.router, prefix="/api")

# Create database tables (only if they don't exist)
# In production, you'd use Alembic migrations instead
Base.metadata.create_all(bind=engine)

@app.on_event("startup")
async def startup_event():
    """Code to run when the application starts"""
    print(f"Starting {settings.app_name}")
    print(f"Static directory: {static_dir}")
    # Here you could add startup tasks like:
    # - Database connection testing
    # - Loading initial data
    # - Setting up background tasks

@app.on_event("shutdown")
async def shutdown_event():
    """Code to run when the application shuts down"""
    print(f"Shutting down {settings.app_name}")

# Root endpoint - basic health check
@app.get("/")
async def root():
    """Root endpoint to check if API is running"""
    return {
        "message": "Domain Chatbot API is running!",
        "version": "1.0.0",
        "status": "healthy"
    }

# Health check endpoint
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify database connection"""
    try:
        # Try to query the database
        user_count = db.query(User).count()
        return {
            "status": "healthy",
            "database": "connected",
            "total_users": user_count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

# Test endpoint to verify database models work
@app.get("/test-db")
async def test_database(db: Session = Depends(get_db)):
    """Test endpoint to verify our database models work"""
    try:
        # Count records in each table
        users = db.query(User).count()
        domains = db.query(Domain).count()
        conversations = db.query(Conversation).count()
        messages = db.query(Message).count()
        return {
            "database_status": "working",
            "table_counts": {
                "users": users,
                "domains": domains,
                "conversations": conversations,
                "messages": messages
            }
        }
    except Exception as e:
        return {
            "database_status": "error",
            "error": str(e)
        }
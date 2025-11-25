"""
Database connection and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from backend.config import settings
from typing import Generator, Optional

# Database connection - supports PostgreSQL and SQLite
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # PostgreSQL connection pool optimization
    connect_args = {
        "connect_timeout": 10,
        "options": "-c statement_timeout=30000"  # 30 second query timeout
    }

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_size=10,  # Connection pool size
    max_overflow=20,  # Max overflow connections
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_timeout=30,  # Timeout for getting connection from pool
    echo=settings.DEBUG,
    future=True  # Use SQLAlchemy 2.0 style
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency
    Usage in FastAPI endpoints: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Redis connection (optional) with connection pooling
redis_client = None
try:
    import redis
    from redis.connection import ConnectionPool
    
    # Create connection pool for better performance
    redis_pool = ConnectionPool.from_url(
        settings.REDIS_URL,
        max_connections=50,
        socket_timeout=5,
        socket_connect_timeout=5,
        decode_responses=True
    )
    redis_client = redis.Redis(connection_pool=redis_pool)
    # Test connection - if it fails, set client to None
    try:
        redis_client.ping()
    except:
        redis_client = None
except Exception as e:
    print(f"WARNING: Redis not available: {e}")
    print("   Backend will run without caching")
    redis_client = None


def get_redis():
    """Get Redis client"""
    return redis_client


# MongoDB connection (optional for analytics)
mongo_client = None
mongo_db = None
try:
    from pymongo import MongoClient
    mongo_client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=2000)
    mongo_client.server_info()  # Test connection
    mongo_db = mongo_client.gamma_clone
except Exception as e:
    print(f"WARNING: MongoDB not available: {e}")
    print("   Backend will run without analytics storage")


def get_mongo():
    """Get MongoDB database"""
    return mongo_db


# Initialize database
def init_db():
    """Create all tables"""
    # Import all models to register them with SQLAlchemy
    from backend.models import (
        user, presentation, template, theme, workspace,
        comment, analytics, billing
    )
    Base.metadata.create_all(bind=engine)


# Close connections
def close_connections():
    """Close all database connections"""
    try:
        engine.dispose()
    except Exception as e:
        print(f"[ERROR] Engine dispose failed: {e}")
    
    if redis_client:
        try:
            redis_client.close()
        except Exception as e:
            print(f"[ERROR] Redis close failed: {e}")
    
    if mongo_client:
        try:
            mongo_client.close()
        except Exception as e:
            print(f"[ERROR] Mongo close failed: {e}")

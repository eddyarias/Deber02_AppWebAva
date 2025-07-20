"""
FastAPI Songs CRUD API with DynamoDB backend.
"""
import logging
from typing import List
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from .crud import song_crud
from .schemas import SongCreate, SongUpdate, SongResponse, ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Songs CRUD API")
    try:
        # Test database connection
        await song_crud.get_all_songs()
        logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Songs CRUD API")


# FastAPI application
app = FastAPI(
    title="Songs CRUD API",
    description="A RESTful API for managing songs using Amazon DynamoDB",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc)}
    )


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "message": "Songs CRUD API - DynamoDB Version",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    try:
        # Test database connectivity
        await song_crud.get_all_songs()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )


# Song endpoints
@app.get(
    "/songs",
    response_model=List[SongResponse],
    tags=["Songs"],
    summary="Get all songs",
    description="Retrieve all songs from the database"
)
async def get_songs():
    """Get all songs"""
    try:
        songs = await song_crud.get_all_songs()
        return songs
    except Exception as e:
        logger.error(f"Error retrieving songs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve songs"
        )


@app.post(
    "/songs",
    response_model=SongResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Songs"],
    summary="Create a new song",
    description="Create a new song in the database"
)
async def create_song(song: SongCreate):
    """Create a new song"""
    try:
        created_song = await song_crud.create_song(song)
        return created_song
    except Exception as e:
        logger.error(f"Error creating song: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create song"
        )


@app.get(
    "/songs/{song_id}",
    response_model=SongResponse,
    tags=["Songs"],
    summary="Get a song by ID",
    description="Retrieve a specific song by its ID"
)
async def get_song(song_id: str):
    """Get a song by ID"""
    try:
        song = await song_crud.get_song_by_id(song_id)
        if song is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Song with ID {song_id} not found"
            )
        return song
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving song {song_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve song"
        )


@app.put(
    "/songs/{song_id}",
    response_model=SongResponse,
    tags=["Songs"],
    summary="Update a song",
    description="Update an existing song by its ID"
)
async def update_song(song_id: str, song: SongUpdate):
    """Update a song"""
    try:
        updated_song = await song_crud.update_song(song_id, song)
        if updated_song is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Song with ID {song_id} not found"
            )
        return updated_song
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating song {song_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update song"
        )


@app.delete(
    "/songs/{song_id}",
    tags=["Songs"],
    summary="Delete a song",
    description="Delete a song by its ID"
)
async def delete_song(song_id: str):
    """Delete a song"""
    try:
        deleted_song = await song_crud.delete_song(song_id)
        if deleted_song is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Song with ID {song_id} not found"
            )
        return {
            "message": "Song deleted successfully",
            "deleted_song": deleted_song
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting song {song_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete song"
        )

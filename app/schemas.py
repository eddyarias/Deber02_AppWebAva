"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional


class SongBase(BaseModel):
    """Base song schema with common fields"""
    name: str = Field(..., min_length=1, max_length=200, description="Song name")
    path: str = Field(..., description="Song file path or URL")
    plays: int = Field(default=0, ge=0, description="Number of times played")


class SongCreate(SongBase):
    """Schema for creating a new song"""
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Imagine",
                "path": "https://example.com/songs/imagine.mp3",
                "plays": 0
            }
        }


class SongUpdate(BaseModel):
    """Schema for updating an existing song"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Song name")
    path: Optional[str] = Field(None, description="Song file path or URL")
    plays: Optional[int] = Field(None, ge=0, description="Number of times played")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Imagine - Updated",
                "path": "https://example.com/songs/imagine-v2.mp3",
                "plays": 1500
            }
        }


class SongResponse(SongBase):
    """Schema for song response with ID"""
    id: str = Field(..., description="Unique song identifier")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Imagine",
                "path": "https://example.com/songs/imagine.mp3",
                "plays": 1000
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response schema"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Song not found",
                "detail": "No song found with the provided ID"
            }
        }
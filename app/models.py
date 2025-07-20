"""
Song model definitions and data structures for DynamoDB operations.
"""
from typing import Optional
from pydantic import BaseModel, Field


class DynamoDBSong(BaseModel):
    """
    Song model representation for DynamoDB
    Table: TBL_SONG
    """
    id: str = Field(..., description="Unique song identifier (UUID)")
    name: str = Field(..., min_length=1, max_length=200, description="Song name")
    path: str = Field(..., description="Song file path or URL")
    plays: int = Field(default=0, ge=0, description="Number of times the song has been played")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Imagine",
                "path": "https://example.com/songs/imagine.mp3",
                "plays": 1000
            }
        }

"""
CRUD operations for songs using DynamoDB.
"""
import uuid
import logging
from typing import List, Optional, Dict, Any
from botocore.exceptions import ClientError
from .database import get_table
from .schemas import SongCreate, SongUpdate, SongResponse

# Configure logging
logger = logging.getLogger(__name__)


class SongCRUD:
    """Song CRUD operations"""
    
    def __init__(self):
        self.table = get_table()
    
    async def get_all_songs(self) -> List[Dict[str, Any]]:
        """Get all songs from DynamoDB"""
        try:
            response = self.table.scan()
            songs = response.get('Items', [])
            
            # Handle pagination if needed
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                songs.extend(response.get('Items', []))
            
            logger.info(f"Retrieved {len(songs)} songs")
            return songs
        except ClientError as e:
            logger.error(f"Error getting songs: {e}")
            raise Exception(f"Failed to retrieve songs: {e}")
    
    async def create_song(self, song_data: SongCreate) -> Dict[str, Any]:
        """Create a new song in DynamoDB"""
        try:
            song_id = str(uuid.uuid4())
            
            item = {
                'id': song_id,
                'name': song_data.name,
                'path': song_data.path,
                'plays': song_data.plays
            }
            
            self.table.put_item(Item=item)
            logger.info(f"Created song with ID: {song_id}")
            return item
        except ClientError as e:
            logger.error(f"Error creating song: {e}")
            raise Exception(f"Failed to create song: {e}")
    
    async def get_song_by_id(self, song_id: str) -> Optional[Dict[str, Any]]:
        """Get a single song by ID"""
        try:
            response = self.table.get_item(Key={'id': song_id})
            song = response.get('Item')
            
            if song:
                logger.info(f"Retrieved song: {song_id}")
            else:
                logger.warning(f"Song not found: {song_id}")
            
            return song
        except ClientError as e:
            logger.error(f"Error getting song {song_id}: {e}")
            raise Exception(f"Failed to retrieve song: {e}")
    
    async def update_song(self, song_id: str, song_data: SongUpdate) -> Optional[Dict[str, Any]]:
        """Update a song in DynamoDB"""
        try:
            # Check if song exists first
            existing_song = await self.get_song_by_id(song_id)
            if not existing_song:
                return None
            
            # Build update expression dynamically
            update_expression_parts = []
            expression_attribute_names = {}
            expression_attribute_values = {}
            
            if song_data.name is not None:
                update_expression_parts.append("#name = :name")
                expression_attribute_names['#name'] = 'name'
                expression_attribute_values[':name'] = song_data.name
            
            if song_data.path is not None:
                update_expression_parts.append("#path = :path")
                expression_attribute_names['#path'] = 'path'
                expression_attribute_values[':path'] = song_data.path
            
            if song_data.plays is not None:
                update_expression_parts.append("plays = :plays")
                expression_attribute_values[':plays'] = song_data.plays
            
            if not update_expression_parts:
                # No fields to update
                return existing_song
            
            update_expression = "SET " + ", ".join(update_expression_parts)
            
            response = self.table.update_item(
                Key={'id': song_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW"
            )
            
            updated_song = response.get('Attributes')
            logger.info(f"Updated song: {song_id}")
            return updated_song
        except ClientError as e:
            logger.error(f"Error updating song {song_id}: {e}")
            raise Exception(f"Failed to update song: {e}")
    
    async def delete_song(self, song_id: str) -> Optional[Dict[str, Any]]:
        """Delete a song from DynamoDB"""
        try:
            response = self.table.delete_item(
                Key={'id': song_id},
                ReturnValues="ALL_OLD"
            )
            
            deleted_song = response.get('Attributes')
            if deleted_song:
                logger.info(f"Deleted song: {song_id}")
            else:
                logger.warning(f"Song not found for deletion: {song_id}")
            
            return deleted_song
        except ClientError as e:
            logger.error(f"Error deleting song {song_id}: {e}")
            raise Exception(f"Failed to delete song: {e}")


# Global CRUD instance
song_crud = SongCRUD()

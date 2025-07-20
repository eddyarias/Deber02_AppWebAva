"""
DynamoDB database configuration and connection management.
"""
import boto3
import os
import logging
from typing import Optional
from botocore.exceptions import ClientError, NoCredentialsError

# Configure logging
logger = logging.getLogger(__name__)


class DynamoDBConfig:
    """DynamoDB configuration and connection manager"""
    
    def __init__(self):
        self.region_name = os.getenv('AWS_REGION', 'us-east-1')
        self.table_name = os.getenv('DYNAMODB_TABLE_NAME', 'TBL_SONG')
        self._dynamodb_resource = None
        self._table = None
    
    @property
    def dynamodb_resource(self):
        """Get or create DynamoDB resource"""
        if self._dynamodb_resource is None:
            try:
                self._dynamodb_resource = boto3.resource(
                    'dynamodb',
                    region_name=self.region_name,
                    aws_access_key_id="******************",
                    aws_secret_access_key="******************"
                )
                logger.info(f"Connected to DynamoDB in region: {self.region_name}")
            except NoCredentialsError:
                logger.error("AWS credentials not found")
                raise
            except Exception as e:
                logger.error(f"Error connecting to DynamoDB: {e}")
                raise
        return self._dynamodb_resource
    
    @property
    def table(self):
        """Get DynamoDB table"""
        if self._table is None:
            try:
                self._table = self.dynamodb_resource.Table(self.table_name)
                # Verify table exists
                self._table.load()
                logger.info(f"Connected to table: {self.table_name}")
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    logger.error(f"Table {self.table_name} not found")
                    raise ValueError(f"Table {self.table_name} does not exist")
                else:
                    logger.error(f"Error accessing table: {e}")
                    raise
        return self._table


# Global database configuration instance
db_config = DynamoDBConfig()

def get_table():
    """Get DynamoDB table instance"""
    return db_config.table
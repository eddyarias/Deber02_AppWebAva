"""
DynamoDB table creation script for Songs API.
"""
import boto3
import os
import sys
import logging
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DynamoDBTableManager:
    """Manage DynamoDB table creation and configuration"""
    
    def __init__(self):
        self.region_name = os.getenv('AWS_REGION', 'us-east-1')
        self.table_name = os.getenv('DYNAMODB_TABLE_NAME', 'TBL_SONG')
        
        try:
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=self.region_name,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            logger.info(f"Connected to DynamoDB in region: {self.region_name}")
        except NoCredentialsError:
            logger.error("AWS credentials not found. Please check your .env file or AWS configuration.")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error connecting to DynamoDB: {e}")
            sys.exit(1)
    
    def table_exists(self) -> bool:
        """Check if the table already exists"""
        try:
            table = self.dynamodb.Table(self.table_name)
            table.load()
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                return False
            else:
                logger.error(f"Error checking table existence: {e}")
                raise
    
    def create_table(self) -> bool:
        """Create the songs table with optimized configuration"""
        try:
            if self.table_exists():
                logger.info(f"Table {self.table_name} already exists.")
                return True
            
            logger.info(f"Creating table {self.table_name}...")
            
            table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {
                        'AttributeName': 'id',
                        'KeyType': 'HASH'  # Partition key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'id',
                        'AttributeType': 'S'  # String
                    }
                ],
                BillingMode='PAY_PER_REQUEST',  # On-demand billing
                Tags=[
                    {
                        'Key': 'Project',
                        'Value': 'SongsCRUDAPI'
                    },
                    {
                        'Key': 'Environment',
                        'Value': os.getenv('ENVIRONMENT', 'development')
                    }
                ]
            )
            
            # Wait for table to be created
            logger.info("Waiting for table to be created...")
            table.wait_until_exists()
            
            # Enable point-in-time recovery (optional)
            try:
                self.dynamodb.meta.client.update_continuous_backups(
                    TableName=self.table_name,
                    PointInTimeRecoverySpecification={
                        'PointInTimeRecoveryEnabled': True
                    }
                )
                logger.info("Point-in-time recovery enabled")
            except Exception as e:
                logger.warning(f"Could not enable point-in-time recovery: {e}")
            
            logger.info(f"Table {self.table_name} created successfully!")
            return True
            
        except ClientError as e:
            logger.error(f"Error creating table: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False
    
    def describe_table(self):
        """Describe the table configuration"""
        try:
            table = self.dynamodb.Table(self.table_name)
            table.load()
            
            logger.info(f"Table Name: {table.table_name}")
            logger.info(f"Table Status: {table.table_status}")
            logger.info(f"Item Count: {table.item_count}")
            logger.info(f"Table Size: {table.table_size_bytes} bytes")
            logger.info(f"Key Schema: {table.key_schema}")
            logger.info(f"Billing Mode: {table.billing_mode_summary}")
            
        except ClientError as e:
            logger.error(f"Error describing table: {e}")


def main():
    """Main function to create the DynamoDB table"""
    logger.info("Starting DynamoDB table creation process...")
    
    manager = DynamoDBTableManager()
    
    if manager.create_table():
        logger.info("Table creation process completed successfully!")
        manager.describe_table()
    else:
        logger.error("Table creation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()

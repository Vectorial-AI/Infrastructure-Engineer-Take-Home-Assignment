import os
import ssl
import json
import boto3
from motor.motor_asyncio import AsyncIOMotorClient
from botocore.exceptions import ClientError
import logging
import traceback

logger = logging.getLogger()
logger.setLevel(logging.INFO)

async def get_secret_value():
    """Retrieve secret from AWS Secrets Manager."""
    try:
        secret_name = os.getenv("SECRETS_ARN")
        logger.info("Attempting to retrieve secret")
        
        if not secret_name:
            raise ValueError("SECRETS_ARN environment variable is not set")

        region_name = os.getenv("AWS_REGION", "ap-south-1")
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )

        logger.info("Fetching secret value")
        response = client.get_secret_value(SecretId=secret_name)
        
        if 'SecretString' not in response:
            raise ValueError("Secret value is not a string")
            
        secret_data = json.loads(response['SecretString'])
        logger.info("Successfully retrieved secret")
        return secret_data
        
    except Exception as e:
        logger.error("Error retrieving secret")
        logger.error(traceback.format_exc())
        raise

async def get_db():
    """Get database connection with proper error handling."""
    if not hasattr(get_db, "db"):
        try:
            logger.info("Initializing database connection")
            secret = await get_secret_value()
            
            # Log minimal connection info without exposing full details
            logger.info("Attempting database connection")
            
            # Create connection string with placeholder for sensitive info
            connection_string = (
                f"mongodb://{secret['username']}:****@"
                f"{secret['host']}:{secret['port']}/?ssl=true&"
                "replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"
            )

            # SSL context for DocumentDB
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            logger.info("Creating MongoDB client")
            # Create client with retry logic
            client = AsyncIOMotorClient(
                connection_string,
                ssl=True,
                ssl_cert_reqs=ssl.CERT_NONE,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                retryWrites=False
            )
            
            # Test the connection
            logger.info("Testing database connection")
            await client.admin.command('ismaster')
            
            db_name = os.getenv("DATABASE_NAME", "authservice")
            get_db.db = client[db_name]
            
            logger.info("Successfully connected to database")
        except Exception as e:
            logger.error("Database connection error")
            logger.error(traceback.format_exc())
            raise

    return get_db.db 
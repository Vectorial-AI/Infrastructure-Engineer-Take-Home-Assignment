import os
import boto3
import json
from pymongo import MongoClient
from aws_lambda_powertools import Logger

logger = Logger()

def get_database():
    try:
        # Get database credentials from AWS Secrets Manager
        secret_arn = os.environ.get("DB_SECRET_ARN")
        if not secret_arn:
            raise ValueError("DB_SECRET_ARN environment variable not set")
            
        secrets_client = boto3.client('secretsmanager')
        secret_value = secrets_client.get_secret_value(SecretId=secret_arn)
        secret = json.loads(secret_value['SecretString'])
        
        # Get MongoDB connection endpoint from environment
        db_endpoint = os.environ.get("DB_ENDPOINT")
        if not db_endpoint:
            raise ValueError("DB_ENDPOINT environment variable not set")
        
        # Mask actual endpoint in logs
        logger.info("Connecting to database at [MASKED_ENDPOINT]")
        
        # Construct connection string (credentials masked for security)
        connection_string = f"mongodb://{secret['username']}:[MASKED_PASSWORD]@{db_endpoint}:27017/?tls=true&retryWrites=false"
        
        # Initialize MongoDB client with connection timeouts
        client = MongoClient(
            connection_string,
            serverSelectionTimeoutMS=5000,  # 5 second timeout for server selection
            connectTimeoutMS=5000           # 5 second timeout for initial connection
        )
        
        # Verify connection is alive
        client.admin.command('ping')
        
        logger.info("Successfully connected to database")
        return client.auth_db
        
    except Exception as e:
        logger.exception("Failed to connect to database")
        raise

def verify_database_connection():
    """Utility function to verify database connection"""
    try:
        db = get_database()
        db.command('ping')
        return True, "Connection successful"
    except Exception as e:
        return False, str(e) 
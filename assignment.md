# Authentication Service on AWS - Implementation Documentation

## Project Overview
This project implements a serverless authentication service using Python FastAPI, AWS Lambda, and DocumentDB. The service provides secure user authentication with JWT tokens and is deployed using AWS CDK.

## AI Tools Used
- **ChatGPT**: Used for documentation generation and API endpoint structure
- **Claude**: Used for debugging DocumentDB connection issues and security configuration

## Architecture & Design Decisions

### Technology Stack
- Backend: Python FastAPI
- Database: Amazon DocumentDB (MongoDB compatible)
- Infrastructure: AWS CDK
- Deployment: AWS Lambda + API Gateway
- Authentication: JWT tokens with bcrypt password hashing

### Key Components

The service consists of three main layers:

1. API Layer
   - FastAPI framework for REST endpoints
   - JWT-based authentication
   - Input validation using Pydantic models

2. Database Layer
   - DocumentDB in private VPC
   - Connection pooling with timeout handling
   - Secure credential management via AWS Secrets Manager

3. Infrastructure Layer
   - Separate CDK stacks for API and Database
   - VPC with private subnets
   - Security groups with least privilege access

## Implementation Status

### Core Requirements

The implementation satisfies most core requirements with the following status:

Phase 1: Basic API Development ✓
- All required endpoints implemented
- Password hashing with bcrypt
- Input validation with Pydantic

Phase 2: Database Infrastructure ✓
- DocumentDB setup
- Security groups and VPC
- Backup policies
- Secure credential handling

Phase 3: API Deployment ✓
- Lambda deployment
- API Gateway configuration
- Environment variables
- CORS support

### Known Issues and Future Work

There are several critical issues that need attention:

1. DocumentDB Connection Stability
   - Intermittent connection timeouts during Lambda cold starts
   - Connection pooling requires configuration and optimization

2. TLS Certificate Management
   - TLS certificate verification requires special handling
   - Additional configuration needed in connection strings

3. VPC Connectivity Challenges
   - Lambda functions experience occasional VPC access delays
   - Current mitigation: VPC endpoints and NAT gateways
   - Needs monitoring and potential optimization

## Security Implementation

### Network Security
- VPC isolation for DocumentDB
- Security groups limiting access
- Private subnets for database instances

### Authentication & Authorization
- Password hashing using bcrypt
- JWT token validation
- Role-based access control

### Secrets Management
- AWS Secrets Manager for credentials
- Environment variables for configuration
- Secure secret rotation capability

## Deployment Process

### Prerequisites
```bash
npm install -g aws-cdk
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Deployment Steps
1. Deploy Database Stack:
   ```bash
   cdk deploy AuthServiceDatabase
   ```

2. Deploy API Stack:
   ```bash
   cdk deploy AuthServiceApi
   ```

## Required Dependencies

### Core Modules
- aws-cdk
- FastAPI
- python-jose
- passlib
- pymongo
- pydantic
- uvicorn
- boto3

## Project Structure
```
├── README.md
├── assignment.md
├── src/
│   └── api/
│       └── [API code]
├── cdk/
│   ├── lib/
│   │   ├── database-stack.py
│   │   └── api-stack.py
│   └── bin/

## Environment Variables
Required environment variables:
- `MONGODB_URI`: DocumentDB connection string
- `JWT_SECRET_KEY`: Secret for JWT token signing
- `ENVIRONMENT`: development/staging/production
- `LOG_LEVEL`: INFO/DEBUG/ERROR

## Support and Documentation
For technical issues and questions, refer to:
- AWS DocumentDB documentation
- FastAPI official documentation
- AWS CDK documentation

Please report any issues or bugs through the project's issue tracking system.

AWS S3 → Lambda → Amazon RDS PostgreSQL
Project overview

This project demonstrates an event-driven AWS architecture where files uploaded to Amazon S3 automatically trigger an AWS Lambda function.

The Lambda function logS3ObjectCreated:

receives the S3 ObjectCreated event
retrieves object metadata
reads the file contents
logs information to CloudWatch
stores metadata in an Amazon RDS PostgreSQL database

Architecture

          +----------------+
          |   Amazon S3    |
          +----------------+
                  │
          ObjectCreated Event (metadata) &
		       S3 Object (data)
                  │
                  ▼
        +-------------------+
        |   AWS Lambda      |
        |  (Python 3.13)    |
        +-------------------+
          │             │
          │             │
          ▼             ▼
 CloudWatch Logs     Amazon RDS
                    PostgreSQL
					
AWS Services used
- Amazon S3
  - General Purpose bucket
- AWS Lambda
  - Functions, with enviroment variables
  - Layers
  - Test Event JSON
- Amazon RDS PostgreSQL
- IAM
- VPC
- Security Groups
- Gateway VPC Endpoint (S3)
- CloudWatch
- AWS CLI
- CloudShell
- AWS Policy simulator

Technologies used
- Python 3.13
  - boto3
  - psycopg2
- PostgreSQL (scripts)
- DBeaver
- Visual Studio

Features
- automatic S3 event processing
- reads object metadata
- reads file contents
- inserts metadata into PostgreSQL
- CloudWatch logging
- environment variables for configuration
- Lambda Layer for psycopg2

Lessons learned
- Lambda networking inside a VPC
- Security Groups
- Lambda Layers
  - creating a Linux zipfile with CloudShell
- S3 Gateway Endpoints
- IAM permissions
- PostgreSQL connectivity
- CloudWatch debugging
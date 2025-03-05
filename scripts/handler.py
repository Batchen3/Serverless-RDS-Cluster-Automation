import os
import boto3

sqs = boto3.client('sqs')
secrets_manager = boto3.client('secretsmanager')

GITHUB_TOKEN_SECRET_NAME = os.getenv('GITHUB_TOKEN_SECRET_NAME')
GITHUB_REPO = os.getenv('GITHUB_REPO')
QUEUE_URL = os.getenv('QUEUE_URL')
BRANCH_NAME = "rds-provisioning"













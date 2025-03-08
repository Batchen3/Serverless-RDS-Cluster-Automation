import os
import boto3
import json
import logging
from github import Github

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# sqs = boto3.client('sqs')

secrets_manager = boto3.client('secretsmanager')

GITHUB_TOKEN_SECRET_NAME = os.getenv('GITHUB_TOKEN_SECRET_NAME')
GITHUB_REPO = os.getenv('GITHUB_REPO')
BRANCH_NAME = "rds-provisioning"

def get_github_token():
    logger.info("Fetching GitHub token from Secrets Manager")
    response = secrets_manager.get_secret_value(SecretId=GITHUB_TOKEN_SECRET_NAME)
    secret = json.loads(response['SecretString'])
    return secret.get('github-token')


def generate_terraform_tfvars(db_name, db_engine, instance_type):
    logger.info("Generating terraform.tfvars content for RDS configuration")
    return f"""
    db_instance_identifier = "{db_name}"
    db_engine             = "{db_engine}"
    db_instance_class     = "{instance_type}"
    """

def create_github_pr(terraform_configuration):
    github_token = get_github_token()
    g = Github(github_token)
    repo = g.get_repo(GITHUB_REPO)
    
    logger.info("Checking if branch exists")
    branch_exists = False
    try:
        repo.get_branch(BRANCH_NAME)
        branch_exists = True
    except:
        pass
    
    logger.info("Fetching rdsDeployment branch reference")
    rds_deployment_ref = repo.get_git_ref("heads/rdsDeployment")
    if not branch_exists:
        logger.info(f"Creating branch: {BRANCH_NAME}")
        repo.create_git_ref(ref=f"refs/heads/{BRANCH_NAME}", sha=rds_deployment_ref.object.sha)
    
    file_path = "terraform/terraform.tfvars"

    try:
        existing_file = repo.get_contents(file_path, ref=BRANCH_NAME)
        logger.info(f"Updating existing Terraform file: {file_path}")
        repo.update_file(file_path, "Updating terraform.tfvars", terraform_configuration, existing_file.sha, branch=BRANCH_NAME)    
    except:
        repo.create_file(file_path, "Adding terraform.tfvars", terraform_configuration, branch=BRANCH_NAME)
        
    logger.info("Creating GitHub PR")
    repo.create_pull(title="Provision RDS Cluster", body="This PR sets configuration for RDS cluster", head=BRANCH_NAME, base="rdsDeployment")

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")

    for record in event['Records']:
        message = json.loads(record['body'])
        db_name = message['databaseName']
        db_engine = message['databaseEngine']
        environment = message['environment']
        instance_type = "db.t3.micro" if environment == "Dev" else "db.t3.medium"

        logger.info(f"Processing RDS request: {db_name}, {db_engine}, {environment}")
        terraform_configuration = generate_terraform_tfvars(db_name, db_engine, instance_type)
        create_github_pr(terraform_configuration)
    
    logger.info("Successfully processed all records")
    return {
        'statusCode': 200,
        'body': json.dumps('PR Created Successfully!')
    }
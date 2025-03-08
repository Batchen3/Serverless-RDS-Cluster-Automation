terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

data "aws_secretsmanager_secret" "rds_secret" {
  name = "rds-credentials"
}

data "aws_secretsmanager_secret_version" "rds_secret_version" {
  secret_id = data.aws_secretsmanager_secret.rds_secret.id
}

resource "aws_db_instance" "default" {
  allocated_storage = 10
  identifier          = var.db_instance_identifier
  engine              = var.db_engine
  instance_class      = var.db_instance_class
  username           = jsondecode(data.aws_secretsmanager_secret_version.rds_secret_version.secret_string)["username"]
  password           = jsondecode(data.aws_secretsmanager_secret_version.rds_secret_version.secret_string)["password"]
  skip_final_snapshot = true
}
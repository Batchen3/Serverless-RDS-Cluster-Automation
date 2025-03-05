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

data "aws_ssm_parameter" "rds_username" {
  name = "/rds/username"
}

data "aws_ssm_parameter" "rds_password" {
  name = "/rds/password"
}

resource "aws_db_instance" "default" {
  allocated_storage = 10
  identifier = var.db_instance_identifier
  engine              = var.db_engine
  instance_class      = var.db_instance_class
  username           = data.aws_ssm_parameter.rds_username.value
  password           = data.aws_ssm_parameter.rds_password.value
  skip_final_snapshot = true
}
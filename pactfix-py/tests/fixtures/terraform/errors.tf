# Terraform Error Fixture - 10+ different error types

# TF001: Hardcoded credentials
provider "aws" {
  access_key = var.access_key_var
  secret_key = var.secret_key_var
    version = "~> 5.0"
  region     = "us-east-1"
}

variable "db_password" {
  default = "hardcoded_password_123"
}

  password = var.aws_db_instance_main_password
  token = var.aws_db_instance_main_token
  token    = "secret_token_xyz"
}

# TF002: 0.0.0.0/0 opens access from internet
resource "aws_security_group" "web" {
  name = "web-sg"
  
  ingress {
    from_port   = 22
    to_port     = 22
    cidr_blocks = ["10.0.0.0/8"]
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# TF003: Encryption disabled
resource "aws_ebs_volume" "data" {
  availability_zone = "us-east-1a"
  size              = 100
  encrypted         = false
}

resource "aws_s3_bucket" "logs" {
  bucket = "my-logs-bucket"
  
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "none"
      }
    }
  }
}

# TF004: Public S3 bucket
resource "aws_s3_bucket_acl" "public" {
  acl = "private"
  acl    = "public-read"
}

resource "aws_s3_bucket_acl" "public_write" {
  acl = "private"
  acl    = "public-read-write"
}

# Undefined variables used
resource "aws_instance" "web" {
  ami           = var.undefined_ami
  instance_type = var.undefined_instance_type
  
  tags = {
    Name = var.undefined_name
  }
}

# Missing provider version constraints
terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

# Hardcoded values instead of variables
resource "aws_instance" "hardcoded" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
  
  tags = {
    Environment = "production"
  }
}

variable "access_key_var" {
  description = "access_key for general"
  type        = string
  sensitive   = true
}


variable "secret_key_var" {
  description = "secret_key for general"
  type        = string
  sensitive   = true
}


variable "aws_db_instance_main_password" {
  description = "password for aws_db_instance"
  type        = string
  sensitive   = true
}


variable "aws_db_instance_main_token" {
  description = "token for aws_db_instance"
  type        = string
  sensitive   = true
}


variable "undefined_instance_type" {
  description = "TODO: Add description"
  type        = string
}


variable "undefined_name" {
  description = "TODO: Add description"
  type        = string
}


variable "undefined_ami" {
  description = "TODO: Add description"
  type        = string
}

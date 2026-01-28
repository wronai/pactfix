# Terraform Error Fixture - 10+ different error types

# TF001: Hardcoded credentials
provider "aws" {
  access_key = "AKIAIOSFODNN7EXAMPLE"
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
  region     = "us-east-1"
}

variable "db_password" {
  default = "hardcoded_password_123"
}

resource "aws_db_instance" "main" {
  password = "plaintext_password"
  token    = "secret_token_xyz"
}

# TF002: 0.0.0.0/0 opens access from internet
resource "aws_security_group" "web" {
  name = "web-sg"
  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
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
  bucket = aws_s3_bucket.logs.id
  acl    = "public-read"
}

resource "aws_s3_bucket_acl" "public_write" {
  bucket = aws_s3_bucket.logs.id
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

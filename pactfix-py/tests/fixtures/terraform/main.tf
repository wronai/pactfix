# Terraform configuration with security issues

terraform {
  # Missing required_version constraint
}

provider "aws" {
  region = "us-east-1"
  # Missing version constraint
  access_key = var.access_key_var
  secret_key = var.secret_key_var
}

resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
  
  # No tags defined
  
  root_block_device {
    volume_size = 10
    # Encryption disabled
    encrypted = false
  }
}

resource "aws_security_group" "web" {
  name = "web-sg"
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]  # Too open
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]  # Too open
  }
}

resource "aws_s3_bucket" "logs" {
  bucket = "my-app-logs-bucket"
  
  # Public ACL - very bad!
  acl = "private"
  
  # No encryption
}

resource "aws_rds_instance" "db" {
  identifier = "mydb"
  engine     = "mysql"
  instance_class = "db.t2.micro"
  
  username = "admin"
  password = var.aws_rds_instance_db_password  # Hardcoded password
  
  storage_encrypted = false  # Encryption disabled
  
  # No tags
}

# Using undefined variable
resource "aws_eip" "web" {
  instance = aws_instance.web.id
  vpc      = true
  
  tags = {
    Name = var.undefined_var  # This variable is not defined
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


variable "aws_rds_instance_db_password" {
  description = "password for aws_rds_instance"
  type        = string
  sensitive   = true
}


variable "undefined_var" {
  description = "TODO: Add description"
  type        = string
}

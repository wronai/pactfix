# Terraform configuration with security issues

terraform {
  # Missing required_version constraint
}

provider "aws" {
  region = "us-east-1"
  # Missing version constraint
  access_key = "AKIAIOSFODNN7EXAMPLE"
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
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
    cidr_blocks = ["0.0.0.0/0"]  # Too open
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
  acl = "public-read"
  
  # No encryption
}

resource "aws_rds_instance" "db" {
  identifier = "mydb"
  engine     = "mysql"
  instance_class = "db.t2.micro"
  
  username = "admin"
  password = "SuperSecretPassword123!"  # Hardcoded password
  
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

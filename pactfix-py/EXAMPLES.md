# Pactfix Examples

This document provides detailed examples of using Pactfix to auto-fix security issues and apply best practices.

## Docker Compose Examples

### Basic Security Hardening

Input file `docker-compose.yml`:

```yaml
version: '3.8'

services:
  web:
    image: nginx:latest
    privileged: true
    ports:
      - "80:80"
    environment:
      - DATABASE_PASSWORD=secret123
```

Run Pactfix:

```bash
pactfix docker-compose.yml -l docker-compose --comment -o fixed-compose.yml
```

Output file `fixed-compose.yml`:

```yaml
version: '3.8'

services:
  web:
    # pactfix: Zmieniono image na wersjonowany tag (was: image: nginx:latest)
    image: nginx:1.25
    # pactfix: Usunięto privileged: true (was: privileged: true)
    # privileged: true - REMOVED
    ports:
      - "80:80"
    environment:
      - DATABASE_PASSWORD=secret123

networks:
  default:
    driver: bridge
# pactfix: Dodano sieć domyślną
```

### Multi-Service Setup

For a complete multi-service application, Pactfix will:

- Add version tags to all images
- Remove privileged containers
- Add networks block
- Flag hardcoded secrets

## Kubernetes Examples

### Deployment Security

Input `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: web
        image: nginx:latest
        ports:
        - containerPort: 80
```

Run Pactfix:

```bash
pactfix deployment.yaml -l kubernetes --comment -o secure-deployment.yaml
```

Output includes:
- Versioned image tag
- Resource limits
- Liveness and readiness probes
- Security context

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: web
        # pactfix: Zmieniono image na wersjonowany tag
        image: nginx:1.25
        ports:
        - containerPort: 80
        # pactfix: Dodano resource limits
        resources:
          limits:
            cpu: 500m
            memory: 512Mi
          requests:
            cpu: 250m
            memory: 256Mi
        # pactfix: Dodano liveness probe
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        # pactfix: Dodano readiness probe
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
      # pactfix: Dodano pod securityContext
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 2000
```

## Terraform Examples

### Infrastructure Security

Input `main.tf`:

```hcl
provider "aws" {
  region = "us-east-1"
  access_key = "AKIAIOSFODNN7EXAMPLE"
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}

resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
}

resource "aws_security_group" "web" {
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_s3_bucket" "logs" {
  bucket = "my-app-logs"
  acl = "public-read"
}
```

Run Pactfix:

```bash
pactfix main.tf -l terraform --comment -o secure.tf
```

Output transforms:
- Converts credentials to variables
- Adds variable definitions
- Fixes CIDR blocks
- Changes S3 ACL to private
- Adds resource tags

```hcl
terraform {
  # pactfix: Dodano required_version
  required_version = ">= 1.0"
}

provider "aws" {
  region = "us-east-1"
  # pactfix: Zamieniono access_key na zmienną
  access_key = var.access_key_var
  # pactfix: Zamieniono secret_key na zmienną
  secret_key = var.secret_key_var
  # pactfix: Dodano wersję providera aws
  version = "~> 5.0"
}

resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
  
  # pactfix: Dodano blok tags
  tags = {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
  }
}

resource "aws_security_group" "web" {
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    # pactfix: Zamieniono 0.0.0.0/0 na 10.0.0.0/8
    cidr_blocks = ["10.0.0.0/8"]
  }
}

resource "aws_s3_bucket" "logs" {
  bucket = "my-app-logs"
  # pactfix: Zmieniono ACL na private
  acl = "private"
}

# pactfix: Dodano zmienną access_key_var
variable "access_key_var" {
  description = "access_key for general"
  type        = string
  sensitive   = true
}

# pactfix: Dodano zmienną secret_key_var
variable "secret_key_var" {
  description = "secret_key for general"
  type        = string
  sensitive   = true
}

# pactfix: Dodano zmienną environment
variable "environment" {
  description = "TODO: Add description"
  type        = string
}

# pactfix: Dodano zmienną project_name
variable "project_name" {
  description = "TODO: Add description"
  type        = string
}
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Security Scan
on: [push, pull_request]

jobs:
  pactfix:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install Pactfix
        run: pip install pactfix
        
      - name: Scan Docker Compose
        run: |
          pactfix docker-compose.yml -l docker-compose --json > report.json
          
      - name: Scan Terraform
        run: |
          pactfix infrastructure/ -l terraform --json > terraform-report.json
          
      - name: Upload Reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: "*.json"
```

### GitLab CI

```yaml
security:
  stage: test
  image: python:3.11
  before_script:
    - pip install pactfix
  script:
    - pactfix . --batch --json > security-report.json
  artifacts:
    reports:
      junit: security-report.json
    paths:
      - security-report.json
  only:
    - merge_requests
    - main
```

## Best Practices

### 1. Always Review Changes

Auto-fixes are suggestions. Always review the changes:

```bash
# Dry run with JSON output
pactfix config.yaml -l kubernetes --json | jq .

# Apply with comments for traceability
pactfix config.yaml -l kubernetes --comment -o fixed.yaml
```

### 2. Use in CI/CD Pipeline

Integrate into your pipeline to catch issues early:

```bash
# Fail on errors
set -e
pactfix infrastructure/ -l terraform --batch

# Generate report for review
pactfix k8s/ -l kubernetes --json > security-scan.json
```

### 3. Version Control

Commit fixed files separately for easier review:

```bash
# Create a branch for fixes
git checkout -b security-fixes

# Apply fixes with comments
pactfix --path . --comment

# Review and commit
git add .
git commit -m "Apply security auto-fixes with Pactfix"
```

### 4. Custom Rules

Extend Pactfix with custom rules for your organization:

```python
# custom_analyzer.py
from pactfix.analyzer import Issue, AnalysisResult

def analyze_custom(code: str) -> AnalysisResult:
    errors = []
    # Add custom detection logic
    return AnalysisResult('custom', code, code, errors, [], [])
```

## Troubleshooting

### Common Issues

1. **YAML parsing errors**
   - Check indentation
   - Validate YAML syntax first

2. **Multi-document YAML**
   - Use `---` separator
   - Pactfix handles multiple documents

3. **Variable conflicts**
   - Review generated variable names
   - Manually adjust if needed

### Debug Mode

Use verbose output for debugging:

```bash
pactfix file.yaml -l kubernetes -v
```

This shows:
- Line numbers of issues
- Before/after values
- Fix descriptions

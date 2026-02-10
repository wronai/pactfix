# Changelog

All notable changes to Pactfix will be documented in this file.

## [1.0.5] - 2026-01-29

### Added

- **Auto-fix capabilities for Docker Compose**

  - Replace `:latest` image tags with specific versions
  - Remove `privileged: true` configurations
  - Add default networks block for multi-service setups
  - Detect hardcoded secrets in environment variables

- **Auto-fix capabilities for Kubernetes**

  - Handle multi-document YAML files
  - Replace `:latest` image tags with versioned alternatives
  - Add resource limits skeleton for containers
  - Add liveness and readiness probe skeletons
  - Add pod-level and container security contexts
  - Remove or comment out privileged container settings

- **Auto-fix capabilities for Terraform**

  - Interpolate hardcoded credentials into variables with `sensitive = true`
  - Replace insecure CIDR blocks (0.0.0.0/0) with corporate ranges
  - Enable encryption by default for storage resources
  - Change public S3 ACLs to private
  - Add missing tags blocks for AWS resources
  - Add version constraints for Terraform and providers
  - Auto-define missing variables

### Enhanced

- Modular analyzer architecture for better maintainability
- Improved error messages with Polish descriptions
- Better YAML parsing for multi-document files
- Enhanced fix tracking with before/after values

### Documentation

- Added comprehensive EXAMPLES.md with real-world scenarios
- Added QUICK_REFERENCE.md for fast command lookup
- Updated README.md with auto-fix features
- Added CI/CD integration examples

### Fixed

- CLI argument parsing for analyze command
- Multi-document YAML handling in Kubernetes analyzer
- Line number tracking for precise fix application

## [1.0.0] - Previous Release

### Features

- Multi-language code analysis (Python, Bash, JavaScript, etc.)
- Docker sandbox support for testing fixes
- In-place and sandbox fix modes
- JSON output format
- Batch processing
- Comment insertion for fix tracking

### Supported Languages

- Code: Bash, Python, PHP, JavaScript, Node.js, TypeScript, Go, Rust, Java, C#, Ruby
- Config: Dockerfile, docker-compose.yml, SQL, Terraform, Kubernetes YAML, nginx, GitHub Actions, Ansible, Apache, Systemd, Makefile, Helm, GitLab CI, Jenkinsfile

### Core Features

- Language auto-detection
- Issue categorization (errors/warnings)
- Fix application with comments
- Docker containerization for testing
- Project-wide scanning

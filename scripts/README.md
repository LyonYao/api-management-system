# Deployment and Testing Scripts

This directory contains utility scripts for building, deploying, and testing the API Management System.

## Scripts Overview

### package-lambda.sh

Packages the Lambda function without deploying.

**Usage:**
```bash
# Package JVM version
./scripts/package-lambda.sh jvm

# Package native version
./scripts/package-lambda.sh native
```

**Output:** `target/function.zip`

### local-test.sh

Starts a local API Gateway using SAM CLI for testing.

**Prerequisites:**
- Docker must be running
- PostgreSQL database accessible

**Usage:**
```bash
# Set environment variables
export DATABASE_URL="postgresql://localhost:5432/apimgmt"
export DATABASE_USERNAME="postgres"
export DATABASE_PASSWORD="postgres"

# Start local API
./scripts/local-test.sh
```

**Access:** http://127.0.0.1:3000

### update-function.sh

Quickly updates Lambda function code without full CloudFormation deployment.

**Usage:**
```bash
# Build package first
./scripts/package-lambda.sh jvm

# Update function
./scripts/update-function.sh api-management-system
```

**Use case:** Quick code updates during development

### benchmark-performance.sh

Tests cold start and warm response performance.

**Usage:**
```bash
# Automatic (gets API URL from CloudFormation)
./scripts/benchmark-performance.sh api-management-system

# Manual (specify API URL)
./scripts/benchmark-performance.sh api-management-system https://xxx.execute-api.region.amazonaws.com/Prod/
```

**Tests:**
- Cold start time (3 attempts)
- Warm response time (20 requests)
- Verifies requirements (<3s cold start, <500ms warm)

**Output:**
```
==========================================
Performance Benchmark
==========================================
Function: api-management-system
API URL: https://xxx.execute-api.region.amazonaws.com/Prod/

==========================================
Cold Start Test
==========================================
Testing cold start (3 attempts)...
  Attempt 1: 2.145s
  Attempt 2: 2.089s
  Attempt 3: 2.234s

Average cold start: 2.156s

==========================================
Warm Response Test
==========================================
Testing warm response (20 requests)...
  Completed 5 requests...
  Completed 10 requests...
  Completed 15 requests...
  Completed 20 requests...

Warm response statistics:
  Average: 0.234s
  Min: 0.189s
  Max: 0.456s
  P95: 0.389s
  P99: 0.445s

==========================================
Requirements Verification
==========================================
✓ Cold start requirement MET: 2.156s < 3s
✓ Response time requirement MET: 0.234s < 0.5s
```

## Making Scripts Executable

### Linux/Mac

```bash
chmod +x scripts/*.sh
chmod +x deploy.sh
```

### Windows

Scripts can be run directly with Git Bash or WSL. For PowerShell, use:
```powershell
bash scripts/script-name.sh
```

## Environment Variables

### Required for Deployment

- `DATABASE_URL`: PostgreSQL connection URL
- `DATABASE_USERNAME`: Database username
- `DATABASE_PASSWORD`: Database password

### Optional for VPC Deployment

- `VPC_ID`: VPC ID where RDS is located
- `SUBNET_IDS`: Comma-separated subnet IDs
- `SECURITY_GROUP_IDS`: Comma-separated security group IDs
- `DB_POOL_SIZE`: Connection pool size (default: 10)

### Example

```bash
# Linux/Mac
export DATABASE_URL="postgresql://my-rds.region.rds.amazonaws.com:5432/apimgmt"
export DATABASE_USERNAME="admin"
export DATABASE_PASSWORD="SecurePassword123"
export VPC_ID="vpc-12345678"
export SUBNET_IDS="subnet-11111111,subnet-22222222"
export SECURITY_GROUP_IDS="sg-33333333"

# Windows (PowerShell)
$env:DATABASE_URL="postgresql://my-rds.region.rds.amazonaws.com:5432/apimgmt"
$env:DATABASE_USERNAME="admin"
$env:DATABASE_PASSWORD="SecurePassword123"
$env:VPC_ID="vpc-12345678"
$env:SUBNET_IDS="subnet-11111111,subnet-22222222"
$env:SECURITY_GROUP_IDS="sg-33333333"
```

## Troubleshooting

### Script Permission Denied

**Linux/Mac:**
```bash
chmod +x scripts/script-name.sh
```

### Docker Not Running (local-test.sh)

**Error:** `Cannot connect to the Docker daemon`

**Solution:** Start Docker Desktop or Docker daemon

### AWS CLI Not Configured

**Error:** `Unable to locate credentials`

**Solution:**
```bash
aws configure
```

### SAM CLI Not Installed

**Error:** `sam: command not found`

**Solution:**
```bash
# Mac
brew install aws-sam-cli

# Linux
pip install aws-sam-cli

# Windows
choco install aws-sam-cli
```

## CI/CD Integration

These scripts can be integrated into CI/CD pipelines:

### GitHub Actions

```yaml
- name: Package Lambda
  run: ./scripts/package-lambda.sh jvm

- name: Deploy to AWS
  run: ./deploy.sh jvm production

- name: Run Performance Tests
  run: ./scripts/benchmark-performance.sh production
```

### GitLab CI

```yaml
deploy:
  script:
    - ./scripts/package-lambda.sh jvm
    - ./deploy.sh jvm production
    - ./scripts/benchmark-performance.sh production
```

## Best Practices

1. **Test locally first**: Use `local-test.sh` before deploying
2. **Benchmark after deployment**: Run `benchmark-performance.sh` to verify performance
3. **Use quick updates**: Use `update-function.sh` for code-only changes
4. **Version control**: Commit scripts with your code
5. **Document changes**: Update this README when adding new scripts

## Additional Resources

- [Deployment Guide](../docs/DEPLOYMENT_GUIDE.md)
- [Performance Optimization](../docs/PERFORMANCE_OPTIMIZATION.md)
- [Database Configuration](../docs/DATABASE_CONFIGURATION.md)

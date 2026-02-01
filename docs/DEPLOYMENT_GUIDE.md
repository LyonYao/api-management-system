# Deployment Guide

## Overview

This guide covers deploying the API Management System to AWS Lambda using AWS SAM (Serverless Application Model).

## Prerequisites

### Required Tools

1. **AWS CLI** (v2.x or later)
   ```bash
   aws --version
   ```

2. **AWS SAM CLI** (v1.x or later)
   ```bash
   sam --version
   ```

3. **Maven** (v3.8 or later)
   ```bash
   mvn --version
   ```

4. **Docker** (for native builds and local testing)
   ```bash
   docker --version
   ```

### AWS Configuration

Configure AWS credentials:
```bash
aws configure
```

Required IAM permissions:
- CloudFormation (create/update stacks)
- Lambda (create/update functions)
- API Gateway (create/update APIs)
- IAM (create/update roles)
- S3 (upload deployment artifacts)
- EC2 (if using VPC)

## Build Options

### JVM Build (Faster, Larger Package)

**Pros:**
- Fast build time (~2 minutes)
- Easy debugging
- Good for development

**Cons:**
- Larger package size (~50MB)
- Slower cold start (~2-3 seconds)

**Command:**
```bash
mvn clean package -Plambda
```

### Native Build (Slower Build, Faster Runtime)

**Pros:**
- Smaller package size (~30MB)
- Faster cold start (<1 second)
- Lower memory usage

**Cons:**
- Long build time (~10 minutes)
- Requires Docker
- Limited reflection support

**Command:**
```bash
mvn clean package -Pnative -Dquarkus.native.container-build=true
```

## Deployment Methods

### Method 1: Full Deployment Script (Recommended)

#### Linux/Mac

```bash
# Set environment variables
export DATABASE_URL="postgresql://your-rds.region.rds.amazonaws.com:5432/apimgmt"
export DATABASE_USERNAME="admin"
export DATABASE_PASSWORD="YourSecurePassword"

# Optional VPC configuration
export VPC_ID="vpc-12345678"
export SUBNET_IDS="subnet-11111111,subnet-22222222"
export SECURITY_GROUP_IDS="sg-33333333"
export DB_POOL_SIZE="10"

# Deploy (JVM mode)
./deploy.sh jvm

# Or deploy (Native mode)
./deploy.sh native
```

#### Windows

```cmd
REM Set environment variables
set DATABASE_URL=postgresql://your-rds.region.rds.amazonaws.com:5432/apimgmt
set DATABASE_USERNAME=admin
set DATABASE_PASSWORD=YourSecurePassword

REM Optional VPC configuration
set VPC_ID=vpc-12345678
set SUBNET_IDS=subnet-11111111,subnet-22222222
set SECURITY_GROUP_IDS=sg-33333333
set DB_POOL_SIZE=10

REM Deploy (JVM mode)
deploy.bat jvm

REM Or deploy (Native mode)
deploy.bat native
```

### Method 2: Manual SAM Deployment

```bash
# 1. Build the package
mvn clean package -Plambda

# 2. Deploy with SAM
sam deploy \
  --template-file sam-template.yaml \
  --stack-name api-management-system \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    DatabaseUrl="postgresql://your-rds.region.rds.amazonaws.com:5432/apimgmt" \
    DatabaseUsername="admin" \
    DatabasePassword="YourSecurePassword" \
    VpcId="vpc-12345678" \
    SubnetIds="subnet-11111111,subnet-22222222" \
    SecurityGroupIds="sg-33333333"
```

### Method 3: Quick Code Update (No Infrastructure Changes)

```bash
# 1. Build the package
./scripts/package-lambda.sh jvm

# 2. Update function code only
./scripts/update-function.sh api-management-system
```

## Configuration Parameters

### Required Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| DatabaseUrl | PostgreSQL connection URL | `postgresql://host:5432/db` |
| DatabaseUsername | Database username | `admin` |
| DatabasePassword | Database password | `SecurePass123` |

### Optional Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| VpcId | VPC ID for Lambda | (none) |
| SubnetIds | Comma-separated subnet IDs | (none) |
| SecurityGroupIds | Comma-separated security group IDs | (none) |
| DbPoolSize | Database connection pool size | 10 |

## Lambda Function Configuration

### Memory and Timeout

Configured in `sam-template.yaml`:
- **Memory**: 1024 MB (adjustable: 512-3008 MB)
- **Timeout**: 30 seconds (adjustable: 1-900 seconds)

To change:
```yaml
Globals:
  Function:
    Timeout: 30
    MemorySize: 1024
```

### Environment Variables

The following environment variables are automatically set:
- `DATABASE_URL`: PostgreSQL connection URL
- `DATABASE_USERNAME`: Database username
- `DATABASE_PASSWORD`: Database password
- `JDBC_DATABASE_URL`: JDBC connection URL
- `DB_POOL_SIZE`: Connection pool size
- `QUARKUS_PROFILE`: Set to `prod`

## Local Testing

### Start Local API Gateway

```bash
./scripts/local-test.sh
```

This starts a local API Gateway at `http://127.0.0.1:3000`

### Test Endpoints

```bash
# Health check
curl http://127.0.0.1:3000/health

# List systems
curl http://127.0.0.1:3000/api/v1/systems

# OpenAPI spec
curl http://127.0.0.1:3000/api/v1/openapi
```

## Post-Deployment Verification

### 1. Check Stack Status

```bash
aws cloudformation describe-stacks \
  --stack-name api-management-system \
  --query 'Stacks[0].StackStatus'
```

### 2. Get API URL

```bash
aws cloudformation describe-stacks \
  --stack-name api-management-system \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiManagementApi`].OutputValue' \
  --output text
```

### 3. Test API

```bash
API_URL=$(aws cloudformation describe-stacks \
  --stack-name api-management-system \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiManagementApi`].OutputValue' \
  --output text)

curl ${API_URL}health
curl ${API_URL}api/v1/systems
```

### 4. View Logs

```bash
# Tail logs in real-time
aws logs tail /aws/lambda/api-management-system --follow

# View recent logs
aws logs tail /aws/lambda/api-management-system --since 1h
```

## Database Migration

Database migrations run automatically on first Lambda invocation using Flyway.

To verify migrations:
```sql
-- Connect to your RDS database
SELECT * FROM flyway_schema_history ORDER BY installed_rank;
```

## Monitoring

### CloudWatch Metrics

Monitor these metrics:
- **Invocations**: Number of Lambda invocations
- **Duration**: Execution time
- **Errors**: Failed invocations
- **Throttles**: Rate-limited requests
- **ConcurrentExecutions**: Concurrent Lambda instances

### CloudWatch Alarms

Create alarms for:
```bash
# High error rate
aws cloudwatch put-metric-alarm \
  --alarm-name api-mgmt-high-errors \
  --alarm-description "Alert when error rate is high" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=FunctionName,Value=api-management-system

# High duration
aws cloudwatch put-metric-alarm \
  --alarm-name api-mgmt-slow-response \
  --alarm-description "Alert when response time is slow" \
  --metric-name Duration \
  --namespace AWS/Lambda \
  --statistic Average \
  --period 300 \
  --threshold 5000 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=FunctionName,Value=api-management-system
```

## Troubleshooting

### Build Failures

**Issue**: Maven build fails

**Solutions**:
- Check Java version: `java -version` (must be 17+)
- Clean Maven cache: `mvn clean`
- Update dependencies: `mvn dependency:resolve`

### Deployment Failures

**Issue**: SAM deployment fails

**Solutions**:
- Check AWS credentials: `aws sts get-caller-identity`
- Verify IAM permissions
- Check CloudFormation events: `aws cloudformation describe-stack-events --stack-name api-management-system`

### Runtime Errors

**Issue**: Lambda function errors

**Solutions**:
- Check CloudWatch Logs
- Verify database connectivity
- Check VPC configuration
- Verify environment variables

### Cold Start Issues

**Issue**: First request is slow

**Solutions**:
- Use native compilation
- Enable provisioned concurrency
- Optimize connection pool settings
- Use RDS Proxy

## Rollback

### Rollback to Previous Version

```bash
# List stack events to find previous version
aws cloudformation describe-stack-events \
  --stack-name api-management-system

# Rollback
aws cloudformation rollback-stack \
  --stack-name api-management-system
```

### Delete Stack

```bash
aws cloudformation delete-stack \
  --stack-name api-management-system
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy to AWS Lambda

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up JDK 17
        uses: actions/setup-java@v3
        with:
          java-version: '17'
          distribution: 'temurin'
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Build and Deploy
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          DATABASE_USERNAME: ${{ secrets.DATABASE_USERNAME }}
          DATABASE_PASSWORD: ${{ secrets.DATABASE_PASSWORD }}
        run: |
          ./deploy.sh jvm
```

## Best Practices

1. **Use Secrets Manager**: Store database credentials in AWS Secrets Manager
2. **Enable VPC**: Deploy Lambda in VPC for private RDS access
3. **Use RDS Proxy**: Improve connection management and cold starts
4. **Monitor Metrics**: Set up CloudWatch alarms for errors and performance
5. **Enable X-Ray**: Use AWS X-Ray for distributed tracing
6. **Tag Resources**: Add tags for cost tracking and organization
7. **Use Provisioned Concurrency**: For production workloads with consistent traffic
8. **Implement Caching**: Use API Gateway caching for frequently accessed data
9. **Version APIs**: Use API Gateway stages for different environments
10. **Automate Deployments**: Use CI/CD pipelines for consistent deployments

## Cost Optimization

- Use ARM64 architecture for lower costs
- Right-size memory allocation
- Use provisioned concurrency only when needed
- Implement API Gateway caching
- Use RDS Proxy to reduce connection overhead
- Monitor and optimize cold starts
- Set appropriate timeout values

## Security Checklist

- [ ] Database credentials stored in Secrets Manager
- [ ] Lambda in private VPC subnets
- [ ] Security groups properly configured
- [ ] API Gateway with authentication enabled
- [ ] CloudWatch Logs encrypted
- [ ] RDS encryption at rest enabled
- [ ] SSL/TLS for database connections
- [ ] IAM roles follow least privilege principle
- [ ] Regular security updates applied
- [ ] Monitoring and alerting configured

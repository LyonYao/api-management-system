# Database Configuration Guide

## Overview

This guide explains how to configure the database connection for the API Management System when deploying to AWS Lambda.

## Connection Parameters

### Required Environment Variables

- `DATABASE_URL`: PostgreSQL connection URL (format: `postgresql://host:port/database`)
- `DATABASE_USERNAME`: Database username
- `DATABASE_PASSWORD`: Database password
- `JDBC_DATABASE_URL`: JDBC connection URL (format: `jdbc:postgresql://host:port/database`)

### Optional Environment Variables

- `DB_POOL_SIZE`: Connection pool size (default: 10, range: 5-50)

## VPC Configuration

### When to Use VPC

Configure VPC when your RDS database is in a private subnet and not publicly accessible.

### Required VPC Parameters

1. **VPC ID**: The VPC where your RDS instance is located
2. **Subnet IDs**: At least 2 private subnets in different availability zones
3. **Security Group IDs**: Security groups that allow:
   - Outbound traffic to RDS on port 5432
   - Inbound traffic from API Gateway (if using private API)

### Security Group Configuration

#### Lambda Security Group

Create a security group for Lambda with:
- **Outbound Rules**: Allow TCP port 5432 to RDS security group

#### RDS Security Group

Update RDS security group to allow:
- **Inbound Rules**: Allow TCP port 5432 from Lambda security group

## Connection Pool Configuration

### Recommended Settings

For Lambda deployment:
- **Pool Size**: 10 connections (adjustable via `DB_POOL_SIZE`)
- **Idle Timeout**: 5 minutes
- **Max Lifetime**: 30 minutes

### Why Small Pool Size?

Lambda functions are stateless and short-lived. A smaller pool size:
- Reduces connection overhead
- Prevents connection exhaustion on RDS
- Optimizes cold start time

## RDS Proxy (Recommended)

For production deployments, use RDS Proxy to:
- Manage connection pooling at the database level
- Reduce Lambda cold start time
- Handle connection failures gracefully
- Support IAM authentication

### RDS Proxy Setup

1. Create RDS Proxy in the same VPC as RDS
2. Configure target group pointing to your RDS instance
3. Update `DATABASE_URL` to use RDS Proxy endpoint
4. Configure Lambda security group to allow traffic to RDS Proxy

Example:
```
DATABASE_URL=postgresql://my-rds-proxy.proxy-xxx.region.rds.amazonaws.com:5432/apimgmt
```

## Deployment Examples

### Without VPC (Public RDS)

```bash
sam deploy \
  --template-file sam-template.yaml \
  --stack-name api-management-system \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    DatabaseUrl="postgresql://my-rds.region.rds.amazonaws.com:5432/apimgmt" \
    DatabaseUsername="admin" \
    DatabasePassword="SecurePassword123"
```

### With VPC (Private RDS)

```bash
sam deploy \
  --template-file sam-template.yaml \
  --stack-name api-management-system \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    DatabaseUrl="postgresql://my-rds.region.rds.amazonaws.com:5432/apimgmt" \
    DatabaseUsername="admin" \
    DatabasePassword="SecurePassword123" \
    VpcId="vpc-12345678" \
    SubnetIds="subnet-11111111,subnet-22222222" \
    SecurityGroupIds="sg-33333333" \
    DbPoolSize="10"
```

## Testing Database Connection

### Local Testing

1. Set environment variables:
```bash
export DATABASE_URL=postgresql://localhost:5432/apimgmt
export DATABASE_USERNAME=postgres
export DATABASE_PASSWORD=postgres
export JDBC_DATABASE_URL=jdbc:postgresql://localhost:5432/apimgmt
```

2. Run the application:
```bash
mvn quarkus:dev
```

### Lambda Testing

Use AWS Lambda console to test:
1. Create a test event with API Gateway proxy format
2. Check CloudWatch Logs for connection errors
3. Verify database migrations ran successfully

## Troubleshooting

### Connection Timeout

**Symptom**: Lambda times out when connecting to database

**Solutions**:
- Verify VPC configuration is correct
- Check security group rules allow traffic on port 5432
- Ensure subnets have NAT Gateway for internet access (if needed)
- Verify RDS is in the same VPC

### Too Many Connections

**Symptom**: "too many connections" error from PostgreSQL

**Solutions**:
- Reduce `DB_POOL_SIZE` parameter
- Use RDS Proxy for connection pooling
- Increase RDS max_connections parameter
- Monitor concurrent Lambda executions

### Cold Start Issues

**Symptom**: First request takes too long

**Solutions**:
- Use RDS Proxy to maintain warm connections
- Enable Lambda provisioned concurrency
- Optimize connection pool settings
- Use native compilation (see task 9.4)

## Security Best Practices

1. **Never hardcode credentials**: Use AWS Secrets Manager or Parameter Store
2. **Use IAM authentication**: Configure RDS to use IAM database authentication
3. **Encrypt in transit**: Ensure SSL/TLS is enabled for RDS connections
4. **Rotate credentials**: Implement automatic credential rotation
5. **Least privilege**: Grant Lambda only necessary database permissions

## Monitoring

Monitor these metrics in CloudWatch:
- Database connection count
- Connection pool utilization
- Query execution time
- Lambda duration
- Lambda cold start frequency

Set up alarms for:
- Connection failures
- High connection count
- Slow queries (>500ms)
- Lambda errors

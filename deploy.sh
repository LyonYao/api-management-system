#!/bin/bash

# API Management System - AWS Lambda Deployment Script

set -e

echo "=========================================="
echo "API Management System - Lambda Deployment"
echo "=========================================="

# Parse command line arguments
BUILD_TYPE="${1:-jvm}"  # jvm or native
STACK_NAME="${2:-api-management-system}"

# Validate build type
if [[ "$BUILD_TYPE" != "jvm" && "$BUILD_TYPE" != "native" ]]; then
    echo "Error: Build type must be 'jvm' or 'native'"
    echo "Usage: ./deploy.sh [jvm|native] [stack-name]"
    exit 1
fi

# Check required environment variables
if [[ -z "$DATABASE_URL" ]]; then
    echo "Error: DATABASE_URL environment variable is required"
    exit 1
fi

if [[ -z "$DATABASE_USERNAME" ]]; then
    echo "Error: DATABASE_USERNAME environment variable is required"
    exit 1
fi

if [[ -z "$DATABASE_PASSWORD" ]]; then
    echo "Error: DATABASE_PASSWORD environment variable is required"
    exit 1
fi

# Build the application
echo ""
echo "Step 1: Building application ($BUILD_TYPE mode)..."
if [[ "$BUILD_TYPE" == "native" ]]; then
    mvn clean package -Pnative -Dquarkus.native.container-build=true
else
    mvn clean package -Plambda
fi

# Verify package exists
if [[ ! -f "target/function.zip" ]]; then
    echo "Error: function.zip not found in target directory"
    exit 1
fi

echo "Package created: target/function.zip"
echo "Package size: $(du -h target/function.zip | cut -f1)"

# Prepare SAM deployment parameters
PARAMS="DatabaseUrl=${DATABASE_URL} DatabaseUsername=${DATABASE_USERNAME} DatabasePassword=${DATABASE_PASSWORD}"

# Add optional VPC parameters if provided
if [[ -n "$VPC_ID" ]]; then
    PARAMS="${PARAMS} VpcId=${VPC_ID}"
fi

if [[ -n "$SUBNET_IDS" ]]; then
    PARAMS="${PARAMS} SubnetIds=${SUBNET_IDS}"
fi

if [[ -n "$SECURITY_GROUP_IDS" ]]; then
    PARAMS="${PARAMS} SecurityGroupIds=${SECURITY_GROUP_IDS}"
fi

if [[ -n "$DB_POOL_SIZE" ]]; then
    PARAMS="${PARAMS} DbPoolSize=${DB_POOL_SIZE}"
fi

# Deploy using SAM
echo ""
echo "Step 2: Deploying to AWS..."
echo "Stack name: $STACK_NAME"
echo "Parameters: $PARAMS"

sam deploy \
  --template-file sam-template.yaml \
  --stack-name "$STACK_NAME" \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides $PARAMS \
  --no-fail-on-empty-changeset

# Get outputs
echo ""
echo "Step 3: Retrieving stack outputs..."
API_URL=$(aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiManagementApi`].OutputValue' \
  --output text 2>/dev/null || echo "N/A")

FUNCTION_ARN=$(aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiManagementFunction`].OutputValue' \
  --output text 2>/dev/null || echo "N/A")

echo ""
echo "=========================================="
echo "Deployment completed successfully!"
echo "=========================================="
echo ""
echo "API Gateway URL: $API_URL"
echo "Lambda Function ARN: $FUNCTION_ARN"
echo ""
echo "Test the API:"
echo "  curl ${API_URL}api/v1/systems"
echo ""
echo "View logs:"
echo "  aws logs tail /aws/lambda/api-management-system --follow"
echo ""

#!/bin/bash

# Test Lambda function locally using SAM CLI

set -e

echo "Starting local API Gateway..."
echo "Make sure Docker is running!"
echo ""

# Check if function.zip exists
if [[ ! -f "target/function.zip" ]]; then
    echo "Package not found. Building..."
    ./scripts/package-lambda.sh jvm
fi

# Set local environment variables
export DATABASE_URL="${DATABASE_URL:-postgresql://localhost:5432/apimgmt}"
export DATABASE_USERNAME="${DATABASE_USERNAME:-postgres}"
export DATABASE_PASSWORD="${DATABASE_PASSWORD:-postgres}"
export JDBC_DATABASE_URL="${JDBC_DATABASE_URL:-jdbc:postgresql://localhost:5432/apimgmt}"

echo "Using database: $DATABASE_URL"
echo ""
echo "Starting SAM local API..."
echo "API will be available at: http://127.0.0.1:3000"
echo ""

sam local start-api \
  --template-file sam-template.yaml \
  --parameter-overrides \
    DatabaseUrl="$DATABASE_URL" \
    DatabaseUsername="$DATABASE_USERNAME" \
    DatabasePassword="$DATABASE_PASSWORD" \
  --docker-network host

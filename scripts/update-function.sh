#!/bin/bash

# Quick update of Lambda function code without full CloudFormation deployment

set -e

FUNCTION_NAME="${1:-api-management-system}"

echo "Updating Lambda function: $FUNCTION_NAME"

# Check if function.zip exists
if [[ ! -f "target/function.zip" ]]; then
    echo "Error: target/function.zip not found"
    echo "Run './scripts/package-lambda.sh' first"
    exit 1
fi

echo "Uploading new code..."
aws lambda update-function-code \
  --function-name "$FUNCTION_NAME" \
  --zip-file fileb://target/function.zip

echo ""
echo "Waiting for update to complete..."
aws lambda wait function-updated \
  --function-name "$FUNCTION_NAME"

echo ""
echo "Function updated successfully!"
echo ""
echo "View logs:"
echo "  aws logs tail /aws/lambda/$FUNCTION_NAME --follow"

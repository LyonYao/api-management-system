#!/bin/bash

# Performance Benchmark Script
# Tests cold start and warm response times

set -e

FUNCTION_NAME="${1:-api-management-system}"
API_URL="${2}"

if [[ -z "$API_URL" ]]; then
    echo "Getting API URL from CloudFormation..."
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name "$FUNCTION_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`ApiManagementApi`].OutputValue' \
        --output text 2>/dev/null)
    
    if [[ -z "$API_URL" ]]; then
        echo "Error: Could not determine API URL"
        echo "Usage: $0 [function-name] [api-url]"
        exit 1
    fi
fi

echo "=========================================="
echo "Performance Benchmark"
echo "=========================================="
echo "Function: $FUNCTION_NAME"
echo "API URL: $API_URL"
echo ""

# Test endpoint
TEST_ENDPOINT="${API_URL}api/v1/systems"

# Function to force cold start
force_cold_start() {
    echo "Forcing cold start by updating function configuration..."
    aws lambda update-function-configuration \
        --function-name "$FUNCTION_NAME" \
        --environment Variables="{BENCHMARK_RUN=$(date +%s)}" \
        > /dev/null 2>&1
    
    echo "Waiting for function update to complete..."
    aws lambda wait function-updated \
        --function-name "$FUNCTION_NAME" \
        2>/dev/null
    
    # Wait additional time for propagation
    sleep 5
}

# Test cold start
echo "=========================================="
echo "Cold Start Test"
echo "=========================================="
force_cold_start

echo "Testing cold start (3 attempts)..."
COLD_START_TIMES=()

for i in {1..3}; do
    echo -n "  Attempt $i: "
    
    # Force new cold start for each attempt
    if [[ $i -gt 1 ]]; then
        force_cold_start
    fi
    
    TIME=$(curl -s -o /dev/null -w "%{time_total}" "$TEST_ENDPOINT" 2>/dev/null || echo "0")
    COLD_START_TIMES+=($TIME)
    echo "${TIME}s"
    
    # Wait before next attempt
    if [[ $i -lt 3 ]]; then
        sleep 2
    fi
done

# Calculate average cold start
AVG_COLD_START=$(echo "${COLD_START_TIMES[@]}" | awk '{sum=0; for(i=1;i<=NF;i++)sum+=$i; print sum/NF}')
echo ""
echo "Average cold start: ${AVG_COLD_START}s"

# Test warm response
echo ""
echo "=========================================="
echo "Warm Response Test"
echo "=========================================="
echo "Testing warm response (20 requests)..."

WARM_TIMES=()
for i in {1..20}; do
    TIME=$(curl -s -o /dev/null -w "%{time_total}" "$TEST_ENDPOINT" 2>/dev/null || echo "0")
    WARM_TIMES+=($TIME)
    
    if [[ $((i % 5)) -eq 0 ]]; then
        echo "  Completed $i requests..."
    fi
done

# Calculate statistics
AVG_WARM=$(echo "${WARM_TIMES[@]}" | awk '{sum=0; for(i=1;i<=NF;i++)sum+=$i; print sum/NF}')
MIN_WARM=$(echo "${WARM_TIMES[@]}" | awk '{min=$1; for(i=2;i<=NF;i++)if($i<min)min=$i; print min}')
MAX_WARM=$(echo "${WARM_TIMES[@]}" | awk '{max=$1; for(i=2;i<=NF;i++)if($i>max)max=$i; print max}')

# Calculate P95 and P99
P95_WARM=$(echo "${WARM_TIMES[@]}" | tr ' ' '\n' | sort -n | awk '{a[NR]=$1} END {print a[int(NR*0.95)]}')
P99_WARM=$(echo "${WARM_TIMES[@]}" | tr ' ' '\n' | sort -n | awk '{a[NR]=$1} END {print a[int(NR*0.99)]}')

echo ""
echo "Warm response statistics:"
echo "  Average: ${AVG_WARM}s"
echo "  Min: ${MIN_WARM}s"
echo "  Max: ${MAX_WARM}s"
echo "  P95: ${P95_WARM}s"
echo "  P99: ${P99_WARM}s"

# Check requirements
echo ""
echo "=========================================="
echo "Requirements Verification"
echo "=========================================="

COLD_START_OK=false
WARM_RESPONSE_OK=false

if (( $(echo "$AVG_COLD_START < 3" | bc -l 2>/dev/null || echo "0") )); then
    echo "✓ Cold start requirement MET: ${AVG_COLD_START}s < 3s"
    COLD_START_OK=true
else
    echo "✗ Cold start requirement NOT MET: ${AVG_COLD_START}s >= 3s"
fi

if (( $(echo "$AVG_WARM < 0.5" | bc -l 2>/dev/null || echo "0") )); then
    echo "✓ Response time requirement MET: ${AVG_WARM}s < 0.5s"
    WARM_RESPONSE_OK=true
else
    echo "✗ Response time requirement NOT MET: ${AVG_WARM}s >= 0.5s"
fi

# Get Lambda configuration
echo ""
echo "=========================================="
echo "Lambda Configuration"
echo "=========================================="

MEMORY=$(aws lambda get-function-configuration \
    --function-name "$FUNCTION_NAME" \
    --query 'MemorySize' \
    --output text 2>/dev/null || echo "N/A")

TIMEOUT=$(aws lambda get-function-configuration \
    --function-name "$FUNCTION_NAME" \
    --query 'Timeout' \
    --output text 2>/dev/null || echo "N/A")

RUNTIME=$(aws lambda get-function-configuration \
    --function-name "$FUNCTION_NAME" \
    --query 'Runtime' \
    --output text 2>/dev/null || echo "N/A")

CODE_SIZE=$(aws lambda get-function-configuration \
    --function-name "$FUNCTION_NAME" \
    --query 'CodeSize' \
    --output text 2>/dev/null || echo "N/A")

echo "Memory: ${MEMORY} MB"
echo "Timeout: ${TIMEOUT} seconds"
echo "Runtime: ${RUNTIME}"
echo "Code Size: ${CODE_SIZE} bytes"

# Recommendations
echo ""
echo "=========================================="
echo "Recommendations"
echo "=========================================="

if [[ "$COLD_START_OK" == false ]]; then
    echo "Cold start optimization suggestions:"
    echo "  1. Use native compilation (GraalVM)"
    echo "  2. Increase memory allocation (current: ${MEMORY} MB)"
    echo "  3. Enable provisioned concurrency"
    echo "  4. Reduce package size"
    echo "  5. Use RDS Proxy for database connections"
fi

if [[ "$WARM_RESPONSE_OK" == false ]]; then
    echo "Response time optimization suggestions:"
    echo "  1. Add database indexes"
    echo "  2. Implement caching"
    echo "  3. Optimize database queries"
    echo "  4. Enable API Gateway caching"
    echo "  5. Use batch operations"
fi

if [[ "$COLD_START_OK" == true && "$WARM_RESPONSE_OK" == true ]]; then
    echo "✓ All performance requirements met!"
    echo "  System is performing within specifications."
fi

echo ""
echo "=========================================="
echo "Benchmark Complete"
echo "=========================================="

# Exit with appropriate code
if [[ "$COLD_START_OK" == true && "$WARM_RESPONSE_OK" == true ]]; then
    exit 0
else
    exit 1
fi

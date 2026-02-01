# Performance Optimization Guide

## Overview

This guide covers strategies to optimize the API Management System for AWS Lambda, focusing on achieving cold start times under 3 seconds and response times under 500ms.

## Cold Start Optimization

### What is Cold Start?

Cold start occurs when Lambda creates a new execution environment:
1. Download deployment package
2. Initialize runtime
3. Initialize application code
4. Execute handler

### Target Metrics

- **Cold Start**: < 3 seconds (requirement 8.4)
- **Warm Response**: < 500ms (requirement 8.5)

## Native Compilation

### Benefits

Native compilation with GraalVM provides:
- **Faster startup**: 10-20x faster than JVM
- **Lower memory**: 50-70% less memory usage
- **Smaller package**: 30-40% smaller deployment size

### Build Native Image

```bash
# Build native image using Docker
mvn clean package -Pnative -Dquarkus.native.container-build=true

# Build time: ~10 minutes
# Package size: ~30MB
# Cold start: <1 second
```

### Native Configuration

Key configurations in `application.properties`:

```properties
# Initialize at runtime (not build time)
quarkus.native.additional-build-args=--initialize-at-run-time=io.vertx.core.impl.VertxImpl

# Enable compression
quarkus.native.compression.level=10

# Strip debug symbols
quarkus.native.compression.additional-args=--strip-debug

# Optimize for startup
--gc=serial
-O2
```

### Reflection Configuration

Native images require explicit reflection configuration. See:
- `src/main/resources/META-INF/native-image/reflect-config.json`
- `src/main/resources/META-INF/native-image/resource-config.json`

## JVM Optimization

If native compilation is not feasible, optimize JVM mode:

### 1. Use Uber JAR

```bash
mvn clean package -Plambda
```

### 2. Optimize Dependencies

Remove unused dependencies to reduce package size:
```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-resteasy-reactive</artifactId>
    <exclusions>
        <!-- Exclude unused features -->
    </exclusions>
</dependency>
```

### 3. Class Data Sharing (CDS)

Enable CDS for faster class loading:
```properties
quarkus.package.create-appcds=true
```

## Database Connection Optimization

### 1. Connection Pool Configuration

Optimize pool size for Lambda:
```properties
# Small pool for Lambda
quarkus.datasource.reactive.max-size=10

# Quick timeout for idle connections
quarkus.datasource.reactive.idle-timeout=PT5M

# Limit connection lifetime
quarkus.datasource.reactive.max-lifetime=PT30M
```

### 2. Use RDS Proxy

RDS Proxy maintains warm connections:
- Eliminates connection overhead
- Reduces cold start impact
- Handles connection pooling

**Setup:**
```bash
# Create RDS Proxy
aws rds create-db-proxy \
  --db-proxy-name api-mgmt-proxy \
  --engine-family POSTGRESQL \
  --auth ... \
  --role-arn ... \
  --vpc-subnet-ids ...

# Update DATABASE_URL to use proxy endpoint
DATABASE_URL=postgresql://proxy-endpoint:5432/apimgmt
```

### 3. Lazy Connection Initialization

Defer database connection until first use:
```properties
quarkus.datasource.reactive.lazy=true
```

## Lambda Configuration

### 1. Memory Allocation

Higher memory = more CPU = faster execution:

| Memory | vCPU | Cold Start | Cost |
|--------|------|------------|------|
| 512 MB | 0.5 | ~3s | Low |
| 1024 MB | 1.0 | ~2s | Medium |
| 2048 MB | 2.0 | ~1s | High |

**Recommendation**: Start with 1024 MB, adjust based on metrics.

```yaml
# sam-template.yaml
Globals:
  Function:
    MemorySize: 1024
```

### 2. Provisioned Concurrency

Keep Lambda instances warm:

```bash
aws lambda put-provisioned-concurrency-config \
  --function-name api-management-system \
  --provisioned-concurrent-executions 2
```

**Cost**: ~$10/month per instance

**When to use**:
- Production with consistent traffic
- SLA requirements < 1s response time
- Cost is acceptable

### 3. Reserved Concurrency

Limit concurrent executions to control costs:

```bash
aws lambda put-function-concurrency \
  --function-name api-management-system \
  --reserved-concurrent-executions 10
```

## Application-Level Optimizations

### 1. Lazy Initialization

Initialize expensive resources only when needed:

```java
@ApplicationScoped
public class ExpensiveService {
    private volatile Client client;
    
    public Client getClient() {
        if (client == null) {
            synchronized (this) {
                if (client == null) {
                    client = initializeClient();
                }
            }
        }
        return client;
    }
}
```

### 2. Caching

Cache frequently accessed data:

```java
@ApplicationScoped
public class SystemService {
    private final Cache<UUID, SystemEntity> cache = 
        Caffeine.newBuilder()
            .maximumSize(100)
            .expireAfterWrite(5, TimeUnit.MINUTES)
            .build();
}
```

### 3. Async Processing

Use reactive programming for I/O operations:

```java
@GET
@Path("/{id}")
public Uni<SystemDTO> getSystem(@PathParam("id") UUID id) {
    return systemService.findById(id)
        .map(this::toDTO);
}
```

### 4. Batch Operations

Reduce database round trips:

```java
// Bad: N+1 queries
for (UUID id : ids) {
    repository.findById(id);
}

// Good: Single batch query
repository.findByIds(ids);
```

## API Gateway Optimization

### 1. Enable Caching

Cache GET requests at API Gateway:

```yaml
# sam-template.yaml
Events:
  ApiEvent:
    Type: Api
    Properties:
      Path: /{proxy+}
      Method: ANY
      RestApiId: !Ref ApiGateway

ApiGateway:
  Type: AWS::Serverless::Api
  Properties:
    CacheClusterEnabled: true
    CacheClusterSize: '0.5'
    MethodSettings:
      - ResourcePath: /api/v1/systems
        HttpMethod: GET
        CachingEnabled: true
        CacheTtlInSeconds: 300
```

### 2. Request Validation

Validate requests at API Gateway to reduce Lambda invocations:

```yaml
RequestValidator:
  Type: AWS::ApiGateway::RequestValidator
  Properties:
    ValidateRequestBody: true
    ValidateRequestParameters: true
```

### 3. Throttling

Protect backend from overload:

```yaml
MethodSettings:
  - ResourcePath: /*
    HttpMethod: '*'
    ThrottlingBurstLimit: 100
    ThrottlingRateLimit: 50
```

## Monitoring and Profiling

### 1. Enable X-Ray

Trace request flow and identify bottlenecks:

```properties
quarkus.lambda.enable-xray=true
```

```bash
# View traces
aws xray get-trace-summaries \
  --start-time $(date -u -d '1 hour ago' +%s) \
  --end-time $(date -u +%s)
```

### 2. CloudWatch Insights

Query Lambda logs for performance metrics:

```sql
-- Average cold start time
fields @timestamp, @duration
| filter @message like /Cold start/
| stats avg(@duration) as avg_cold_start

-- P99 response time
fields @timestamp, @duration
| stats percentile(@duration, 99) as p99_duration

-- Slow queries
fields @timestamp, @message
| filter @message like /Query execution/
| filter @duration > 500
```

### 3. Custom Metrics

Emit custom metrics to CloudWatch:

```java
@ApplicationScoped
public class MetricsService {
    @Inject
    CloudWatchClient cloudWatch;
    
    public void recordDuration(String operation, long durationMs) {
        cloudWatch.putMetricData(PutMetricDataRequest.builder()
            .namespace("ApiManagement")
            .metricData(MetricDatum.builder()
                .metricName(operation + "Duration")
                .value((double) durationMs)
                .unit(StandardUnit.MILLISECONDS)
                .build())
            .build());
    }
}
```

## Performance Testing

### 1. Load Testing

Use Artillery or JMeter:

```yaml
# artillery-config.yml
config:
  target: 'https://your-api.execute-api.region.amazonaws.com'
  phases:
    - duration: 60
      arrivalRate: 10
      name: "Warm up"
    - duration: 300
      arrivalRate: 50
      name: "Sustained load"
scenarios:
  - name: "Get systems"
    flow:
      - get:
          url: "/api/v1/systems"
```

```bash
artillery run artillery-config.yml
```

### 2. Cold Start Testing

Test cold start performance:

```bash
# Force cold start by updating function
aws lambda update-function-configuration \
  --function-name api-management-system \
  --environment Variables={FORCE_COLD_START=true}

# Wait for update
aws lambda wait function-updated \
  --function-name api-management-system

# Test cold start
time curl https://your-api.execute-api.region.amazonaws.com/api/v1/systems
```

### 3. Benchmark Script

```bash
#!/bin/bash

echo "Running performance benchmarks..."

# Test cold start
echo "Testing cold start..."
aws lambda update-function-configuration \
  --function-name api-management-system \
  --environment Variables={TEST=1} > /dev/null
aws lambda wait function-updated --function-name api-management-system

COLD_START=$(time curl -s -o /dev/null -w "%{time_total}" \
  https://your-api.execute-api.region.amazonaws.com/api/v1/systems)
echo "Cold start: ${COLD_START}s"

# Test warm response
echo "Testing warm response..."
WARM_TIMES=()
for i in {1..10}; do
  TIME=$(curl -s -o /dev/null -w "%{time_total}" \
    https://your-api.execute-api.region.amazonaws.com/api/v1/systems)
  WARM_TIMES+=($TIME)
done

AVG_WARM=$(echo "${WARM_TIMES[@]}" | awk '{sum=0; for(i=1;i<=NF;i++)sum+=$i; print sum/NF}')
echo "Average warm response: ${AVG_WARM}s"

# Check requirements
if (( $(echo "$COLD_START < 3" | bc -l) )); then
  echo "✓ Cold start requirement met (<3s)"
else
  echo "✗ Cold start requirement NOT met (>3s)"
fi

if (( $(echo "$AVG_WARM < 0.5" | bc -l) )); then
  echo "✓ Response time requirement met (<500ms)"
else
  echo "✗ Response time requirement NOT met (>500ms)"
fi
```

## Optimization Checklist

### Build Time
- [ ] Use native compilation for production
- [ ] Enable compression and strip debug symbols
- [ ] Configure reflection for all entities
- [ ] Minimize dependencies

### Runtime
- [ ] Configure optimal memory (1024 MB recommended)
- [ ] Use RDS Proxy for database connections
- [ ] Optimize connection pool size (10 connections)
- [ ] Enable lazy initialization

### Infrastructure
- [ ] Deploy Lambda in VPC with RDS
- [ ] Use provisioned concurrency for critical paths
- [ ] Enable API Gateway caching
- [ ] Configure appropriate timeouts

### Monitoring
- [ ] Enable X-Ray tracing
- [ ] Set up CloudWatch alarms
- [ ] Monitor cold start frequency
- [ ] Track P99 response times

## Troubleshooting Performance Issues

### Issue: Cold Start > 3s

**Diagnosis:**
```bash
# Check package size
ls -lh target/function.zip

# Check Lambda configuration
aws lambda get-function-configuration \
  --function-name api-management-system
```

**Solutions:**
1. Use native compilation
2. Increase memory allocation
3. Enable provisioned concurrency
4. Reduce package size

### Issue: Warm Response > 500ms

**Diagnosis:**
```bash
# Check X-Ray traces
aws xray get-trace-summaries --filter-expression "duration > 0.5"

# Check database query times
# Review CloudWatch Logs
```

**Solutions:**
1. Optimize database queries
2. Add database indexes
3. Implement caching
4. Use batch operations
5. Enable API Gateway caching

### Issue: High Memory Usage

**Diagnosis:**
```bash
# Check memory metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name MemoryUtilization \
  --dimensions Name=FunctionName,Value=api-management-system \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average
```

**Solutions:**
1. Use native compilation
2. Reduce connection pool size
3. Implement proper resource cleanup
4. Review memory leaks

## Best Practices Summary

1. **Use native compilation** for production deployments
2. **Configure RDS Proxy** to eliminate connection overhead
3. **Right-size memory** allocation (start with 1024 MB)
4. **Enable caching** at API Gateway and application level
5. **Monitor continuously** with X-Ray and CloudWatch
6. **Test regularly** with realistic load patterns
7. **Optimize queries** with proper indexes and batching
8. **Use provisioned concurrency** for critical endpoints
9. **Implement lazy initialization** for expensive resources
10. **Profile and iterate** based on real-world metrics

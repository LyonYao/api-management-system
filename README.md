# API Management System

Microservice API management and topology visualization system built with Quarkus and deployed on AWS Lambda.

## Technology Stack

- **Runtime**: AWS Lambda (Java 17+)
- **Framework**: Quarkus 3.6.4
- **Database**: PostgreSQL (Amazon RDS)
- **Build Tool**: Maven
- **API Documentation**: OpenAPI 3.0

## Prerequisites

- Java 17 or higher
- Maven 3.8+
- PostgreSQL 14+ (for local development)
- Docker (optional, for running PostgreSQL in container)

## Project Structure

```
api-management-system/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/company/apimgmt/
│   │   │       ├── controller/     # REST API controllers
│   │   │       ├── service/        # Business logic
│   │   │       ├── repository/     # Data access layer
│   │   │       ├── entity/         # Database entities
│   │   │       ├── dto/            # Data transfer objects
│   │   │       └── exception/      # Custom exceptions
│   │   └── resources/
│   │       ├── application.properties
│   │       └── db/migration/       # Flyway migration scripts
│   └── test/
│       └── java/
│           └── com/company/apimgmt/
├── pom.xml
└── README.md
```

## Local Development Setup

### 1. Start PostgreSQL Database

Using Docker:
```bash
docker run --name apimgmt-postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=apimgmt -p 5432:5432 -d postgres:14

docker-compose up -d
docker-compose down
```

Or use your local PostgreSQL installation and create the database:
```sql
CREATE DATABASE apimgmt;
```

### 2. Configure Environment Variables (Optional)

The application uses the following environment variables (defaults are provided):

```bash
export DATABASE_URL=postgresql://localhost:5432/apimgmt
export DATABASE_USERNAME=postgres
export DATABASE_PASSWORD=
export JDBC_DATABASE_URL=jdbc:postgresql://localhost:5432/apimgmt
```

### 3. Run the Application in Dev Mode

```bash
mvn quarkus:dev
```

The application will start on http://localhost:8080

### 4. Access OpenAPI Documentation

Once running, access the OpenAPI documentation at:
- Swagger UI: http://localhost:8080/q/swagger-ui
- OpenAPI Spec: http://localhost:8080/api/v1/openapi

## Building the Application

### JVM Mode

```bash
mvn clean package
```

Run the packaged application:
```bash
java -jar target/quarkus-app/quarkus-run.jar
```

### Native Mode (for optimal Lambda performance)

```bash
mvn clean package -Pnative
```

This creates a native executable optimized for fast startup times.

## Testing

Run all tests:
```bash
mvn test
```

Run with coverage:
```bash
mvn verify
```

## AWS Lambda Deployment

### Quick Start

1. **Set environment variables:**
```bash
export DATABASE_URL="postgresql://your-rds.region.rds.amazonaws.com:5432/apimgmt"
export DATABASE_USERNAME="admin"
export DATABASE_PASSWORD="YourSecurePassword"
```

2. **Deploy (JVM mode - faster build):**
```bash
./deploy.sh jvm
```

3. **Or deploy (Native mode - faster runtime):**
```bash
./deploy.sh native
```

### Build Options

#### JVM Build (Recommended for Development)
- Build time: ~2 minutes
- Package size: ~50MB
- Cold start: ~2-3 seconds

```bash
mvn clean package -Plambda
```

#### Native Build (Recommended for Production)
- Build time: ~10 minutes
- Package size: ~30MB
- Cold start: <1 second

```bash
mvn clean package -Pnative -Dquarkus.native.container-build=true
```

### Deployment Scripts

- **`deploy.sh`** / **`deploy.bat`**: Full deployment with CloudFormation
- **`scripts/package-lambda.sh`**: Build Lambda package only
- **`scripts/update-function.sh`**: Quick code update without infrastructure changes
- **`scripts/local-test.sh`**: Test locally with SAM CLI
- **`scripts/benchmark-performance.sh`**: Verify performance requirements

### Configuration

#### Required Parameters
- `DATABASE_URL`: PostgreSQL connection URL
- `DATABASE_USERNAME`: Database username
- `DATABASE_PASSWORD`: Database password

#### Optional Parameters (for VPC deployment)
- `VPC_ID`: VPC ID where RDS is located
- `SUBNET_IDS`: Comma-separated subnet IDs
- `SECURITY_GROUP_IDS`: Comma-separated security group IDs
- `DB_POOL_SIZE`: Connection pool size (default: 10)

#### Lambda Function Settings
- **Memory**: 1024 MB (configurable in sam-template.yaml)
- **Timeout**: 30 seconds
- **Runtime**: Java 17 or GraalVM native

### Performance Requirements

The system is optimized to meet these requirements:
- **Cold Start**: < 3 seconds
- **Warm Response**: < 500ms

Verify with:
```bash
./scripts/benchmark-performance.sh api-management-system
```

### Documentation

- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) - Comprehensive deployment instructions
- [Database Configuration](docs/DATABASE_CONFIGURATION.md) - RDS and VPC setup
- [Performance Optimization](docs/PERFORMANCE_OPTIMIZATION.md) - Cold start and response time optimization
- [Scripts README](scripts/README.md) - Utility scripts documentation

## Database Migrations

Database schema is managed by Flyway. Migration scripts are located in `src/main/resources/db/migration/`.

Migrations run automatically on application startup when `quarkus.flyway.migrate-at-start=true`.

## API Endpoints

### Health Check
- `GET /health` - Application health status

### Systems
- `POST /api/v1/systems` - Create system
- `GET /api/v1/systems/{id}` - Get system details
- `PUT /api/v1/systems/{id}` - Update system
- `DELETE /api/v1/systems/{id}` - Delete system
- `GET /api/v1/systems` - List all systems

### APIs
- `POST /api/v1/apis` - Create API
- `GET /api/v1/apis/{id}` - Get API details
- `PUT /api/v1/apis/{id}` - Update API
- `DELETE /api/v1/apis/{id}` - Delete API
- `GET /api/v1/apis` - List all APIs
- `GET /api/v1/apis/search` - Search APIs by system

### Endpoints
- `POST /api/v1/endpoints` - Create endpoint
- `GET /api/v1/endpoints/{id}` - Get endpoint details
- `PUT /api/v1/endpoints/{id}` - Update endpoint
- `DELETE /api/v1/endpoints/{id}` - Delete endpoint
- `GET /api/v1/endpoints` - List all endpoints
- `GET /api/v1/apis/{apiId}/endpoints` - Get API endpoints

### Relationships
- `POST /api/v1/relationships` - Create call relationship
- `GET /api/v1/relationships/{id}` - Get relationship details
- `PUT /api/v1/relationships/{id}` - Update relationship
- `DELETE /api/v1/relationships/{id}` - Delete relationship
- `GET /api/v1/relationships` - List all relationships

### Topology
- `GET /api/v1/topology` - Get full topology graph
- `GET /api/v1/topology/filter` - Get filtered topology graph

### Health Checks
- `POST /api/v1/health-check/batch` - Batch health check
- `POST /api/v1/health-check/system/{systemId}` - System health check
- `GET /api/v1/health-check/results/{batchId}` - Get health check results

## License

Copyright © 2024 Company. All rights reserved.

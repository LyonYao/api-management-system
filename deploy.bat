@echo off
REM API Management System - AWS Lambda Deployment Script for Windows

setlocal enabledelayedexpansion

echo ==========================================
echo API Management System - Lambda Deployment
echo ==========================================

REM Parse command line arguments
set BUILD_TYPE=%1
set STACK_NAME=%2

if "%BUILD_TYPE%"=="" set BUILD_TYPE=jvm
if "%STACK_NAME%"=="" set STACK_NAME=api-management-system

REM Validate build type
if not "%BUILD_TYPE%"=="jvm" if not "%BUILD_TYPE%"=="native" (
    echo Error: Build type must be 'jvm' or 'native'
    echo Usage: deploy.bat [jvm^|native] [stack-name]
    exit /b 1
)

REM Check required environment variables
if "%DATABASE_URL%"=="" (
    echo Error: DATABASE_URL environment variable is required
    exit /b 1
)

if "%DATABASE_USERNAME%"=="" (
    echo Error: DATABASE_USERNAME environment variable is required
    exit /b 1
)

if "%DATABASE_PASSWORD%"=="" (
    echo Error: DATABASE_PASSWORD environment variable is required
    exit /b 1
)

REM Build the application
echo.
echo Step 1: Building application (%BUILD_TYPE% mode^)...
if "%BUILD_TYPE%"=="native" (
    call mvn clean package -Pnative -Dquarkus.native.container-build=true
) else (
    call mvn clean package -Plambda
)

if %ERRORLEVEL% NEQ 0 (
    echo Build failed!
    exit /b %ERRORLEVEL%
)

REM Verify package exists
if not exist "target\function.zip" (
    echo Error: function.zip not found in target directory
    exit /b 1
)

echo Package created: target\function.zip

REM Prepare SAM deployment parameters
set PARAMS=DatabaseUrl="%DATABASE_URL%" DatabaseUsername="%DATABASE_USERNAME%" DatabasePassword="%DATABASE_PASSWORD%"

REM Add optional VPC parameters if provided
if not "%VPC_ID%"=="" (
    set PARAMS=!PARAMS! VpcId="%VPC_ID%"
)

if not "%SUBNET_IDS%"=="" (
    set PARAMS=!PARAMS! SubnetIds="%SUBNET_IDS%"
)

if not "%SECURITY_GROUP_IDS%"=="" (
    set PARAMS=!PARAMS! SecurityGroupIds="%SECURITY_GROUP_IDS%"
)

if not "%DB_POOL_SIZE%"=="" (
    set PARAMS=!PARAMS! DbPoolSize="%DB_POOL_SIZE%"
)

REM Deploy using SAM
echo.
echo Step 2: Deploying to AWS...
echo Stack name: %STACK_NAME%
echo Parameters: !PARAMS!

sam deploy ^
  --template-file sam-template.yaml ^
  --stack-name %STACK_NAME% ^
  --capabilities CAPABILITY_IAM ^
  --parameter-overrides !PARAMS! ^
  --no-fail-on-empty-changeset

if %ERRORLEVEL% NEQ 0 (
    echo Deployment failed!
    exit /b %ERRORLEVEL%
)

REM Get outputs
echo.
echo Step 3: Retrieving stack outputs...
for /f "delims=" %%i in ('aws cloudformation describe-stacks --stack-name %STACK_NAME% --query "Stacks[0].Outputs[?OutputKey==`ApiManagementApi`].OutputValue" --output text 2^>nul') do set API_URL=%%i
for /f "delims=" %%i in ('aws cloudformation describe-stacks --stack-name %STACK_NAME% --query "Stacks[0].Outputs[?OutputKey==`ApiManagementFunction`].OutputValue" --output text 2^>nul') do set FUNCTION_ARN=%%i

if "%API_URL%"=="" set API_URL=N/A
if "%FUNCTION_ARN%"=="" set FUNCTION_ARN=N/A

echo.
echo ==========================================
echo Deployment completed successfully!
echo ==========================================
echo.
echo API Gateway URL: %API_URL%
echo Lambda Function ARN: %FUNCTION_ARN%
echo.
echo Test the API:
echo   curl %API_URL%api/v1/systems
echo.
echo View logs:
echo   aws logs tail /aws/lambda/api-management-system --follow
echo.

endlocal

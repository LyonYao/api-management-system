#!/bin/bash

# Package Lambda function without deploying

set -e

BUILD_TYPE="${1:-jvm}"

echo "Packaging Lambda function ($BUILD_TYPE mode)..."

if [[ "$BUILD_TYPE" == "native" ]]; then
    mvn clean package -Pnative -Dquarkus.native.container-build=true
elif [[ "$BUILD_TYPE" == "jvm" ]]; then
    mvn clean package -Plambda
else
    echo "Error: Build type must be 'jvm' or 'native'"
    exit 1
fi

if [[ -f "target/function.zip" ]]; then
    echo "Package created successfully: target/function.zip"
    echo "Size: $(du -h target/function.zip | cut -f1)"
else
    echo "Error: Package creation failed"
    exit 1
fi

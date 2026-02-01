package com.company.apimgmt.repository;

import com.company.apimgmt.UnitTestProfile;
import io.quarkus.test.junit.QuarkusTest;
import io.quarkus.test.junit.TestProfile;

/**
 * Base class for repository tests that should run without Docker dependencies.
 * All repository tests are disabled by default since they require real database connections.
 * Use service tests with mocked repositories for unit testing instead.
 */
@QuarkusTest
@TestProfile(UnitTestProfile.class)
public abstract class BaseNoDockerRepositoryTest {
    // This base class provides the test profile configuration
    // Individual repository tests should disable their test methods
    // since they require real database connections
}
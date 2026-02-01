package com.company.apimgmt.repository;

import io.quarkus.test.junit.QuarkusTest;
import org.junit.jupiter.api.BeforeEach;

import jakarta.inject.Inject;
import io.vertx.mutiny.pgclient.PgPool;

/**
 * Base class for repository tests that use Docker PostgreSQL
 * NOTE: This class is deprecated. Use BaseNoDockerRepositoryTest instead
 * to avoid Docker dependency issues.
 */
@QuarkusTest
public abstract class BaseRepositoryTest {

    @Inject
    protected PgPool client;

    @BeforeEach
    public void cleanDatabase() {
        // Clean tables in reverse order of dependencies
        try {
            client.query("DELETE FROM health_check_results").execute().await().indefinitely();
            client.query("DELETE FROM relationships").execute().await().indefinitely();
            client.query("DELETE FROM api_tags").execute().await().indefinitely();
            client.query("DELETE FROM tags").execute().await().indefinitely();
            client.query("DELETE FROM endpoints").execute().await().indefinitely();
            client.query("DELETE FROM apis").execute().await().indefinitely();
            client.query("DELETE FROM systems").execute().await().indefinitely();
        } catch (Exception e) {
            // Ignore errors when database is not available
        }
    }
}
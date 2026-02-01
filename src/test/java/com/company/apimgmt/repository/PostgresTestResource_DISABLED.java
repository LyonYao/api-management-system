package com.company.apimgmt.repository;

import io.quarkus.test.common.QuarkusTestResourceLifecycleManager;
import org.testcontainers.containers.PostgreSQLContainer;

import java.util.HashMap;
import java.util.Map;

// DISABLED: This class is disabled to avoid Docker dependency issues
// Use BaseNoDockerRepositoryTest with H2 database instead
public class PostgresTestResource_DISABLED implements QuarkusTestResourceLifecycleManager {
    
    private static final PostgreSQLContainer<?> POSTGRES = new PostgreSQLContainer<>("postgres:15-alpine")
            .withDatabaseName("apimgmt_test")
            .withUsername("test")
            .withPassword("test");
    
    @Override
    public Map<String, String> start() {
        POSTGRES.start();
        
        Map<String, String> config = new HashMap<>();
        // Configure reactive datasource
        config.put("quarkus.datasource.reactive.url", POSTGRES.getJdbcUrl().replace("jdbc:", ""));
        config.put("quarkus.datasource.username", POSTGRES.getUsername());
        config.put("quarkus.datasource.password", POSTGRES.getPassword());
        
        // Configure JDBC datasource for Flyway
        config.put("quarkus.datasource.jdbc.url", POSTGRES.getJdbcUrl());
        
        return config;
    }
    
    @Override
    public void stop() {
        if (POSTGRES != null) {
            POSTGRES.stop();
        }
    }
}

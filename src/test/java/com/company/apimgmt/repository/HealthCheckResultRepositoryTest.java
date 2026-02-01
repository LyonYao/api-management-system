package com.company.apimgmt.repository;

import com.company.apimgmt.entity.ApiEntity;
import com.company.apimgmt.entity.EndpointEntity;
import com.company.apimgmt.entity.HealthCheckResultEntity;
import com.company.apimgmt.entity.SystemEntity;
import com.company.apimgmt.enums.AuthType;
import com.company.apimgmt.enums.HealthCheckStatus;
import com.company.apimgmt.enums.HttpMethod;
import org.junit.jupiter.api.Test;

import jakarta.inject.Inject;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

public class HealthCheckResultRepositoryTest extends BaseNoDockerRepositoryTest {
    
    @Inject
    HealthCheckResultRepository healthCheckResultRepository;
    
    @Inject
    EndpointRepository endpointRepository;
    
    @Inject
    ApiRepository apiRepository;
    
    @Inject
    SystemRepository systemRepository;
    
    @Test
    public void testCreateHealthCheckResult() {
        EndpointEntity endpoint = createTestEndpoint();
        
        HealthCheckResultEntity result = new HealthCheckResultEntity();
        result.id = UUID.randomUUID();
        result.endpointId = endpoint.id;
        result.status = HealthCheckStatus.SUCCESS;
        result.responseCode = 200;
        result.responseTimeMs = 150;
        result.errorMessage = null;
        result.checkedAt = LocalDateTime.now();
        
        HealthCheckResultEntity created = healthCheckResultRepository.create(result).await().indefinitely();
        
        assertNotNull(created);
        assertEquals(result.endpointId, created.endpointId);
        assertEquals(result.status, created.status);
        assertEquals(result.responseCode, created.responseCode);
        assertEquals(result.responseTimeMs, created.responseTimeMs);
    }
    
    @Test
    public void testCreateFailedHealthCheckResult() {
        EndpointEntity endpoint = createTestEndpoint();
        
        HealthCheckResultEntity result = new HealthCheckResultEntity();
        result.id = UUID.randomUUID();
        result.endpointId = endpoint.id;
        result.status = HealthCheckStatus.FAILURE;
        result.responseCode = 500;
        result.responseTimeMs = 2000;
        result.errorMessage = "Internal Server Error";
        result.checkedAt = LocalDateTime.now();
        
        HealthCheckResultEntity created = healthCheckResultRepository.create(result).await().indefinitely();
        
        assertNotNull(created);
        assertEquals(HealthCheckStatus.FAILURE, created.status);
        assertEquals("Internal Server Error", created.errorMessage);
    }
    
    @Test
    public void testCreateTimeoutHealthCheckResult() {
        EndpointEntity endpoint = createTestEndpoint();
        
        HealthCheckResultEntity result = new HealthCheckResultEntity();
        result.id = UUID.randomUUID();
        result.endpointId = endpoint.id;
        result.status = HealthCheckStatus.TIMEOUT;
        result.responseCode = null;
        result.responseTimeMs = 30000;
        result.errorMessage = "Request timeout";
        result.checkedAt = LocalDateTime.now();
        
        HealthCheckResultEntity created = healthCheckResultRepository.create(result).await().indefinitely();
        
        assertNotNull(created);
        assertEquals(HealthCheckStatus.TIMEOUT, created.status);
        assertNull(created.responseCode);
    }
    
    @Test
    public void testFindByEndpointId() {
        EndpointEntity endpoint = createTestEndpoint();
        
        // Create multiple health check results for the same endpoint
        createHealthCheckResult(endpoint.id, HealthCheckStatus.SUCCESS, 200, 100);
        createHealthCheckResult(endpoint.id, HealthCheckStatus.SUCCESS, 200, 120);
        createHealthCheckResult(endpoint.id, HealthCheckStatus.FAILURE, 500, 200);
        
        List<HealthCheckResultEntity> results = healthCheckResultRepository
            .findByEndpointId(endpoint.id)
            .await().indefinitely();
        
        assertEquals(3, results.size());
        assertTrue(results.stream().allMatch(r -> r.endpointId.equals(endpoint.id)));
    }
    
    @Test
    public void testFindByEndpointIdOrderedByTime() throws InterruptedException {
        EndpointEntity endpoint = createTestEndpoint();
        
        // Create results with different timestamps
        HealthCheckResultEntity result1 = createHealthCheckResult(endpoint.id, HealthCheckStatus.SUCCESS, 200, 100);
        Thread.sleep(10); // Small delay to ensure different timestamps
        HealthCheckResultEntity result2 = createHealthCheckResult(endpoint.id, HealthCheckStatus.SUCCESS, 200, 120);
        
        List<HealthCheckResultEntity> results = healthCheckResultRepository
            .findByEndpointId(endpoint.id)
            .await().indefinitely();
        
        // Results should be ordered by checkedAt DESC (most recent first)
        assertTrue(results.get(0).checkedAt.isAfter(results.get(1).checkedAt) ||
                   results.get(0).checkedAt.isEqual(results.get(1).checkedAt));
    }
    
    @Test
    public void testFindRecent() {
        EndpointEntity endpoint1 = createTestEndpoint();
        EndpointEntity endpoint2 = createTestEndpoint();
        
        createHealthCheckResult(endpoint1.id, HealthCheckStatus.SUCCESS, 200, 100);
        createHealthCheckResult(endpoint2.id, HealthCheckStatus.FAILURE, 500, 200);
        createHealthCheckResult(endpoint1.id, HealthCheckStatus.SUCCESS, 200, 110);
        
        List<HealthCheckResultEntity> results = healthCheckResultRepository
            .findRecent(10)
            .await().indefinitely();
        
        assertTrue(results.size() >= 3);
        // Results should be ordered by checkedAt DESC
        for (int i = 0; i < results.size() - 1; i++) {
            assertTrue(results.get(i).checkedAt.isAfter(results.get(i + 1).checkedAt) ||
                       results.get(i).checkedAt.isEqual(results.get(i + 1).checkedAt));
        }
    }
    
    @Test
    public void testFindRecentWithLimit() {
        EndpointEntity endpoint = createTestEndpoint();
        
        // Create 5 health check results
        for (int i = 0; i < 5; i++) {
            createHealthCheckResult(endpoint.id, HealthCheckStatus.SUCCESS, 200, 100 + i * 10);
        }
        
        List<HealthCheckResultEntity> results = healthCheckResultRepository
            .findRecent(3)
            .await().indefinitely();
        
        assertTrue(results.size() <= 3);
    }
    
    // Helper methods
    
    private SystemEntity createTestSystem() {
        SystemEntity system = new SystemEntity();
        system.id = UUID.randomUUID();
        system.name = "Test System " + UUID.randomUUID();
        system.description = "Test";
        system.createdAt = LocalDateTime.now();
        system.updatedAt = LocalDateTime.now();
        return systemRepository.create(system).await().indefinitely();
    }
    
    private ApiEntity createTestApi() {
        SystemEntity system = createTestSystem();
        ApiEntity api = new ApiEntity();
        api.id = UUID.randomUUID();
        api.systemId = system.id;
        api.name = "Test API " + UUID.randomUUID();
        api.description = "Test";
        api.authType = AuthType.API_KEY;
        api.department = "Engineering";
        api.contactName = "Test";
        api.contactEmails = "test@example.com";
        api.createdAt = LocalDateTime.now();
        api.updatedAt = LocalDateTime.now();
        return apiRepository.create(api).await().indefinitely();
    }
    
    private EndpointEntity createTestEndpoint() {
        ApiEntity api = createTestApi();
        EndpointEntity endpoint = new EndpointEntity();
        endpoint.id = UUID.randomUUID();
        endpoint.apiId = api.id;
        endpoint.path = "/api/test/" + UUID.randomUUID();
        endpoint.httpMethod = HttpMethod.GET;
        endpoint.description = "Test";
        endpoint.createdAt = LocalDateTime.now();
        endpoint.updatedAt = LocalDateTime.now();
        return endpointRepository.create(endpoint).await().indefinitely();
    }
    
    private HealthCheckResultEntity createHealthCheckResult(
        UUID endpointId,
        HealthCheckStatus status,
        Integer responseCode,
        Integer responseTimeMs
    ) {
        HealthCheckResultEntity result = new HealthCheckResultEntity();
        result.id = UUID.randomUUID();
        result.endpointId = endpointId;
        result.status = status;
        result.responseCode = responseCode;
        result.responseTimeMs = responseTimeMs;
        result.errorMessage = status == HealthCheckStatus.SUCCESS ? null : "Error occurred";
        result.checkedAt = LocalDateTime.now();
        return healthCheckResultRepository.create(result).await().indefinitely();
    }
}

package com.company.apimgmt.service;

import com.company.apimgmt.dto.BatchHealthCheckResponse;
import com.company.apimgmt.dto.HealthCheckResultDTO;
import com.company.apimgmt.entity.ApiEntity;
import com.company.apimgmt.entity.EndpointEntity;
import com.company.apimgmt.entity.HealthCheckResultEntity;
import com.company.apimgmt.enums.AuthType;
import com.company.apimgmt.enums.HealthCheckStatus;
import com.company.apimgmt.enums.HttpMethod;
import com.company.apimgmt.exception.ResourceNotFoundException;
import com.company.apimgmt.repository.ApiRepository;
import com.company.apimgmt.repository.EndpointRepository;
import com.company.apimgmt.repository.HealthCheckResultRepository;
import com.company.apimgmt.UnitTestProfile;
import io.quarkus.test.junit.QuarkusTest;
import io.quarkus.test.junit.TestProfile;
import io.quarkus.test.InjectMock;
import io.smallrye.mutiny.Uni;
import org.junit.jupiter.api.Test;

import jakarta.inject.Inject;
import java.time.LocalDateTime;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@QuarkusTest
@TestProfile(UnitTestProfile.class)
public class HealthCheckServiceTest {
    
    @Inject
    HealthCheckService healthCheckService;
    
    @InjectMock
    EndpointRepository endpointRepository;
    
    @InjectMock
    ApiRepository apiRepository;
    
    @InjectMock
    HealthCheckResultRepository healthCheckResultRepository;
    
    @Test
    public void testPerformHealthCheck_EndpointNotFound() {
        UUID endpointId = UUID.randomUUID();
        
        when(endpointRepository.findById(endpointId))
            .thenReturn(Uni.createFrom().nullItem());
        
        assertThrows(ResourceNotFoundException.class, () -> {
            healthCheckService.performHealthCheck(endpointId).await().indefinitely();
        });
    }
    
    @Test
    public void testPerformHealthCheck_Success() {
        UUID endpointId = UUID.randomUUID();
        UUID apiId = UUID.randomUUID();
        
        EndpointEntity endpoint = createEndpointEntity(endpointId, apiId, "http://localhost:8080/test", HttpMethod.GET);
        HealthCheckResultEntity savedResult = createHealthCheckResult(endpointId, HealthCheckStatus.FAILURE);
        savedResult.responseCode = 500;
        savedResult.responseTimeMs = 100;
        
        when(endpointRepository.findById(endpointId))
            .thenReturn(Uni.createFrom().item(endpoint));
        when(healthCheckResultRepository.create(any(HealthCheckResultEntity.class)))
            .thenReturn(Uni.createFrom().item(savedResult));
        
        HealthCheckResultDTO result = healthCheckService.performHealthCheck(endpointId)
            .await().indefinitely();
        
        assertNotNull(result);
        assertEquals(endpointId, result.endpointId);
        assertEquals("http://localhost:8080/test", result.endpointPath);
        assertEquals(HttpMethod.GET, result.httpMethod);
        assertNotNull(result.status);
    }
    
    @Test
    public void testBatchHealthCheck_EmptyList() {
        List<UUID> endpointIds = Collections.emptyList();
        
        BatchHealthCheckResponse result = healthCheckService.batchHealthCheck(endpointIds)
            .await().indefinitely();
        
        assertNotNull(result);
        assertNotNull(result.batchId);
        assertEquals(0, result.totalCount);
        assertEquals(0, result.successCount);
        assertEquals(0, result.failureCount);
        assertTrue(result.results.isEmpty());
    }
    
    @Test
    public void testBatchHealthCheck_MultipleEndpoints() {
        UUID endpointId1 = UUID.randomUUID();
        UUID endpointId2 = UUID.randomUUID();
        UUID apiId = UUID.randomUUID();
        
        EndpointEntity endpoint1 = createEndpointEntity(endpointId1, apiId, "http://localhost:8080/test1", HttpMethod.GET);
        EndpointEntity endpoint2 = createEndpointEntity(endpointId2, apiId, "http://localhost:8080/test2", HttpMethod.POST);
        
        HealthCheckResultEntity result1 = createHealthCheckResult(endpointId1, HealthCheckStatus.FAILURE);
        result1.responseCode = 500;
        result1.responseTimeMs = 100;
        
        HealthCheckResultEntity result2 = createHealthCheckResult(endpointId2, HealthCheckStatus.FAILURE);
        result2.responseCode = 404;
        result2.responseTimeMs = 150;
        
        when(endpointRepository.findById(endpointId1))
            .thenReturn(Uni.createFrom().item(endpoint1));
        when(endpointRepository.findById(endpointId2))
            .thenReturn(Uni.createFrom().item(endpoint2));
        when(healthCheckResultRepository.create(any(HealthCheckResultEntity.class)))
            .thenReturn(Uni.createFrom().item(result1))
            .thenReturn(Uni.createFrom().item(result2));
        
        List<UUID> endpointIds = Arrays.asList(endpointId1, endpointId2);
        BatchHealthCheckResponse result = healthCheckService.batchHealthCheck(endpointIds)
            .await().indefinitely();
        
        assertNotNull(result);
        assertNotNull(result.batchId);
        assertEquals(2, result.totalCount);
        assertEquals(2, result.results.size());
    }
    
    @Test
    public void testHealthCheckBySystem_NoApis() {
        UUID systemId = UUID.randomUUID();
        
        when(apiRepository.findBySystemId(systemId))
            .thenReturn(Uni.createFrom().item(Collections.emptyList()));
        
        assertThrows(ResourceNotFoundException.class, () -> {
            healthCheckService.healthCheckBySystem(systemId).await().indefinitely();
        });
    }
    
    @Test
    public void testHealthCheckBySystem_WithApis() {
        UUID systemId = UUID.randomUUID();
        UUID apiId1 = UUID.randomUUID();
        UUID apiId2 = UUID.randomUUID();
        UUID endpointId1 = UUID.randomUUID();
        UUID endpointId2 = UUID.randomUUID();
        
        ApiEntity api1 = createApiEntity(apiId1, systemId, "API 1");
        ApiEntity api2 = createApiEntity(apiId2, systemId, "API 2");
        
        EndpointEntity endpoint1 = createEndpointEntity(endpointId1, apiId1, "http://localhost:8080/test1", HttpMethod.GET);
        EndpointEntity endpoint2 = createEndpointEntity(endpointId2, apiId2, "http://localhost:8080/test2", HttpMethod.POST);
        
        HealthCheckResultEntity result1 = createHealthCheckResult(endpointId1, HealthCheckStatus.FAILURE);
        HealthCheckResultEntity result2 = createHealthCheckResult(endpointId2, HealthCheckStatus.FAILURE);
        
        when(apiRepository.findBySystemId(systemId))
            .thenReturn(Uni.createFrom().item(Arrays.asList(api1, api2)));
        when(endpointRepository.findByApiId(apiId1))
            .thenReturn(Uni.createFrom().item(Arrays.asList(endpoint1)));
        when(endpointRepository.findByApiId(apiId2))
            .thenReturn(Uni.createFrom().item(Arrays.asList(endpoint2)));
        when(endpointRepository.findById(endpointId1))
            .thenReturn(Uni.createFrom().item(endpoint1));
        when(endpointRepository.findById(endpointId2))
            .thenReturn(Uni.createFrom().item(endpoint2));
        when(healthCheckResultRepository.create(any(HealthCheckResultEntity.class)))
            .thenReturn(Uni.createFrom().item(result1))
            .thenReturn(Uni.createFrom().item(result2));
        
        BatchHealthCheckResponse result = healthCheckService.healthCheckBySystem(systemId)
            .await().indefinitely();
        
        assertNotNull(result);
        assertEquals(2, result.totalCount);
        assertEquals(2, result.results.size());
    }
    
    @Test
    public void testGetHealthCheckHistory_EndpointNotFound() {
        UUID endpointId = UUID.randomUUID();
        
        when(endpointRepository.findById(endpointId))
            .thenReturn(Uni.createFrom().nullItem());
        
        assertThrows(ResourceNotFoundException.class, () -> {
            healthCheckService.getHealthCheckHistory(endpointId).await().indefinitely();
        });
    }
    
    @Test
    public void testGetHealthCheckHistory_Success() {
        UUID endpointId = UUID.randomUUID();
        UUID apiId = UUID.randomUUID();
        
        EndpointEntity endpoint = createEndpointEntity(endpointId, apiId, "http://localhost:8080/test", HttpMethod.GET);
        
        HealthCheckResultEntity result1 = createHealthCheckResult(endpointId, HealthCheckStatus.SUCCESS);
        result1.responseCode = 200;
        result1.responseTimeMs = 100;
        
        HealthCheckResultEntity result2 = createHealthCheckResult(endpointId, HealthCheckStatus.FAILURE);
        result2.responseCode = 500;
        result2.responseTimeMs = 200;
        result2.errorMessage = "Internal Server Error";
        
        when(endpointRepository.findById(endpointId))
            .thenReturn(Uni.createFrom().item(endpoint));
        when(healthCheckResultRepository.findByEndpointId(endpointId))
            .thenReturn(Uni.createFrom().item(Arrays.asList(result1, result2)));
        
        List<HealthCheckResultDTO> results = healthCheckService.getHealthCheckHistory(endpointId)
            .await().indefinitely();
        
        assertNotNull(results);
        assertEquals(2, results.size());
        
        HealthCheckResultDTO dto1 = results.get(0);
        assertEquals(endpointId, dto1.endpointId);
        assertEquals(HealthCheckStatus.SUCCESS, dto1.status);
        assertEquals(200, dto1.responseCode);
        assertEquals(100, dto1.responseTimeMs);
        
        HealthCheckResultDTO dto2 = results.get(1);
        assertEquals(endpointId, dto2.endpointId);
        assertEquals(HealthCheckStatus.FAILURE, dto2.status);
        assertEquals(500, dto2.responseCode);
        assertEquals("Internal Server Error", dto2.errorMessage);
    }
    
    @Test
    public void testGetHealthCheckHistory_EmptyHistory() {
        UUID endpointId = UUID.randomUUID();
        UUID apiId = UUID.randomUUID();
        
        EndpointEntity endpoint = createEndpointEntity(endpointId, apiId, "http://localhost:8080/test", HttpMethod.GET);
        
        when(endpointRepository.findById(endpointId))
            .thenReturn(Uni.createFrom().item(endpoint));
        when(healthCheckResultRepository.findByEndpointId(endpointId))
            .thenReturn(Uni.createFrom().item(Collections.emptyList()));
        
        List<HealthCheckResultDTO> results = healthCheckService.getHealthCheckHistory(endpointId)
            .await().indefinitely();
        
        assertNotNull(results);
        assertTrue(results.isEmpty());
    }
    
    // Helper methods
    private ApiEntity createApiEntity(UUID id, UUID systemId, String name) {
        ApiEntity entity = new ApiEntity();
        entity.id = id;
        entity.systemId = systemId;
        entity.name = name;
        entity.description = "Test description";
        entity.authType = AuthType.API_KEY;
        entity.createdAt = LocalDateTime.now();
        entity.updatedAt = LocalDateTime.now();
        entity.tags = new HashSet<>();
        return entity;
    }
    
    private EndpointEntity createEndpointEntity(UUID id, UUID apiId, String path, HttpMethod method) {
        EndpointEntity entity = new EndpointEntity();
        entity.id = id;
        entity.apiId = apiId;
        entity.path = path;
        entity.httpMethod = method;
        entity.description = "Test endpoint";
        entity.createdAt = LocalDateTime.now();
        entity.updatedAt = LocalDateTime.now();
        return entity;
    }
    
    private HealthCheckResultEntity createHealthCheckResult(UUID endpointId, HealthCheckStatus status) {
        HealthCheckResultEntity entity = new HealthCheckResultEntity();
        entity.id = UUID.randomUUID();
        entity.endpointId = endpointId;
        entity.status = status;
        entity.checkedAt = LocalDateTime.now();
        return entity;
    }
}

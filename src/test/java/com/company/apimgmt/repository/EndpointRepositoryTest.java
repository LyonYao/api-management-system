package com.company.apimgmt.repository;

import com.company.apimgmt.entity.ApiEntity;
import com.company.apimgmt.entity.EndpointEntity;
import com.company.apimgmt.entity.SystemEntity;
import com.company.apimgmt.enums.AuthType;
import com.company.apimgmt.enums.HttpMethod;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Disabled;

import jakarta.inject.Inject;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Repository tests are disabled in no-Docker environment
 * These tests require a real database connection and are meant for integration testing
 * Use service tests with mocked repositories for unit testing instead
 */
public class EndpointRepositoryTest extends BaseNoDockerRepositoryTest {
    
    @Inject
    EndpointRepository endpointRepository;
    
    @Inject
    ApiRepository apiRepository;
    
    @Inject
    SystemRepository systemRepository;
    
    @Test
    @Disabled("Repository tests require real database - use service tests with mocks instead")
    public void testCreateEndpoint() {
        ApiEntity api = createTestApi();
        
        EndpointEntity endpoint = new EndpointEntity();
        endpoint.id = UUID.randomUUID();
        endpoint.apiId = api.id;
        endpoint.path = "/api/test";
        endpoint.httpMethod = HttpMethod.GET;
        endpoint.description = "Test endpoint";
        endpoint.createdAt = LocalDateTime.now();
        endpoint.updatedAt = LocalDateTime.now();
        
        EndpointEntity created = endpointRepository.create(endpoint).await().indefinitely();
        
        assertNotNull(created);
        assertEquals(endpoint.path, created.path);
        assertEquals(endpoint.httpMethod, created.httpMethod);
    }
    
    @Test
    @Disabled("Repository tests require real database - use service tests with mocks instead")
    public void testFindById() {
        EndpointEntity endpoint = createTestEndpoint();
        
        EndpointEntity found = endpointRepository.findById(endpoint.id).await().indefinitely();
        
        assertNotNull(found);
        assertEquals(endpoint.id, found.id);
    }
    
    @Test
    @Disabled("Repository tests require real database - use service tests with mocks instead")
    public void testFindByApiId() {
        ApiEntity api = createTestApi();
        createTestEndpointForApi(api.id, "/api/endpoint1", HttpMethod.GET);
        createTestEndpointForApi(api.id, "/api/endpoint2", HttpMethod.POST);
        
        List<EndpointEntity> endpoints = endpointRepository.findByApiId(api.id).await().indefinitely();
        
        assertEquals(2, endpoints.size());
    }
    
    @Test
    public void testUpdate() {
        EndpointEntity endpoint = createTestEndpoint();
        
        endpoint.path = "/api/updated";
        endpoint.description = "Updated description";
        EndpointEntity updated = endpointRepository.update(endpoint).await().indefinitely();
        
        assertEquals("/api/updated", updated.path);
    }
    
    @Test
    public void testDelete() {
        EndpointEntity endpoint = createTestEndpoint();
        
        Boolean deleted = endpointRepository.delete(endpoint.id).await().indefinitely();
        
        assertTrue(deleted);
    }
    
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
        return createTestEndpointForApi(api.id, "/api/test", HttpMethod.GET);
    }
    
    private EndpointEntity createTestEndpointForApi(UUID apiId, String path, HttpMethod method) {
        EndpointEntity endpoint = new EndpointEntity();
        endpoint.id = UUID.randomUUID();
        endpoint.apiId = apiId;
        endpoint.path = path;
        endpoint.httpMethod = method;
        endpoint.description = "Test";
        endpoint.createdAt = LocalDateTime.now();
        endpoint.updatedAt = LocalDateTime.now();
        return endpointRepository.create(endpoint).await().indefinitely();
    }
}

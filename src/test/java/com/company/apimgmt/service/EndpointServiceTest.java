package com.company.apimgmt.service;

import com.company.apimgmt.UnitTestProfile;

import com.company.apimgmt.dto.CreateEndpointRequest;
import com.company.apimgmt.dto.EndpointDTO;
import com.company.apimgmt.dto.UpdateEndpointRequest;
import com.company.apimgmt.entity.ApiEntity;
import com.company.apimgmt.entity.EndpointEntity;
import com.company.apimgmt.enums.AuthType;
import com.company.apimgmt.enums.HttpMethod;
import com.company.apimgmt.exception.DuplicateResourceException;
import com.company.apimgmt.exception.ResourceNotFoundException;
import com.company.apimgmt.repository.ApiRepository;
import com.company.apimgmt.repository.EndpointRepository;
import io.quarkus.test.junit.QuarkusTest;
import io.quarkus.test.junit.TestProfile;
import io.quarkus.test.InjectMock;
import io.smallrye.mutiny.Uni;
import org.junit.jupiter.api.Test;

import jakarta.inject.Inject;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;

@QuarkusTest
@TestProfile(UnitTestProfile.class)
public class EndpointServiceTest {
    
    @Inject
    EndpointService endpointService;
    
    @InjectMock
    EndpointRepository endpointRepository;
    
    @InjectMock
    ApiRepository apiRepository;
    
    @Test
    public void testCreateEndpoint_Success() {
        UUID apiId = UUID.randomUUID();
        ApiEntity api = createApiEntity(apiId, "Test API");
        
        CreateEndpointRequest request = new CreateEndpointRequest();
        request.apiId = apiId;
        request.path = "/api/test";
        request.httpMethod = HttpMethod.GET;
        request.description = "Test endpoint";
        
        EndpointEntity entity = createEndpointEntity(UUID.randomUUID(), apiId, "/api/test", HttpMethod.GET);
        
        when(apiRepository.findById(apiId))
            .thenReturn(Uni.createFrom().item(api));
        when(endpointRepository.findByApiIdPathAndMethod(apiId, "/api/test", HttpMethod.GET))
            .thenReturn(Uni.createFrom().nullItem());
        when(endpointRepository.create(any(EndpointEntity.class)))
            .thenReturn(Uni.createFrom().item(entity));
        
        EndpointDTO result = endpointService.createEndpoint(request).await().indefinitely();
        
        assertNotNull(result);
        assertEquals("/api/test", result.path);
        assertEquals(HttpMethod.GET, result.httpMethod);
    }
    
    @Test
    public void testCreateEndpoint_ApiNotFound() {
        UUID apiId = UUID.randomUUID();
        
        CreateEndpointRequest request = new CreateEndpointRequest();
        request.apiId = apiId;
        request.path = "/api/test";
        request.httpMethod = HttpMethod.GET;
        
        when(apiRepository.findById(apiId))
            .thenReturn(Uni.createFrom().nullItem());
        
        assertThrows(ResourceNotFoundException.class, () -> {
            endpointService.createEndpoint(request).await().indefinitely();
        });
    }
    
    @Test
    public void testCreateEndpoint_DuplicatePathAndMethod() {
        UUID apiId = UUID.randomUUID();
        ApiEntity api = createApiEntity(apiId, "Test API");
        EndpointEntity existing = createEndpointEntity(UUID.randomUUID(), apiId, "/api/test", HttpMethod.GET);
        
        CreateEndpointRequest request = new CreateEndpointRequest();
        request.apiId = apiId;
        request.path = "/api/test";
        request.httpMethod = HttpMethod.GET;
        
        when(apiRepository.findById(apiId))
            .thenReturn(Uni.createFrom().item(api));
        when(endpointRepository.findByApiIdPathAndMethod(apiId, "/api/test", HttpMethod.GET))
            .thenReturn(Uni.createFrom().item(existing));
        
        assertThrows(DuplicateResourceException.class, () -> {
            endpointService.createEndpoint(request).await().indefinitely();
        });
    }
    
    @Test
    public void testGetEndpointById_Success() {
        UUID id = UUID.randomUUID();
        UUID apiId = UUID.randomUUID();
        EndpointEntity entity = createEndpointEntity(id, apiId, "/api/test", HttpMethod.GET);
        
        when(endpointRepository.findById(id))
            .thenReturn(Uni.createFrom().item(entity));
        
        EndpointDTO result = endpointService.getEndpointById(id).await().indefinitely();
        
        assertNotNull(result);
        assertEquals(id, result.id);
        assertEquals("/api/test", result.path);
    }
    
    @Test
    public void testGetEndpointById_NotFound() {
        UUID id = UUID.randomUUID();
        
        when(endpointRepository.findById(id))
            .thenReturn(Uni.createFrom().nullItem());
        
        assertThrows(ResourceNotFoundException.class, () -> {
            endpointService.getEndpointById(id).await().indefinitely();
        });
    }
    
    @Test
    public void testGetAllEndpoints() {
        UUID apiId = UUID.randomUUID();
        EndpointEntity entity1 = createEndpointEntity(UUID.randomUUID(), apiId, "/api/endpoint1", HttpMethod.GET);
        EndpointEntity entity2 = createEndpointEntity(UUID.randomUUID(), apiId, "/api/endpoint2", HttpMethod.POST);
        
        when(endpointRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(entity1, entity2)));
        
        List<EndpointDTO> results = endpointService.getAllEndpoints().await().indefinitely();
        
        assertEquals(2, results.size());
    }
    
    @Test
    public void testGetEndpointsByApiId_Success() {
        UUID apiId = UUID.randomUUID();
        ApiEntity api = createApiEntity(apiId, "Test API");
        EndpointEntity entity1 = createEndpointEntity(UUID.randomUUID(), apiId, "/api/endpoint1", HttpMethod.GET);
        EndpointEntity entity2 = createEndpointEntity(UUID.randomUUID(), apiId, "/api/endpoint2", HttpMethod.POST);
        
        when(apiRepository.findById(apiId))
            .thenReturn(Uni.createFrom().item(api));
        when(endpointRepository.findByApiId(apiId))
            .thenReturn(Uni.createFrom().item(Arrays.asList(entity1, entity2)));
        
        List<EndpointDTO> results = endpointService.getEndpointsByApiId(apiId).await().indefinitely();
        
        assertEquals(2, results.size());
    }
    
    @Test
    public void testUpdateEndpoint_Success() {
        UUID id = UUID.randomUUID();
        UUID apiId = UUID.randomUUID();
        EndpointEntity entity = createEndpointEntity(id, apiId, "/api/old", HttpMethod.GET);
        
        UpdateEndpointRequest request = new UpdateEndpointRequest();
        request.path = "/api/new";
        request.description = "Updated description";
        
        EndpointEntity updated = createEndpointEntity(id, apiId, "/api/new", HttpMethod.GET);
        
        when(endpointRepository.findById(id))
            .thenReturn(Uni.createFrom().item(entity));
        when(endpointRepository.findByApiIdPathAndMethod(apiId, "/api/new", HttpMethod.GET))
            .thenReturn(Uni.createFrom().nullItem());
        when(endpointRepository.update(any(EndpointEntity.class)))
            .thenReturn(Uni.createFrom().item(updated));
        
        EndpointDTO result = endpointService.updateEndpoint(id, request).await().indefinitely();
        
        assertEquals("/api/new", result.path);
    }
    
    @Test
    public void testUpdateEndpoint_NotFound() {
        UUID id = UUID.randomUUID();
        UpdateEndpointRequest request = new UpdateEndpointRequest();
        request.path = "/api/new";
        
        when(endpointRepository.findById(id))
            .thenReturn(Uni.createFrom().nullItem());
        
        assertThrows(ResourceNotFoundException.class, () -> {
            endpointService.updateEndpoint(id, request).await().indefinitely();
        });
    }
    
    @Test
    public void testDeleteEndpoint_Success() {
        UUID id = UUID.randomUUID();
        EndpointEntity entity = createEndpointEntity(id, UUID.randomUUID(), "/api/test", HttpMethod.GET);
        
        when(endpointRepository.findById(id))
            .thenReturn(Uni.createFrom().item(entity));
        when(endpointRepository.delete(id))
            .thenReturn(Uni.createFrom().item(true));
        
        assertDoesNotThrow(() -> {
            endpointService.deleteEndpoint(id).await().indefinitely();
        });
    }
    
    @Test
    public void testDeleteEndpoint_NotFound() {
        UUID id = UUID.randomUUID();
        
        when(endpointRepository.findById(id))
            .thenReturn(Uni.createFrom().nullItem());
        
        assertThrows(ResourceNotFoundException.class, () -> {
            endpointService.deleteEndpoint(id).await().indefinitely();
        });
    }
    
    private ApiEntity createApiEntity(UUID id, String name) {
        ApiEntity entity = new ApiEntity();
        entity.id = id;
        entity.systemId = UUID.randomUUID();
        entity.name = name;
        entity.description = "Test";
        entity.authType = AuthType.API_KEY;
        entity.department = "Engineering";
        entity.contactName = "Test";
        entity.contactEmails = "test@example.com";
        entity.createdAt = LocalDateTime.now();
        entity.updatedAt = LocalDateTime.now();
        return entity;
    }
    
    private EndpointEntity createEndpointEntity(UUID id, UUID apiId, String path, HttpMethod method) {
        EndpointEntity entity = new EndpointEntity();
        entity.id = id;
        entity.apiId = apiId;
        entity.path = path;
        entity.httpMethod = method;
        entity.description = "Test";
        entity.createdAt = LocalDateTime.now();
        entity.updatedAt = LocalDateTime.now();
        return entity;
    }
}

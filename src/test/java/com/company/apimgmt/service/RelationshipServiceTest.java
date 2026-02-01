package com.company.apimgmt.service;

import com.company.apimgmt.UnitTestProfile;
import com.company.apimgmt.dto.CreateRelationshipRequest;
import com.company.apimgmt.dto.RelationshipDTO;
import com.company.apimgmt.dto.UpdateRelationshipRequest;
import com.company.apimgmt.entity.ApiEntity;
import com.company.apimgmt.entity.EndpointEntity;
import com.company.apimgmt.entity.RelationshipEntity;
import com.company.apimgmt.entity.SystemEntity;
import com.company.apimgmt.enums.AuthType;
import com.company.apimgmt.enums.EntityType;
import com.company.apimgmt.enums.HttpMethod;
import com.company.apimgmt.exception.ResourceNotFoundException;
import com.company.apimgmt.exception.ValidationException;
import com.company.apimgmt.repository.ApiRepository;
import com.company.apimgmt.repository.EndpointRepository;
import com.company.apimgmt.repository.RelationshipRepository;
import com.company.apimgmt.repository.SystemRepository;
import io.quarkus.test.junit.QuarkusTest;
import io.quarkus.test.junit.TestProfile;
import io.quarkus.test.InjectMock;
import io.smallrye.mutiny.Uni;
import io.vertx.core.json.JsonObject;
import org.junit.jupiter.api.Test;

import jakarta.inject.Inject;
import java.time.LocalDateTime;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@QuarkusTest
@TestProfile(UnitTestProfile.class)
public class RelationshipServiceTest {
    
    @Inject
    RelationshipService relationshipService;
    
    @InjectMock
    RelationshipRepository relationshipRepository;
    
    @InjectMock
    SystemRepository systemRepository;
    
    @InjectMock
    ApiRepository apiRepository;
    
    @InjectMock
    EndpointRepository endpointRepository;
    
    @Test
    public void testCreateRelationship_SystemToApi_Success() {
        UUID callerId = UUID.randomUUID();
        UUID calleeId = UUID.randomUUID();
        UUID endpointId = UUID.randomUUID();
        
        CreateRelationshipRequest request = new CreateRelationshipRequest();
        request.callerType = EntityType.SYSTEM;
        request.callerId = callerId;
        request.calleeType = EntityType.API;
        request.calleeId = calleeId;
        request.endpointId = endpointId;
        request.authType = AuthType.API_KEY;
        request.description = "Test relationship";
        
        SystemEntity callerSystem = createSystemEntity(callerId, "Caller System");
        ApiEntity calleeApi = createApiEntity(calleeId, UUID.randomUUID(), "Callee API");
        EndpointEntity endpoint = createEndpointEntity(endpointId, calleeId, "/test", HttpMethod.GET);
        RelationshipEntity createdEntity = createRelationshipEntity(
            UUID.randomUUID(), EntityType.SYSTEM, callerId, EntityType.API, calleeId, endpointId
        );
        
        when(systemRepository.findById(callerId))
            .thenReturn(Uni.createFrom().item(callerSystem));
        when(apiRepository.findById(calleeId))
            .thenReturn(Uni.createFrom().item(calleeApi));
        when(endpointRepository.findById(endpointId))
            .thenReturn(Uni.createFrom().item(endpoint));
        when(relationshipRepository.create(any(RelationshipEntity.class)))
            .thenReturn(Uni.createFrom().item(createdEntity));
        
        RelationshipDTO result = relationshipService.createRelationship(request).await().indefinitely();
        
        assertNotNull(result);
        assertEquals(EntityType.SYSTEM, result.callerType);
        assertEquals(EntityType.API, result.calleeType);
        assertEquals(callerId, result.callerId);
        assertEquals(calleeId, result.calleeId);
    }
    
    @Test
    public void testCreateRelationship_CallerNotFound() {
        UUID callerId = UUID.randomUUID();
        UUID calleeId = UUID.randomUUID();
        UUID endpointId = UUID.randomUUID();
        
        CreateRelationshipRequest request = new CreateRelationshipRequest();
        request.callerType = EntityType.SYSTEM;
        request.callerId = callerId;
        request.calleeType = EntityType.API;
        request.calleeId = calleeId;
        request.endpointId = endpointId;
        
        when(systemRepository.findById(callerId))
            .thenReturn(Uni.createFrom().nullItem());
        
        assertThrows(ResourceNotFoundException.class, () -> {
            relationshipService.createRelationship(request).await().indefinitely();
        });
    }
    
    @Test
    public void testCreateRelationship_CalleeNotFound() {
        UUID callerId = UUID.randomUUID();
        UUID calleeId = UUID.randomUUID();
        UUID endpointId = UUID.randomUUID();
        
        CreateRelationshipRequest request = new CreateRelationshipRequest();
        request.callerType = EntityType.SYSTEM;
        request.callerId = callerId;
        request.calleeType = EntityType.API;
        request.calleeId = calleeId;
        request.endpointId = endpointId;
        
        SystemEntity callerSystem = createSystemEntity(callerId, "Caller System");
        
        when(systemRepository.findById(callerId))
            .thenReturn(Uni.createFrom().item(callerSystem));
        when(apiRepository.findById(calleeId))
            .thenReturn(Uni.createFrom().nullItem());
        
        assertThrows(ResourceNotFoundException.class, () -> {
            relationshipService.createRelationship(request).await().indefinitely();
        });
    }
    
    @Test
    public void testCreateRelationship_EndpointNotFound() {
        UUID callerId = UUID.randomUUID();
        UUID calleeId = UUID.randomUUID();
        UUID endpointId = UUID.randomUUID();
        
        CreateRelationshipRequest request = new CreateRelationshipRequest();
        request.callerType = EntityType.SYSTEM;
        request.callerId = callerId;
        request.calleeType = EntityType.API;
        request.calleeId = calleeId;
        request.endpointId = endpointId;
        
        SystemEntity callerSystem = createSystemEntity(callerId, "Caller System");
        ApiEntity calleeApi = createApiEntity(calleeId, UUID.randomUUID(), "Callee API");
        
        when(systemRepository.findById(callerId))
            .thenReturn(Uni.createFrom().item(callerSystem));
        when(apiRepository.findById(calleeId))
            .thenReturn(Uni.createFrom().item(calleeApi));
        when(endpointRepository.findById(endpointId))
            .thenReturn(Uni.createFrom().nullItem());
        
        assertThrows(ResourceNotFoundException.class, () -> {
            relationshipService.createRelationship(request).await().indefinitely();
        });
    }
    
    @Test
    public void testCreateRelationship_EndpointDoesNotBelongToApi() {
        UUID callerId = UUID.randomUUID();
        UUID calleeId = UUID.randomUUID();
        UUID endpointId = UUID.randomUUID();
        UUID wrongApiId = UUID.randomUUID();
        
        CreateRelationshipRequest request = new CreateRelationshipRequest();
        request.callerType = EntityType.SYSTEM;
        request.callerId = callerId;
        request.calleeType = EntityType.API;
        request.calleeId = calleeId;
        request.endpointId = endpointId;
        
        SystemEntity callerSystem = createSystemEntity(callerId, "Caller System");
        ApiEntity calleeApi = createApiEntity(calleeId, UUID.randomUUID(), "Callee API");
        EndpointEntity endpoint = createEndpointEntity(endpointId, wrongApiId, "/test", HttpMethod.GET);
        
        when(systemRepository.findById(callerId))
            .thenReturn(Uni.createFrom().item(callerSystem));
        when(apiRepository.findById(calleeId))
            .thenReturn(Uni.createFrom().item(calleeApi));
        when(endpointRepository.findById(endpointId))
            .thenReturn(Uni.createFrom().item(endpoint));
        
        assertThrows(ValidationException.class, () -> {
            relationshipService.createRelationship(request).await().indefinitely();
        });
    }
    
    @Test
    public void testCreateRelationship_ApiToApi_Success() {
        UUID callerId = UUID.randomUUID();
        UUID calleeId = UUID.randomUUID();
        UUID endpointId = UUID.randomUUID();
        
        CreateRelationshipRequest request = new CreateRelationshipRequest();
        request.callerType = EntityType.API;
        request.callerId = callerId;
        request.calleeType = EntityType.API;
        request.calleeId = calleeId;
        request.endpointId = endpointId;
        request.authType = AuthType.OAUTH2;
        
        ApiEntity callerApi = createApiEntity(callerId, UUID.randomUUID(), "Caller API");
        ApiEntity calleeApi = createApiEntity(calleeId, UUID.randomUUID(), "Callee API");
        EndpointEntity endpoint = createEndpointEntity(endpointId, calleeId, "/test", HttpMethod.POST);
        RelationshipEntity createdEntity = createRelationshipEntity(
            UUID.randomUUID(), EntityType.API, callerId, EntityType.API, calleeId, endpointId
        );
        
        when(apiRepository.findById(callerId))
            .thenReturn(Uni.createFrom().item(callerApi));
        when(apiRepository.findById(calleeId))
            .thenReturn(Uni.createFrom().item(calleeApi));
        when(endpointRepository.findById(endpointId))
            .thenReturn(Uni.createFrom().item(endpoint));
        when(relationshipRepository.create(any(RelationshipEntity.class)))
            .thenReturn(Uni.createFrom().item(createdEntity));
        
        RelationshipDTO result = relationshipService.createRelationship(request).await().indefinitely();
        
        assertNotNull(result);
        assertEquals(EntityType.API, result.callerType);
        assertEquals(EntityType.API, result.calleeType);
    }
    
    @Test
    public void testGetRelationshipById_Success() {
        UUID id = UUID.randomUUID();
        UUID callerId = UUID.randomUUID();
        UUID calleeId = UUID.randomUUID();
        UUID endpointId = UUID.randomUUID();
        
        RelationshipEntity entity = createRelationshipEntity(
            id, EntityType.SYSTEM, callerId, EntityType.API, calleeId, endpointId
        );
        SystemEntity callerSystem = createSystemEntity(callerId, "Caller System");
        ApiEntity calleeApi = createApiEntity(calleeId, UUID.randomUUID(), "Callee API");
        EndpointEntity endpoint = createEndpointEntity(endpointId, calleeId, "/test", HttpMethod.GET);
        
        when(relationshipRepository.findById(id))
            .thenReturn(Uni.createFrom().item(entity));
        when(systemRepository.findById(callerId))
            .thenReturn(Uni.createFrom().item(callerSystem));
        when(apiRepository.findById(calleeId))
            .thenReturn(Uni.createFrom().item(calleeApi));
        when(endpointRepository.findById(endpointId))
            .thenReturn(Uni.createFrom().item(endpoint));
        
        RelationshipDTO result = relationshipService.getRelationshipById(id).await().indefinitely();
        
        assertNotNull(result);
        assertEquals(id, result.id);
        assertEquals("Caller System", result.callerName);
        assertEquals("Callee API", result.calleeName);
    }
    
    @Test
    public void testGetRelationshipById_NotFound() {
        UUID id = UUID.randomUUID();
        
        when(relationshipRepository.findById(id))
            .thenReturn(Uni.createFrom().nullItem());
        
        assertThrows(ResourceNotFoundException.class, () -> {
            relationshipService.getRelationshipById(id).await().indefinitely();
        });
    }
    
    @Test
    public void testGetAllRelationships() {
        UUID id1 = UUID.randomUUID();
        UUID id2 = UUID.randomUUID();
        UUID callerId1 = UUID.randomUUID();
        UUID calleeId1 = UUID.randomUUID();
        UUID endpointId1 = UUID.randomUUID();
        UUID callerId2 = UUID.randomUUID();
        UUID calleeId2 = UUID.randomUUID();
        UUID endpointId2 = UUID.randomUUID();
        
        RelationshipEntity entity1 = createRelationshipEntity(
            id1, EntityType.SYSTEM, callerId1, EntityType.API, calleeId1, endpointId1
        );
        RelationshipEntity entity2 = createRelationshipEntity(
            id2, EntityType.API, callerId2, EntityType.API, calleeId2, endpointId2
        );
        
        SystemEntity system1 = createSystemEntity(callerId1, "System 1");
        ApiEntity api1 = createApiEntity(calleeId1, UUID.randomUUID(), "API 1");
        ApiEntity api2 = createApiEntity(callerId2, UUID.randomUUID(), "API 2");
        ApiEntity api3 = createApiEntity(calleeId2, UUID.randomUUID(), "API 3");
        EndpointEntity endpoint1 = createEndpointEntity(endpointId1, calleeId1, "/test1", HttpMethod.GET);
        EndpointEntity endpoint2 = createEndpointEntity(endpointId2, calleeId2, "/test2", HttpMethod.POST);
        
        when(relationshipRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(entity1, entity2)));
        when(systemRepository.findById(callerId1))
            .thenReturn(Uni.createFrom().item(system1));
        when(apiRepository.findById(calleeId1))
            .thenReturn(Uni.createFrom().item(api1));
        when(apiRepository.findById(callerId2))
            .thenReturn(Uni.createFrom().item(api2));
        when(apiRepository.findById(calleeId2))
            .thenReturn(Uni.createFrom().item(api3));
        when(endpointRepository.findById(endpointId1))
            .thenReturn(Uni.createFrom().item(endpoint1));
        when(endpointRepository.findById(endpointId2))
            .thenReturn(Uni.createFrom().item(endpoint2));
        
        List<RelationshipDTO> results = relationshipService.getAllRelationships().await().indefinitely();
        
        assertEquals(2, results.size());
    }
    
    @Test
    public void testGetRelationshipsByCaller() {
        UUID callerId = UUID.randomUUID();
        UUID calleeId = UUID.randomUUID();
        UUID endpointId = UUID.randomUUID();
        UUID id = UUID.randomUUID();
        
        RelationshipEntity entity = createRelationshipEntity(
            id, EntityType.SYSTEM, callerId, EntityType.API, calleeId, endpointId
        );
        SystemEntity callerSystem = createSystemEntity(callerId, "Caller System");
        ApiEntity calleeApi = createApiEntity(calleeId, UUID.randomUUID(), "Callee API");
        EndpointEntity endpoint = createEndpointEntity(endpointId, calleeId, "/test", HttpMethod.GET);
        
        when(relationshipRepository.findByCaller(EntityType.SYSTEM, callerId))
            .thenReturn(Uni.createFrom().item(Arrays.asList(entity)));
        when(systemRepository.findById(callerId))
            .thenReturn(Uni.createFrom().item(callerSystem));
        when(apiRepository.findById(calleeId))
            .thenReturn(Uni.createFrom().item(calleeApi));
        when(endpointRepository.findById(endpointId))
            .thenReturn(Uni.createFrom().item(endpoint));
        
        List<RelationshipDTO> results = relationshipService.getRelationshipsByCaller(
            EntityType.SYSTEM, callerId
        ).await().indefinitely();
        
        assertEquals(1, results.size());
        assertEquals(callerId, results.get(0).callerId);
    }
    
    @Test
    public void testGetRelationshipsByCallee() {
        UUID callerId = UUID.randomUUID();
        UUID calleeId = UUID.randomUUID();
        UUID endpointId = UUID.randomUUID();
        UUID id = UUID.randomUUID();
        
        RelationshipEntity entity = createRelationshipEntity(
            id, EntityType.SYSTEM, callerId, EntityType.API, calleeId, endpointId
        );
        SystemEntity callerSystem = createSystemEntity(callerId, "Caller System");
        ApiEntity calleeApi = createApiEntity(calleeId, UUID.randomUUID(), "Callee API");
        EndpointEntity endpoint = createEndpointEntity(endpointId, calleeId, "/test", HttpMethod.GET);
        
        when(relationshipRepository.findByCallee(EntityType.API, calleeId))
            .thenReturn(Uni.createFrom().item(Arrays.asList(entity)));
        when(systemRepository.findById(callerId))
            .thenReturn(Uni.createFrom().item(callerSystem));
        when(apiRepository.findById(calleeId))
            .thenReturn(Uni.createFrom().item(calleeApi));
        when(endpointRepository.findById(endpointId))
            .thenReturn(Uni.createFrom().item(endpoint));
        
        List<RelationshipDTO> results = relationshipService.getRelationshipsByCallee(
            EntityType.API, calleeId
        ).await().indefinitely();
        
        assertEquals(1, results.size());
        assertEquals(calleeId, results.get(0).calleeId);
    }
    
    @Test
    public void testUpdateRelationship_Success() {
        UUID id = UUID.randomUUID();
        UUID callerId = UUID.randomUUID();
        UUID calleeId = UUID.randomUUID();
        UUID endpointId = UUID.randomUUID();
        
        RelationshipEntity entity = createRelationshipEntity(
            id, EntityType.SYSTEM, callerId, EntityType.API, calleeId, endpointId
        );
        
        UpdateRelationshipRequest request = new UpdateRelationshipRequest();
        request.description = "Updated description";
        request.authType = AuthType.JWT;
        
        SystemEntity callerSystem = createSystemEntity(callerId, "Caller System");
        ApiEntity calleeApi = createApiEntity(calleeId, UUID.randomUUID(), "Callee API");
        EndpointEntity endpoint = createEndpointEntity(endpointId, calleeId, "/test", HttpMethod.GET);
        
        when(relationshipRepository.findById(id))
            .thenReturn(Uni.createFrom().item(entity));
        when(relationshipRepository.update(any(RelationshipEntity.class)))
            .thenReturn(Uni.createFrom().item(entity));
        when(systemRepository.findById(callerId))
            .thenReturn(Uni.createFrom().item(callerSystem));
        when(apiRepository.findById(calleeId))
            .thenReturn(Uni.createFrom().item(calleeApi));
        when(endpointRepository.findById(endpointId))
            .thenReturn(Uni.createFrom().item(endpoint));
        
        RelationshipDTO result = relationshipService.updateRelationship(id, request).await().indefinitely();
        
        assertNotNull(result);
    }
    
    @Test
    public void testUpdateRelationship_NotFound() {
        UUID id = UUID.randomUUID();
        UpdateRelationshipRequest request = new UpdateRelationshipRequest();
        request.description = "Updated";
        
        when(relationshipRepository.findById(id))
            .thenReturn(Uni.createFrom().nullItem());
        
        assertThrows(ResourceNotFoundException.class, () -> {
            relationshipService.updateRelationship(id, request).await().indefinitely();
        });
    }
    
    @Test
    public void testDeleteRelationship_Success() {
        UUID id = UUID.randomUUID();
        RelationshipEntity entity = createRelationshipEntity(
            id, EntityType.SYSTEM, UUID.randomUUID(), EntityType.API, UUID.randomUUID(), UUID.randomUUID()
        );
        
        when(relationshipRepository.findById(id))
            .thenReturn(Uni.createFrom().item(entity));
        when(relationshipRepository.delete(id))
            .thenReturn(Uni.createFrom().item(true));
        
        assertDoesNotThrow(() -> {
            relationshipService.deleteRelationship(id).await().indefinitely();
        });
    }
    
    @Test
    public void testDeleteRelationship_NotFound() {
        UUID id = UUID.randomUUID();
        
        when(relationshipRepository.findById(id))
            .thenReturn(Uni.createFrom().nullItem());
        
        assertThrows(ResourceNotFoundException.class, () -> {
            relationshipService.deleteRelationship(id).await().indefinitely();
        });
    }
    
    // Helper methods
    private SystemEntity createSystemEntity(UUID id, String name) {
        SystemEntity entity = new SystemEntity();
        entity.id = id;
        entity.name = name;
        entity.description = "Test description";
        entity.createdAt = LocalDateTime.now();
        entity.updatedAt = LocalDateTime.now();
        return entity;
    }
    
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
    
    private RelationshipEntity createRelationshipEntity(
            UUID id, EntityType callerType, UUID callerId, 
            EntityType calleeType, UUID calleeId, UUID endpointId) {
        RelationshipEntity entity = new RelationshipEntity();
        entity.id = id;
        entity.callerType = callerType;
        entity.callerId = callerId;
        entity.calleeType = calleeType;
        entity.calleeId = calleeId;
        entity.endpointId = endpointId;
        entity.authType = AuthType.API_KEY;
        entity.authConfig = new JsonObject();
        entity.description = "Test relationship";
        entity.createdAt = LocalDateTime.now();
        entity.updatedAt = LocalDateTime.now();
        return entity;
    }
}

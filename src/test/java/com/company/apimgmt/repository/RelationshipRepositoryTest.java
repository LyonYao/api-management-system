package com.company.apimgmt.repository;

import com.company.apimgmt.entity.ApiEntity;
import com.company.apimgmt.entity.EndpointEntity;
import com.company.apimgmt.entity.RelationshipEntity;
import com.company.apimgmt.entity.SystemEntity;
import com.company.apimgmt.enums.AuthType;
import com.company.apimgmt.enums.EntityType;
import com.company.apimgmt.enums.HttpMethod;
import io.vertx.core.json.JsonObject;
import org.junit.jupiter.api.Test;

import jakarta.inject.Inject;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

public class RelationshipRepositoryTest extends BaseNoDockerRepositoryTest {
    
    @Inject
    RelationshipRepository relationshipRepository;
    
    @Inject
    SystemRepository systemRepository;
    
    @Inject
    ApiRepository apiRepository;
    
    @Inject
    EndpointRepository endpointRepository;
    
    @Test
    public void testCreateRelationship() {
        SystemEntity callerSystem = createTestSystem("Caller System");
        SystemEntity calleeSystem = createTestSystem("Callee System");
        ApiEntity calleeApi = createTestApiForSystem(calleeSystem.id, "Callee API");
        EndpointEntity endpoint = createTestEndpointForApi(calleeApi.id, "/api/test", HttpMethod.GET);
        
        RelationshipEntity relationship = new RelationshipEntity();
        relationship.id = UUID.randomUUID();
        relationship.callerType = EntityType.SYSTEM;
        relationship.callerId = callerSystem.id;
        relationship.calleeType = EntityType.API;
        relationship.calleeId = calleeApi.id;
        relationship.endpointId = endpoint.id;
        relationship.authType = AuthType.API_KEY;
        relationship.authConfig = new JsonObject().put("apiKey", "test-key");
        relationship.description = "Test relationship";
        relationship.createdAt = LocalDateTime.now();
        relationship.updatedAt = LocalDateTime.now();
        
        RelationshipEntity created = relationshipRepository.create(relationship).await().indefinitely();
        
        assertNotNull(created);
        assertEquals(relationship.callerType, created.callerType);
        assertEquals(relationship.callerId, created.callerId);
        assertEquals(relationship.calleeType, created.calleeType);
        assertEquals(relationship.calleeId, created.calleeId);
        assertEquals(relationship.endpointId, created.endpointId);
    }
    
    @Test
    public void testFindById() {
        RelationshipEntity relationship = createTestRelationship();
        
        RelationshipEntity found = relationshipRepository.findById(relationship.id).await().indefinitely();
        
        assertNotNull(found);
        assertEquals(relationship.id, found.id);
        assertEquals(relationship.callerType, found.callerType);
        assertEquals(relationship.calleeType, found.calleeType);
    }
    
    @Test
    public void testFindAll() {
        createTestRelationship();
        createTestRelationship();
        
        List<RelationshipEntity> relationships = relationshipRepository.findAll().await().indefinitely();
        
        assertTrue(relationships.size() >= 2);
    }
    
    @Test
    public void testFindByCaller() {
        SystemEntity callerSystem = createTestSystem("Specific Caller");
        SystemEntity calleeSystem = createTestSystem("Callee System");
        ApiEntity calleeApi = createTestApiForSystem(calleeSystem.id, "Callee API");
        EndpointEntity endpoint = createTestEndpointForApi(calleeApi.id, "/api/test", HttpMethod.GET);
        
        RelationshipEntity rel1 = createRelationship(
            EntityType.SYSTEM, callerSystem.id,
            EntityType.API, calleeApi.id,
            endpoint.id
        );
        
        List<RelationshipEntity> relationships = relationshipRepository
            .findByCaller(EntityType.SYSTEM, callerSystem.id)
            .await().indefinitely();
        
        assertTrue(relationships.size() >= 1);
        assertTrue(relationships.stream().anyMatch(r -> r.id.equals(rel1.id)));
    }
    
    @Test
    public void testFindByCallee() {
        SystemEntity callerSystem = createTestSystem("Caller System");
        ApiEntity calleeApi = createTestApi();
        EndpointEntity endpoint = createTestEndpointForApi(calleeApi.id, "/api/test", HttpMethod.GET);
        
        RelationshipEntity rel1 = createRelationship(
            EntityType.SYSTEM, callerSystem.id,
            EntityType.API, calleeApi.id,
            endpoint.id
        );
        
        List<RelationshipEntity> relationships = relationshipRepository
            .findByCallee(EntityType.API, calleeApi.id)
            .await().indefinitely();
        
        assertTrue(relationships.size() >= 1);
        assertTrue(relationships.stream().anyMatch(r -> r.id.equals(rel1.id)));
    }
    
    @Test
    public void testUpdate() {
        RelationshipEntity relationship = createTestRelationship();
        
        relationship.description = "Updated description";
        relationship.authType = AuthType.OAUTH2;
        RelationshipEntity updated = relationshipRepository.update(relationship).await().indefinitely();
        
        assertEquals("Updated description", updated.description);
        assertEquals(AuthType.OAUTH2, updated.authType);
    }
    
    @Test
    public void testDelete() {
        RelationshipEntity relationship = createTestRelationship();
        
        Boolean deleted = relationshipRepository.delete(relationship.id).await().indefinitely();
        
        assertTrue(deleted);
        
        RelationshipEntity found = relationshipRepository.findById(relationship.id).await().indefinitely();
        assertNull(found);
    }
    
    @Test
    public void testSystemToSystemRelationship() {
        SystemEntity callerSystem = createTestSystem("System A");
        SystemEntity calleeSystem = createTestSystem("System B");
        ApiEntity calleeApi = createTestApiForSystem(calleeSystem.id, "API");
        EndpointEntity endpoint = createTestEndpointForApi(calleeApi.id, "/api/test", HttpMethod.POST);
        
        RelationshipEntity relationship = createRelationship(
            EntityType.SYSTEM, callerSystem.id,
            EntityType.SYSTEM, calleeSystem.id,
            endpoint.id
        );
        
        assertNotNull(relationship);
        assertEquals(EntityType.SYSTEM, relationship.callerType);
        assertEquals(EntityType.SYSTEM, relationship.calleeType);
    }
    
    @Test
    public void testApiToApiRelationship() {
        ApiEntity callerApi = createTestApi();
        ApiEntity calleeApi = createTestApi();
        EndpointEntity endpoint = createTestEndpointForApi(calleeApi.id, "/api/test", HttpMethod.GET);
        
        RelationshipEntity relationship = createRelationship(
            EntityType.API, callerApi.id,
            EntityType.API, calleeApi.id,
            endpoint.id
        );
        
        assertNotNull(relationship);
        assertEquals(EntityType.API, relationship.callerType);
        assertEquals(EntityType.API, relationship.calleeType);
    }
    
    // Helper methods
    
    private SystemEntity createTestSystem(String name) {
        SystemEntity system = new SystemEntity();
        system.id = UUID.randomUUID();
        system.name = name + " " + UUID.randomUUID();
        system.description = "Test";
        system.createdAt = LocalDateTime.now();
        system.updatedAt = LocalDateTime.now();
        return systemRepository.create(system).await().indefinitely();
    }
    
    private ApiEntity createTestApi() {
        SystemEntity system = createTestSystem("System");
        return createTestApiForSystem(system.id, "API");
    }
    
    private ApiEntity createTestApiForSystem(UUID systemId, String name) {
        ApiEntity api = new ApiEntity();
        api.id = UUID.randomUUID();
        api.systemId = systemId;
        api.name = name + " " + UUID.randomUUID();
        api.description = "Test";
        api.authType = AuthType.API_KEY;
        api.department = "Engineering";
        api.contactName = "Test";
        api.contactEmails = "test@example.com";
        api.createdAt = LocalDateTime.now();
        api.updatedAt = LocalDateTime.now();
        return apiRepository.create(api).await().indefinitely();
    }
    
    private EndpointEntity createTestEndpointForApi(UUID apiId, String path, HttpMethod method) {
        EndpointEntity endpoint = new EndpointEntity();
        endpoint.id = UUID.randomUUID();
        endpoint.apiId = apiId;
        endpoint.path = path + "/" + UUID.randomUUID();
        endpoint.httpMethod = method;
        endpoint.description = "Test";
        endpoint.createdAt = LocalDateTime.now();
        endpoint.updatedAt = LocalDateTime.now();
        return endpointRepository.create(endpoint).await().indefinitely();
    }
    
    private RelationshipEntity createTestRelationship() {
        SystemEntity callerSystem = createTestSystem("Caller");
        ApiEntity calleeApi = createTestApi();
        EndpointEntity endpoint = createTestEndpointForApi(calleeApi.id, "/api/test", HttpMethod.GET);
        
        return createRelationship(
            EntityType.SYSTEM, callerSystem.id,
            EntityType.API, calleeApi.id,
            endpoint.id
        );
    }
    
    private RelationshipEntity createRelationship(
        EntityType callerType, UUID callerId,
        EntityType calleeType, UUID calleeId,
        UUID endpointId
    ) {
        RelationshipEntity relationship = new RelationshipEntity();
        relationship.id = UUID.randomUUID();
        relationship.callerType = callerType;
        relationship.callerId = callerId;
        relationship.calleeType = calleeType;
        relationship.calleeId = calleeId;
        relationship.endpointId = endpointId;
        relationship.authType = AuthType.API_KEY;
        relationship.authConfig = new JsonObject().put("key", "value");
        relationship.description = "Test relationship";
        relationship.createdAt = LocalDateTime.now();
        relationship.updatedAt = LocalDateTime.now();
        return relationshipRepository.create(relationship).await().indefinitely();
    }
}

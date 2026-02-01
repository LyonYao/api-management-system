package com.company.apimgmt.service;

import com.company.apimgmt.UnitTestProfile;
import com.company.apimgmt.dto.EdgeDTO;
import com.company.apimgmt.dto.NodeDTO;
import com.company.apimgmt.dto.TopologyDTO;
import com.company.apimgmt.entity.ApiEntity;
import com.company.apimgmt.entity.RelationshipEntity;
import com.company.apimgmt.entity.SystemEntity;
import com.company.apimgmt.enums.AuthType;
import com.company.apimgmt.enums.EntityType;
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
import static org.mockito.Mockito.when;

@QuarkusTest
@TestProfile(UnitTestProfile.class)
public class TopologyServiceTest {
    
    @Inject
    TopologyService topologyService;
    
    @InjectMock
    SystemRepository systemRepository;
    
    @InjectMock
    ApiRepository apiRepository;
    
    @InjectMock
    RelationshipRepository relationshipRepository;
    
    @InjectMock
    EndpointRepository endpointRepository;
    
    @Test
    public void testGetFullTopology_EmptyData() {
        when(systemRepository.findAll())
            .thenReturn(Uni.createFrom().item(Collections.emptyList()));
        when(apiRepository.findAll())
            .thenReturn(Uni.createFrom().item(Collections.emptyList()));
        when(relationshipRepository.findAll())
            .thenReturn(Uni.createFrom().item(Collections.emptyList()));
        
        TopologyDTO result = topologyService.getFullTopology().await().indefinitely();
        
        assertNotNull(result);
        assertTrue(result.nodes.isEmpty());
        assertTrue(result.edges.isEmpty());
    }
    
    @Test
    public void testGetFullTopology_WithSystemsAndApis() {
        UUID systemId1 = UUID.randomUUID();
        UUID systemId2 = UUID.randomUUID();
        UUID apiId1 = UUID.randomUUID();
        UUID apiId2 = UUID.randomUUID();
        
        SystemEntity system1 = createSystemEntity(systemId1, "System 1");
        SystemEntity system2 = createSystemEntity(systemId2, "System 2");
        ApiEntity api1 = createApiEntity(apiId1, systemId1, "API 1");
        ApiEntity api2 = createApiEntity(apiId2, systemId2, "API 2");
        
        when(systemRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(system1, system2)));
        when(apiRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(api1, api2)));
        when(relationshipRepository.findAll())
            .thenReturn(Uni.createFrom().item(Collections.emptyList()));
        
        TopologyDTO result = topologyService.getFullTopology().await().indefinitely();
        
        assertNotNull(result);
        assertEquals(4, result.nodes.size());
        
        // Verify system nodes
        long systemNodeCount = result.nodes.stream()
            .filter(node -> node.type == EntityType.SYSTEM)
            .count();
        assertEquals(2, systemNodeCount);
        
        // Verify API nodes
        long apiNodeCount = result.nodes.stream()
            .filter(node -> node.type == EntityType.API)
            .count();
        assertEquals(2, apiNodeCount);
        
        assertTrue(result.edges.isEmpty());
    }
    
    @Test
    public void testGetFullTopology_WithRelationships() {
        UUID systemId1 = UUID.randomUUID();
        UUID apiId1 = UUID.randomUUID();
        UUID apiId2 = UUID.randomUUID();
        UUID endpointId = UUID.randomUUID();
        UUID relationshipId = UUID.randomUUID();
        
        SystemEntity system1 = createSystemEntity(systemId1, "System 1");
        ApiEntity api1 = createApiEntity(apiId1, systemId1, "API 1");
        ApiEntity api2 = createApiEntity(apiId2, systemId1, "API 2");
        RelationshipEntity relationship = createRelationshipEntity(
            relationshipId, EntityType.API, apiId1, EntityType.API, apiId2, endpointId
        );
        
        when(systemRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(system1)));
        when(apiRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(api1, api2)));
        when(relationshipRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(relationship)));
        
        TopologyDTO result = topologyService.getFullTopology().await().indefinitely();
        
        assertNotNull(result);
        assertEquals(3, result.nodes.size()); // 1 system + 2 APIs
        assertEquals(1, result.edges.size());
        
        EdgeDTO edge = result.edges.get(0);
        assertEquals(relationshipId, edge.id);
        assertEquals(apiId1, edge.sourceId);
        assertEquals(apiId2, edge.targetId);
        assertEquals(AuthType.API_KEY, edge.authType);
    }
    
    @Test
    public void testGetFullTopology_NodeMetadata() {
        UUID systemId = UUID.randomUUID();
        UUID apiId = UUID.randomUUID();
        
        SystemEntity system = createSystemEntity(systemId, "Test System");
        system.description = "System description";
        
        ApiEntity api = createApiEntity(apiId, systemId, "Test API");
        api.description = "API description";
        api.department = "Engineering";
        api.contactName = "John Doe";
        api.contactEmails = "john@example.com,jane@example.com";
        api.specLink = "https://api.example.com/spec";
        api.tags = new HashSet<>(Arrays.asList("tag1", "tag2"));
        
        when(systemRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(system)));
        when(apiRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(api)));
        when(relationshipRepository.findAll())
            .thenReturn(Uni.createFrom().item(Collections.emptyList()));
        
        TopologyDTO result = topologyService.getFullTopology().await().indefinitely();
        
        assertNotNull(result);
        assertEquals(2, result.nodes.size());
        
        // Find system node
        NodeDTO systemNode = result.nodes.stream()
            .filter(node -> node.type == EntityType.SYSTEM)
            .findFirst()
            .orElse(null);
        assertNotNull(systemNode);
        assertEquals("Test System", systemNode.name);
        assertEquals("System description", systemNode.metadata.get("description"));
        
        // Find API node
        NodeDTO apiNode = result.nodes.stream()
            .filter(node -> node.type == EntityType.API)
            .findFirst()
            .orElse(null);
        assertNotNull(apiNode);
        assertEquals("Test API", apiNode.name);
        assertEquals("API description", apiNode.metadata.get("description"));
        assertEquals("Engineering", apiNode.metadata.get("department"));
        assertEquals("John Doe", apiNode.metadata.get("contactName"));
        assertEquals("https://api.example.com/spec", apiNode.metadata.get("specLink"));
        
        @SuppressWarnings("unchecked")
        List<String> contactEmails = (List<String>) apiNode.metadata.get("contactEmails");
        assertEquals(2, contactEmails.size());
        assertTrue(contactEmails.contains("john@example.com"));
        assertTrue(contactEmails.contains("jane@example.com"));
    }
    
    @Test
    public void testGetTopologyByTags_EmptyTags() {
        UUID systemId = UUID.randomUUID();
        UUID apiId = UUID.randomUUID();
        
        SystemEntity system = createSystemEntity(systemId, "System 1");
        ApiEntity api = createApiEntity(apiId, systemId, "API 1");
        
        when(systemRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(system)));
        when(apiRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(api)));
        when(relationshipRepository.findAll())
            .thenReturn(Uni.createFrom().item(Collections.emptyList()));
        
        TopologyDTO result = topologyService.getTopologyByTags(Collections.emptySet()).await().indefinitely();
        
        assertNotNull(result);
        assertEquals(2, result.nodes.size());
    }
    
    @Test
    public void testGetTopologyByTags_FilteredByTag() {
        UUID systemId1 = UUID.randomUUID();
        UUID systemId2 = UUID.randomUUID();
        UUID apiId1 = UUID.randomUUID();
        UUID apiId2 = UUID.randomUUID();
        UUID apiId3 = UUID.randomUUID();
        
        SystemEntity system1 = createSystemEntity(systemId1, "System 1");
        SystemEntity system2 = createSystemEntity(systemId2, "System 2");
        
        ApiEntity api1 = createApiEntity(apiId1, systemId1, "API 1");
        api1.tags = new HashSet<>(Arrays.asList("tag1"));
        
        ApiEntity api2 = createApiEntity(apiId2, systemId1, "API 2");
        api2.tags = new HashSet<>(Arrays.asList("tag1", "tag2"));
        
        ApiEntity api3 = createApiEntity(apiId3, systemId2, "API 3");
        api3.tags = new HashSet<>(Arrays.asList("tag3"));
        
        Set<String> filterTags = new HashSet<>(Arrays.asList("tag1"));
        
        when(apiRepository.findByTags(filterTags))
            .thenReturn(Uni.createFrom().item(Arrays.asList(api1, api2)));
        when(systemRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(system1, system2)));
        when(relationshipRepository.findAll())
            .thenReturn(Uni.createFrom().item(Collections.emptyList()));
        
        TopologyDTO result = topologyService.getTopologyByTags(filterTags).await().indefinitely();
        
        assertNotNull(result);
        // Should have 1 system (system1) + 2 APIs (api1, api2)
        assertEquals(3, result.nodes.size());
        
        // Verify only system1 is included
        long systemCount = result.nodes.stream()
            .filter(node -> node.type == EntityType.SYSTEM)
            .count();
        assertEquals(1, systemCount);
        
        // Verify only api1 and api2 are included
        long apiCount = result.nodes.stream()
            .filter(node -> node.type == EntityType.API)
            .count();
        assertEquals(2, apiCount);
    }
    
    @Test
    public void testGetTopologyByTags_FilteredRelationships() {
        UUID systemId1 = UUID.randomUUID();
        UUID apiId1 = UUID.randomUUID();
        UUID apiId2 = UUID.randomUUID();
        UUID apiId3 = UUID.randomUUID();
        UUID endpointId1 = UUID.randomUUID();
        UUID endpointId2 = UUID.randomUUID();
        
        SystemEntity system1 = createSystemEntity(systemId1, "System 1");
        
        ApiEntity api1 = createApiEntity(apiId1, systemId1, "API 1");
        api1.tags = new HashSet<>(Arrays.asList("tag1"));
        
        ApiEntity api2 = createApiEntity(apiId2, systemId1, "API 2");
        api2.tags = new HashSet<>(Arrays.asList("tag1"));
        
        ApiEntity api3 = createApiEntity(apiId3, systemId1, "API 3");
        api3.tags = new HashSet<>(Arrays.asList("tag2"));
        
        // Relationship between api1 and api2 (should be included)
        RelationshipEntity rel1 = createRelationshipEntity(
            UUID.randomUUID(), EntityType.API, apiId1, EntityType.API, apiId2, endpointId1
        );
        
        // Relationship between api1 and api3 (should be excluded because api3 is not in filtered set)
        RelationshipEntity rel2 = createRelationshipEntity(
            UUID.randomUUID(), EntityType.API, apiId1, EntityType.API, apiId3, endpointId2
        );
        
        Set<String> filterTags = new HashSet<>(Arrays.asList("tag1"));
        
        when(apiRepository.findByTags(filterTags))
            .thenReturn(Uni.createFrom().item(Arrays.asList(api1, api2)));
        when(systemRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(system1)));
        when(relationshipRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(rel1, rel2)));
        
        TopologyDTO result = topologyService.getTopologyByTags(filterTags).await().indefinitely();
        
        assertNotNull(result);
        assertEquals(3, result.nodes.size()); // 1 system + 2 APIs
        assertEquals(1, result.edges.size()); // Only rel1 should be included
        
        EdgeDTO edge = result.edges.get(0);
        assertEquals(apiId1, edge.sourceId);
        assertEquals(apiId2, edge.targetId);
    }
    
    @Test
    public void testGetTopologyByTags_SystemToApiRelationship() {
        UUID systemId1 = UUID.randomUUID();
        UUID systemId2 = UUID.randomUUID();
        UUID apiId1 = UUID.randomUUID();
        UUID endpointId = UUID.randomUUID();
        
        SystemEntity system1 = createSystemEntity(systemId1, "System 1");
        SystemEntity system2 = createSystemEntity(systemId2, "System 2");
        
        ApiEntity api1 = createApiEntity(apiId1, systemId1, "API 1");
        api1.tags = new HashSet<>(Arrays.asList("tag1"));
        
        // Relationship from system2 to api1
        RelationshipEntity rel = createRelationshipEntity(
            UUID.randomUUID(), EntityType.SYSTEM, systemId2, EntityType.API, apiId1, endpointId
        );
        
        Set<String> filterTags = new HashSet<>(Arrays.asList("tag1"));
        
        when(apiRepository.findByTags(filterTags))
            .thenReturn(Uni.createFrom().item(Arrays.asList(api1)));
        when(systemRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(system1, system2)));
        when(relationshipRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(rel)));
        
        TopologyDTO result = topologyService.getTopologyByTags(filterTags).await().indefinitely();
        
        assertNotNull(result);
        // Should include system1 (parent of api1) but not system2 (not related to filtered APIs)
        assertEquals(2, result.nodes.size()); // 1 system + 1 API
        assertEquals(0, result.edges.size()); // Relationship excluded because system2 is not in filtered set
    }
    
    @Test
    public void testGetFullTopology_EdgeMetadata() {
        UUID systemId = UUID.randomUUID();
        UUID apiId1 = UUID.randomUUID();
        UUID apiId2 = UUID.randomUUID();
        UUID endpointId = UUID.randomUUID();
        UUID relationshipId = UUID.randomUUID();
        
        SystemEntity system = createSystemEntity(systemId, "System 1");
        ApiEntity api1 = createApiEntity(apiId1, systemId, "API 1");
        ApiEntity api2 = createApiEntity(apiId2, systemId, "API 2");
        
        RelationshipEntity relationship = createRelationshipEntity(
            relationshipId, EntityType.API, apiId1, EntityType.API, apiId2, endpointId
        );
        relationship.description = "Test relationship description";
        relationship.authType = AuthType.OAUTH2;
        relationship.authConfig = new JsonObject()
            .put("clientId", "test-client")
            .put("scope", "read:api");
        
        when(systemRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(system)));
        when(apiRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(api1, api2)));
        when(relationshipRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(relationship)));
        
        TopologyDTO result = topologyService.getFullTopology().await().indefinitely();
        
        assertNotNull(result);
        assertEquals(1, result.edges.size());
        
        EdgeDTO edge = result.edges.get(0);
        assertEquals(relationshipId, edge.id);
        assertEquals(apiId1, edge.sourceId);
        assertEquals(apiId2, edge.targetId);
        assertEquals(AuthType.OAUTH2, edge.authType);
        
        // Verify edge metadata
        assertEquals(endpointId.toString(), edge.metadata.get("endpointId"));
        assertEquals("Test relationship description", edge.metadata.get("description"));
        assertEquals("API", edge.metadata.get("callerType"));
        assertEquals("API", edge.metadata.get("calleeType"));
        
        @SuppressWarnings("unchecked")
        Map<String, Object> authConfig = (Map<String, Object>) edge.metadata.get("authConfig");
        assertNotNull(authConfig);
        assertEquals("test-client", authConfig.get("clientId"));
        assertEquals("read:api", authConfig.get("scope"));
    }
    
    @Test
    public void testGetFullTopology_MultipleRelationshipTypes() {
        UUID systemId1 = UUID.randomUUID();
        UUID systemId2 = UUID.randomUUID();
        UUID apiId1 = UUID.randomUUID();
        UUID apiId2 = UUID.randomUUID();
        UUID endpointId1 = UUID.randomUUID();
        UUID endpointId2 = UUID.randomUUID();
        UUID endpointId3 = UUID.randomUUID();
        UUID endpointId4 = UUID.randomUUID();
        
        SystemEntity system1 = createSystemEntity(systemId1, "System 1");
        SystemEntity system2 = createSystemEntity(systemId2, "System 2");
        ApiEntity api1 = createApiEntity(apiId1, systemId1, "API 1");
        ApiEntity api2 = createApiEntity(apiId2, systemId2, "API 2");
        
        // System to System
        RelationshipEntity rel1 = createRelationshipEntity(
            UUID.randomUUID(), EntityType.SYSTEM, systemId1, EntityType.SYSTEM, systemId2, endpointId1
        );
        
        // System to API
        RelationshipEntity rel2 = createRelationshipEntity(
            UUID.randomUUID(), EntityType.SYSTEM, systemId1, EntityType.API, apiId2, endpointId2
        );
        
        // API to System
        RelationshipEntity rel3 = createRelationshipEntity(
            UUID.randomUUID(), EntityType.API, apiId1, EntityType.SYSTEM, systemId2, endpointId3
        );
        
        // API to API
        RelationshipEntity rel4 = createRelationshipEntity(
            UUID.randomUUID(), EntityType.API, apiId1, EntityType.API, apiId2, endpointId4
        );
        
        when(systemRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(system1, system2)));
        when(apiRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(api1, api2)));
        when(relationshipRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(rel1, rel2, rel3, rel4)));
        
        TopologyDTO result = topologyService.getFullTopology().await().indefinitely();
        
        assertNotNull(result);
        assertEquals(4, result.nodes.size()); // 2 systems + 2 APIs
        assertEquals(4, result.edges.size()); // All 4 relationship types
        
        // Verify all relationship types are present
        assertEquals(1, result.edges.stream()
            .filter(e -> e.metadata.get("callerType").equals("SYSTEM") && 
                        e.metadata.get("calleeType").equals("SYSTEM"))
            .count());
        
        assertEquals(1, result.edges.stream()
            .filter(e -> e.metadata.get("callerType").equals("SYSTEM") && 
                        e.metadata.get("calleeType").equals("API"))
            .count());
        
        assertEquals(1, result.edges.stream()
            .filter(e -> e.metadata.get("callerType").equals("API") && 
                        e.metadata.get("calleeType").equals("SYSTEM"))
            .count());
        
        assertEquals(1, result.edges.stream()
            .filter(e -> e.metadata.get("callerType").equals("API") && 
                        e.metadata.get("calleeType").equals("API"))
            .count());
    }
    
    @Test
    public void testGetTopologyByTags_NullTags() {
        UUID systemId = UUID.randomUUID();
        UUID apiId = UUID.randomUUID();
        
        SystemEntity system = createSystemEntity(systemId, "System 1");
        ApiEntity api = createApiEntity(apiId, systemId, "API 1");
        
        when(systemRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(system)));
        when(apiRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(api)));
        when(relationshipRepository.findAll())
            .thenReturn(Uni.createFrom().item(Collections.emptyList()));
        
        TopologyDTO result = topologyService.getTopologyByTags(null).await().indefinitely();
        
        assertNotNull(result);
        assertEquals(2, result.nodes.size());
    }
    
    @Test
    public void testGetTopologyByTags_MultipleTagsFilter() {
        UUID systemId1 = UUID.randomUUID();
        UUID systemId2 = UUID.randomUUID();
        UUID apiId1 = UUID.randomUUID();
        UUID apiId2 = UUID.randomUUID();
        UUID apiId3 = UUID.randomUUID();
        
        SystemEntity system1 = createSystemEntity(systemId1, "System 1");
        SystemEntity system2 = createSystemEntity(systemId2, "System 2");
        
        ApiEntity api1 = createApiEntity(apiId1, systemId1, "API 1");
        api1.tags = new HashSet<>(Arrays.asList("tag1", "tag2"));
        
        ApiEntity api2 = createApiEntity(apiId2, systemId1, "API 2");
        api2.tags = new HashSet<>(Arrays.asList("tag2", "tag3"));
        
        ApiEntity api3 = createApiEntity(apiId3, systemId2, "API 3");
        api3.tags = new HashSet<>(Arrays.asList("tag4"));
        
        Set<String> filterTags = new HashSet<>(Arrays.asList("tag1", "tag2"));
        
        when(apiRepository.findByTags(filterTags))
            .thenReturn(Uni.createFrom().item(Arrays.asList(api1, api2)));
        when(systemRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(system1, system2)));
        when(relationshipRepository.findAll())
            .thenReturn(Uni.createFrom().item(Collections.emptyList()));
        
        TopologyDTO result = topologyService.getTopologyByTags(filterTags).await().indefinitely();
        
        assertNotNull(result);
        assertEquals(3, result.nodes.size()); // 1 system + 2 APIs
        
        // Verify correct APIs are included
        long apiCount = result.nodes.stream()
            .filter(node -> node.type == EntityType.API)
            .filter(node -> node.name.equals("API 1") || node.name.equals("API 2"))
            .count();
        assertEquals(2, apiCount);
    }
    
    @Test
    public void testGetFullTopology_NodeWithNullFields() {
        UUID systemId = UUID.randomUUID();
        UUID apiId = UUID.randomUUID();
        
        SystemEntity system = createSystemEntity(systemId, "System 1");
        system.description = null;
        
        ApiEntity api = createApiEntity(apiId, systemId, "API 1");
        api.description = null;
        api.department = null;
        api.contactName = null;
        api.contactEmails = null;
        api.specLink = null;
        api.authType = null;
        api.tags = null;
        
        when(systemRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(system)));
        when(apiRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(api)));
        when(relationshipRepository.findAll())
            .thenReturn(Uni.createFrom().item(Collections.emptyList()));
        
        TopologyDTO result = topologyService.getFullTopology().await().indefinitely();
        
        assertNotNull(result);
        assertEquals(2, result.nodes.size());
        
        // Verify system node with null description
        NodeDTO systemNode = result.nodes.stream()
            .filter(node -> node.type == EntityType.SYSTEM)
            .findFirst()
            .orElse(null);
        assertNotNull(systemNode);
        assertNull(systemNode.metadata.get("description"));
        
        // Verify API node with null fields
        NodeDTO apiNode = result.nodes.stream()
            .filter(node -> node.type == EntityType.API)
            .findFirst()
            .orElse(null);
        assertNotNull(apiNode);
        assertNull(apiNode.metadata.get("description"));
        assertNull(apiNode.metadata.get("department"));
        assertNull(apiNode.metadata.get("contactName"));
        assertNull(apiNode.metadata.get("specLink"));
        assertNull(apiNode.metadata.get("authType"));
    }
    
    @Test
    public void testGetFullTopology_EdgeWithNullAuthConfig() {
        UUID systemId = UUID.randomUUID();
        UUID apiId1 = UUID.randomUUID();
        UUID apiId2 = UUID.randomUUID();
        UUID endpointId = UUID.randomUUID();
        UUID relationshipId = UUID.randomUUID();
        
        SystemEntity system = createSystemEntity(systemId, "System 1");
        ApiEntity api1 = createApiEntity(apiId1, systemId, "API 1");
        ApiEntity api2 = createApiEntity(apiId2, systemId, "API 2");
        
        RelationshipEntity relationship = createRelationshipEntity(
            relationshipId, EntityType.API, apiId1, EntityType.API, apiId2, endpointId
        );
        relationship.authConfig = null;
        
        when(systemRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(system)));
        when(apiRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(api1, api2)));
        when(relationshipRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(relationship)));
        
        TopologyDTO result = topologyService.getFullTopology().await().indefinitely();
        
        assertNotNull(result);
        assertEquals(1, result.edges.size());
        
        EdgeDTO edge = result.edges.get(0);
        assertFalse(edge.metadata.containsKey("authConfig"));
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

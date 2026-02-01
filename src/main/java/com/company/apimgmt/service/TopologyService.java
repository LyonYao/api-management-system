package com.company.apimgmt.service;

import com.company.apimgmt.dto.EdgeDTO;
import com.company.apimgmt.dto.NodeDTO;
import com.company.apimgmt.dto.TopologyDTO;
import com.company.apimgmt.entity.ApiEntity;
import com.company.apimgmt.entity.RelationshipEntity;
import com.company.apimgmt.entity.SystemEntity;
import com.company.apimgmt.enums.EntityType;
import com.company.apimgmt.repository.ApiRepository;
import com.company.apimgmt.repository.EndpointRepository;
import com.company.apimgmt.repository.RelationshipRepository;
import com.company.apimgmt.repository.SystemRepository;
import io.smallrye.mutiny.Uni;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import java.util.*;
import java.util.stream.Collectors;

@ApplicationScoped
public class TopologyService {
    
    @Inject
    SystemRepository systemRepository;
    
    @Inject
    ApiRepository apiRepository;
    
    @Inject
    RelationshipRepository relationshipRepository;
    
    @Inject
    EndpointRepository endpointRepository;
    
    public Uni<TopologyDTO> getFullTopology() {
        return Uni.combine().all()
            .unis(
                systemRepository.findAll(),
                apiRepository.findAll(),
                relationshipRepository.findAll()
            )
            .combinedWith((systems, apis, relationships) -> 
                buildTopology(systems, apis, relationships)
            );
    }
    
    public Uni<TopologyDTO> getTopologyByTags(Set<String> tags) {
        if (tags == null || tags.isEmpty()) {
            return getFullTopology();
        }
        
        // Get APIs filtered by tags
        return apiRepository.findByTags(tags)
            .onItem().transformToUni(filteredApis -> {
                // Get systems that contain these APIs
                Set<UUID> systemIds = filteredApis.stream()
                    .map(api -> api.systemId)
                    .collect(Collectors.toSet());
                
                // Get all systems
                return systemRepository.findAll()
                    .onItem().transformToUni(allSystems -> {
                        // Filter systems
                        List<SystemEntity> filteredSystems = allSystems.stream()
                            .filter(system -> systemIds.contains(system.id))
                            .collect(Collectors.toList());
                        
                        // Get all relationships
                        return relationshipRepository.findAll()
                            .onItem().transformToUni(allRelationships -> {
                                // Filter relationships that involve filtered APIs or systems
                                Set<UUID> apiIds = filteredApis.stream()
                                    .map(api -> api.id)
                                    .collect(Collectors.toSet());
                                
                                List<RelationshipEntity> filteredRelationships = allRelationships.stream()
                                    .filter(rel -> isRelationshipRelevant(rel, systemIds, apiIds))
                                    .collect(Collectors.toList());
                                
                                return Uni.createFrom().item(
                                    buildTopology(filteredSystems, filteredApis, filteredRelationships)
                                );
                            });
                    });
            });
    }
    
    private boolean isRelationshipRelevant(RelationshipEntity rel, Set<UUID> systemIds, Set<UUID> apiIds) {
        boolean callerRelevant = 
            (rel.callerType == EntityType.SYSTEM && systemIds.contains(rel.callerId)) ||
            (rel.callerType == EntityType.API && apiIds.contains(rel.callerId));
        
        boolean calleeRelevant = 
            (rel.calleeType == EntityType.SYSTEM && systemIds.contains(rel.calleeId)) ||
            (rel.calleeType == EntityType.API && apiIds.contains(rel.calleeId));
        
        return callerRelevant && calleeRelevant;
    }
    
    private TopologyDTO buildTopology(
            List<SystemEntity> systems,
            List<ApiEntity> apis,
            List<RelationshipEntity> relationships) {
        
        List<NodeDTO> nodes = new ArrayList<>();
        List<EdgeDTO> edges = new ArrayList<>();
        
        // Build system nodes
        for (SystemEntity system : systems) {
            Map<String, Object> metadata = new HashMap<>();
            metadata.put("description", system.description);
            metadata.put("createdAt", system.createdAt.toString());
            
            nodes.add(new NodeDTO(
                system.id,
                system.name,
                EntityType.SYSTEM,
                metadata
            ));
        }
        
        // Build API nodes
        for (ApiEntity api : apis) {
            Map<String, Object> metadata = new HashMap<>();
            metadata.put("description", api.description);
            metadata.put("systemId", api.systemId.toString());
            metadata.put("authType", api.authType != null ? api.authType.name() : null);
            metadata.put("department", api.department);
            metadata.put("contactName", api.contactName);
            metadata.put("contactEmails", api.getContactEmailList());
            metadata.put("specLink", api.specLink);
            metadata.put("tags", api.tags);
            metadata.put("createdAt", api.createdAt.toString());
            
            nodes.add(new NodeDTO(
                api.id,
                api.name,
                EntityType.API,
                metadata
            ));
        }
        
        // Build edges from relationships
        for (RelationshipEntity rel : relationships) {
            Map<String, Object> metadata = new HashMap<>();
            metadata.put("endpointId", rel.endpointId.toString());
            metadata.put("description", rel.description);
            metadata.put("callerType", rel.callerType.name());
            metadata.put("calleeType", rel.calleeType.name());
            
            if (rel.authConfig != null) {
                metadata.put("authConfig", rel.authConfig.getMap());
            }
            
            edges.add(new EdgeDTO(
                rel.id,
                rel.callerId,
                rel.calleeId,
                rel.authType,
                metadata
            ));
        }
        
        return new TopologyDTO(nodes, edges);
    }
}

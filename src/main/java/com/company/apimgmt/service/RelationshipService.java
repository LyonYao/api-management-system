package com.company.apimgmt.service;

import com.company.apimgmt.dto.CreateRelationshipRequest;
import com.company.apimgmt.dto.RelationshipDTO;
import com.company.apimgmt.dto.UpdateRelationshipRequest;
import com.company.apimgmt.entity.RelationshipEntity;
import com.company.apimgmt.enums.EntityType;
import com.company.apimgmt.exception.ResourceNotFoundException;
import com.company.apimgmt.exception.ValidationException;
import com.company.apimgmt.repository.ApiRepository;
import com.company.apimgmt.repository.EndpointRepository;
import com.company.apimgmt.repository.RelationshipRepository;
import com.company.apimgmt.repository.SystemRepository;
import io.smallrye.mutiny.Uni;
import io.vertx.core.json.JsonObject;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

@ApplicationScoped
public class RelationshipService {
    
    @Inject
    RelationshipRepository relationshipRepository;
    
    @Inject
    SystemRepository systemRepository;
    
    @Inject
    ApiRepository apiRepository;
    
    @Inject
    EndpointRepository endpointRepository;
    
    public Uni<RelationshipDTO> createRelationship(CreateRelationshipRequest request) {
        // Validate caller exists
        return validateEntity(request.callerType, request.callerId, "Caller")
            .onItem().transformToUni(callerName -> 
                // Validate callee exists
                validateEntity(request.calleeType, request.calleeId, "Callee")
                    .onItem().transformToUni(calleeName -> 
                        // Validate endpoint exists and belongs to callee
                        validateEndpoint(request.endpointId, request.calleeType, request.calleeId)
                            .onItem().transformToUni(endpoint -> {
                                // Create relationship entity
                                RelationshipEntity entity = new RelationshipEntity();
                                entity.id = UUID.randomUUID();
                                entity.callerType = request.callerType;
                                entity.callerId = request.callerId;
                                entity.calleeType = request.calleeType;
                                entity.calleeId = request.calleeId;
                                entity.endpointId = request.endpointId;
                                entity.authType = request.authType;
                                entity.authConfig = request.authConfig != null ? 
                                    new JsonObject(request.authConfig) : null;
                                entity.description = request.description;
                                entity.createdAt = LocalDateTime.now();
                                entity.updatedAt = LocalDateTime.now();
                                
                                return relationshipRepository.create(entity)
                                    .onItem().transform(created -> 
                                        toDTO(created, callerName, calleeName, 
                                            endpoint.path, endpoint.httpMethod)
                                    );
                            })
                    )
            );
    }
    
    public Uni<RelationshipDTO> getRelationshipById(UUID id) {
        return relationshipRepository.findById(id)
            .onItem().transformToUni(entity -> {
                if (entity == null) {
                    return Uni.createFrom().failure(
                        new ResourceNotFoundException("Relationship", id)
                    );
                }
                return enrichRelationshipDTO(entity);
            });
    }
    
    public Uni<List<RelationshipDTO>> getAllRelationships() {
        return relationshipRepository.findAll()
            .onItem().transformToUni(entities -> {
                List<Uni<RelationshipDTO>> dtoUnis = entities.stream()
                    .map(this::enrichRelationshipDTO)
                    .collect(Collectors.toList());
                
                return Uni.combine().all().unis(dtoUnis)
                    .combinedWith(dtos -> 
                        dtos.stream()
                            .map(dto -> (RelationshipDTO) dto)
                            .collect(Collectors.toList())
                    );
            });
    }
    
    public Uni<List<RelationshipDTO>> getRelationshipsByCaller(EntityType type, UUID id) {
        return relationshipRepository.findByCaller(type, id)
            .onItem().transformToUni(entities -> {
                List<Uni<RelationshipDTO>> dtoUnis = entities.stream()
                    .map(this::enrichRelationshipDTO)
                    .collect(Collectors.toList());
                
                return Uni.combine().all().unis(dtoUnis)
                    .combinedWith(dtos -> 
                        dtos.stream()
                            .map(dto -> (RelationshipDTO) dto)
                            .collect(Collectors.toList())
                    );
            });
    }
    
    public Uni<List<RelationshipDTO>> getRelationshipsByCallee(EntityType type, UUID id) {
        return relationshipRepository.findByCallee(type, id)
            .onItem().transformToUni(entities -> {
                List<Uni<RelationshipDTO>> dtoUnis = entities.stream()
                    .map(this::enrichRelationshipDTO)
                    .collect(Collectors.toList());
                
                return Uni.combine().all().unis(dtoUnis)
                    .combinedWith(dtos -> 
                        dtos.stream()
                            .map(dto -> (RelationshipDTO) dto)
                            .collect(Collectors.toList())
                    );
            });
    }
    
    public Uni<RelationshipDTO> updateRelationship(UUID id, UpdateRelationshipRequest request) {
        return relationshipRepository.findById(id)
            .onItem().transformToUni(entity -> {
                if (entity == null) {
                    return Uni.createFrom().failure(
                        new ResourceNotFoundException("Relationship", id)
                    );
                }
                
                // Determine which fields to validate
                EntityType newCallerType = request.callerType != null ? request.callerType : entity.callerType;
                UUID newCallerId = request.callerId != null ? request.callerId : entity.callerId;
                EntityType newCalleeType = request.calleeType != null ? request.calleeType : entity.calleeType;
                UUID newCalleeId = request.calleeId != null ? request.calleeId : entity.calleeId;
                UUID newEndpointId = request.endpointId != null ? request.endpointId : entity.endpointId;
                
                // Validate caller if changed
                Uni<String> callerValidation = 
                    (request.callerType != null || request.callerId != null) ?
                    validateEntity(newCallerType, newCallerId, "Caller") :
                    getEntityName(entity.callerType, entity.callerId);
                
                return callerValidation.onItem().transformToUni(callerName -> {
                    // Validate callee if changed
                    Uni<String> calleeValidation = 
                        (request.calleeType != null || request.calleeId != null) ?
                        validateEntity(newCalleeType, newCalleeId, "Callee") :
                        getEntityName(entity.calleeType, entity.calleeId);
                    
                    return calleeValidation.onItem().transformToUni(calleeName -> {
                        // Validate endpoint if changed
                        Uni<Void> endpointValidation = 
                            request.endpointId != null ?
                            validateEndpoint(newEndpointId, newCalleeType, newCalleeId)
                                .onItem().transform(e -> null) :
                            Uni.createFrom().voidItem();
                        
                        return endpointValidation.onItem().transformToUni(v -> {
                            // Update entity fields
                            if (request.callerType != null) {
                                entity.callerType = request.callerType;
                            }
                            if (request.callerId != null) {
                                entity.callerId = request.callerId;
                            }
                            if (request.calleeType != null) {
                                entity.calleeType = request.calleeType;
                            }
                            if (request.calleeId != null) {
                                entity.calleeId = request.calleeId;
                            }
                            if (request.endpointId != null) {
                                entity.endpointId = request.endpointId;
                            }
                            if (request.authType != null) {
                                entity.authType = request.authType;
                            }
                            if (request.authConfig != null) {
                                entity.authConfig = new JsonObject(request.authConfig);
                            }
                            if (request.description != null) {
                                entity.description = request.description;
                            }
                            entity.updatedAt = LocalDateTime.now();
                            
                            return relationshipRepository.update(entity)
                                .onItem().transformToUni(this::enrichRelationshipDTO);
                        });
                    });
                });
            });
    }
    
    public Uni<Void> deleteRelationship(UUID id) {
        return relationshipRepository.findById(id)
            .onItem().transformToUni(entity -> {
                if (entity == null) {
                    return Uni.createFrom().failure(
                        new ResourceNotFoundException("Relationship", id)
                    );
                }
                
                return relationshipRepository.delete(id)
                    .onItem().transform(deleted -> null);
            });
    }
    
    private Uni<String> validateEntity(EntityType type, UUID id, String role) {
        if (type == EntityType.SYSTEM) {
            return systemRepository.findById(id)
                .onItem().transform(entity -> {
                    if (entity == null) {
                        throw new ResourceNotFoundException(role + " System", id);
                    }
                    return entity.name;
                });
        } else {
            return apiRepository.findById(id)
                .onItem().transform(entity -> {
                    if (entity == null) {
                        throw new ResourceNotFoundException(role + " API", id);
                    }
                    return entity.name;
                });
        }
    }
    
    private Uni<String> getEntityName(EntityType type, UUID id) {
        if (type == EntityType.SYSTEM) {
            return systemRepository.findById(id)
                .onItem().transform(entity -> entity != null ? entity.name : null);
        } else {
            return apiRepository.findById(id)
                .onItem().transform(entity -> entity != null ? entity.name : null);
        }
    }
    
    private Uni<com.company.apimgmt.entity.EndpointEntity> validateEndpoint(
            UUID endpointId, EntityType calleeType, UUID calleeId) {
        return endpointRepository.findById(endpointId)
            .onItem().transform(endpoint -> {
                if (endpoint == null) {
                    throw new ResourceNotFoundException("Endpoint", endpointId);
                }
                
                // Verify endpoint belongs to the callee
                if (calleeType == EntityType.API) {
                    if (!endpoint.apiId.equals(calleeId)) {
                        throw new ValidationException(
                            "Endpoint does not belong to the specified API"
                        );
                    }
                } else {
                    // For SYSTEM callee, we need to verify the endpoint's API belongs to the system
                    // This will be checked via API lookup
                    return endpoint;
                }
                
                return endpoint;
            })
            .onItem().transformToUni(endpoint -> {
                if (calleeType == EntityType.SYSTEM) {
                    return apiRepository.findById(endpoint.apiId)
                        .onItem().transform(api -> {
                            if (api == null || !api.systemId.equals(calleeId)) {
                                throw new ValidationException(
                                    "Endpoint does not belong to an API in the specified System"
                                );
                            }
                            return endpoint;
                        });
                }
                return Uni.createFrom().item(endpoint);
            });
    }
    
    private Uni<RelationshipDTO> enrichRelationshipDTO(RelationshipEntity entity) {
        return getEntityName(entity.callerType, entity.callerId)
            .onItem().transformToUni(callerName -> 
                getEntityName(entity.calleeType, entity.calleeId)
                    .onItem().transformToUni(calleeName -> 
                        endpointRepository.findById(entity.endpointId)
                            .onItem().transform(endpoint -> 
                                toDTO(entity, callerName, calleeName,
                                    endpoint != null ? endpoint.path : null,
                                    endpoint != null ? endpoint.httpMethod : null)
                            )
                    )
            );
    }
    
    private RelationshipDTO toDTO(RelationshipEntity entity, String callerName, String calleeName,
                                  String endpointPath, com.company.apimgmt.enums.HttpMethod endpointMethod) {
        Map<String, Object> authConfigMap = null;
        if (entity.authConfig != null) {
            authConfigMap = new HashMap<>(entity.authConfig.getMap());
        }
        
        return new RelationshipDTO(
            entity.id,
            entity.callerType,
            entity.callerId,
            callerName,
            entity.calleeType,
            entity.calleeId,
            calleeName,
            entity.endpointId,
            endpointPath,
            endpointMethod,
            entity.authType,
            authConfigMap,
            entity.description,
            entity.createdAt,
            entity.updatedAt
        );
    }
}

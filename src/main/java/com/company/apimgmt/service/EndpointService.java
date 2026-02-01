package com.company.apimgmt.service;

import com.company.apimgmt.dto.CreateEndpointRequest;
import com.company.apimgmt.dto.EndpointDTO;
import com.company.apimgmt.dto.UpdateEndpointRequest;
import com.company.apimgmt.entity.EndpointEntity;
import com.company.apimgmt.exception.DuplicateResourceException;
import com.company.apimgmt.exception.ResourceNotFoundException;
import com.company.apimgmt.repository.ApiRepository;
import com.company.apimgmt.repository.EndpointRepository;
import io.smallrye.mutiny.Uni;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@ApplicationScoped
public class EndpointService {
    
    @Inject
    EndpointRepository endpointRepository;
    
    @Inject
    ApiRepository apiRepository;
    
    public Uni<EndpointDTO> createEndpoint(CreateEndpointRequest request) {
        // Verify API exists
        return apiRepository.findById(request.apiId)
            .onItem().transformToUni(api -> {
                if (api == null) {
                    return Uni.createFrom().failure(
                        new ResourceNotFoundException("API", request.apiId)
                    );
                }
                
                // Check uniqueness of (api_id, path, http_method)
                return endpointRepository.findByApiIdPathAndMethod(
                    request.apiId, request.path, request.httpMethod)
                    .onItem().transformToUni(existing -> {
                        if (existing != null) {
                            return Uni.createFrom().failure(
                                new DuplicateResourceException(
                                    String.format("Endpoint with path '%s' and method '%s' already exists for this API",
                                        request.path, request.httpMethod)
                                )
                            );
                        }
                        
                        // Create endpoint entity
                        EndpointEntity entity = new EndpointEntity();
                        entity.id = UUID.randomUUID();
                        entity.apiId = request.apiId;
                        entity.path = request.path;
                        entity.httpMethod = request.httpMethod;
                        entity.description = request.description;
                        entity.createdAt = LocalDateTime.now();
                        entity.updatedAt = LocalDateTime.now();
                        
                        return endpointRepository.create(entity)
                            .onItem().transform(this::toDTO);
                    });
            });
    }
    
    public Uni<EndpointDTO> getEndpointById(UUID id) {
        return endpointRepository.findById(id)
            .onItem().transform(entity -> {
                if (entity == null) {
                    throw new ResourceNotFoundException("Endpoint", id);
                }
                return toDTO(entity);
            });
    }
    
    public Uni<List<EndpointDTO>> getAllEndpoints() {
        return endpointRepository.findAll()
            .onItem().transform(entities -> 
                entities.stream()
                    .map(this::toDTO)
                    .collect(Collectors.toList())
            );
    }
    
    public Uni<List<EndpointDTO>> getEndpointsByApiId(UUID apiId) {
        return apiRepository.findById(apiId)
            .onItem().transformToUni(api -> {
                if (api == null) {
                    return Uni.createFrom().failure(
                        new ResourceNotFoundException("API", apiId)
                    );
                }
                
                return endpointRepository.findByApiId(apiId)
                    .onItem().transform(entities -> 
                        entities.stream()
                            .map(this::toDTO)
                            .collect(Collectors.toList())
                    );
            });
    }
    
    public Uni<EndpointDTO> updateEndpoint(UUID id, UpdateEndpointRequest request) {
        return endpointRepository.findById(id)
            .onItem().transformToUni(entity -> {
                if (entity == null) {
                    return Uni.createFrom().failure(
                        new ResourceNotFoundException("Endpoint", id)
                    );
                }
                
                // Check uniqueness if path or method is being updated
                boolean pathOrMethodChanged = 
                    (request.path != null && !request.path.equals(entity.path)) ||
                    (request.httpMethod != null && !request.httpMethod.equals(entity.httpMethod));
                
                if (pathOrMethodChanged) {
                    String newPath = request.path != null ? request.path : entity.path;
                    var newMethod = request.httpMethod != null ? request.httpMethod : entity.httpMethod;
                    
                    return endpointRepository.findByApiIdPathAndMethod(entity.apiId, newPath, newMethod)
                        .onItem().transformToUni(existing -> {
                            if (existing != null && !existing.id.equals(id)) {
                                return Uni.createFrom().failure(
                                    new DuplicateResourceException(
                                        String.format("Endpoint with path '%s' and method '%s' already exists for this API",
                                            newPath, newMethod)
                                    )
                                );
                            }
                            return updateEndpointEntity(entity, request);
                        });
                } else {
                    return updateEndpointEntity(entity, request);
                }
            });
    }
    
    private Uni<EndpointDTO> updateEndpointEntity(EndpointEntity entity, UpdateEndpointRequest request) {
        if (request.path != null) {
            entity.path = request.path;
        }
        if (request.httpMethod != null) {
            entity.httpMethod = request.httpMethod;
        }
        if (request.description != null) {
            entity.description = request.description;
        }
        entity.updatedAt = LocalDateTime.now();
        
        return endpointRepository.update(entity)
            .onItem().transform(this::toDTO);
    }
    
    public Uni<Void> deleteEndpoint(UUID id) {
        return endpointRepository.findById(id)
            .onItem().transformToUni(entity -> {
                if (entity == null) {
                    return Uni.createFrom().failure(
                        new ResourceNotFoundException("Endpoint", id)
                    );
                }
                
                return endpointRepository.delete(id)
                    .onItem().transform(deleted -> null);
            });
    }
    
    private EndpointDTO toDTO(EndpointEntity entity) {
        return new EndpointDTO(
            entity.id,
            entity.apiId,
            entity.path,
            entity.httpMethod,
            entity.description,
            entity.createdAt,
            entity.updatedAt
        );
    }
}

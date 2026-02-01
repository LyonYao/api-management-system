package com.company.apimgmt.service;

import com.company.apimgmt.dto.ApiDTO;
import com.company.apimgmt.dto.CreateApiRequest;
import com.company.apimgmt.dto.UpdateApiRequest;
import com.company.apimgmt.entity.ApiEntity;
import com.company.apimgmt.entity.TagEntity;
import com.company.apimgmt.exception.ResourceNotFoundException;
import com.company.apimgmt.exception.ValidationException;
import com.company.apimgmt.repository.ApiRepository;
import com.company.apimgmt.repository.SystemRepository;
import com.company.apimgmt.repository.TagRepository;
import io.smallrye.mutiny.Uni;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import java.time.LocalDateTime;
import java.util.*;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

@ApplicationScoped
public class ApiService {
    
    private static final Pattern EMAIL_PATTERN = Pattern.compile(
        "^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"
    );
    
    @Inject
    ApiRepository apiRepository;
    
    @Inject
    SystemRepository systemRepository;
    
    @Inject
    TagRepository tagRepository;
    
    public Uni<ApiDTO> createApi(CreateApiRequest request) {
        // Validate email formats
        validateEmails(request.contactEmails);
        
        // Verify system exists
        return systemRepository.findById(request.systemId)
            .onItem().transformToUni(system -> {
                if (system == null) {
                    return Uni.createFrom().failure(
                        new ResourceNotFoundException("System", request.systemId)
                    );
                }
                
                // Create API entity
                ApiEntity entity = new ApiEntity();
                entity.id = UUID.randomUUID();
                entity.systemId = request.systemId;
                entity.name = request.name;
                entity.description = request.description;
                entity.authType = request.authType;
                entity.specLink = request.specLink;
                entity.department = request.department;
                entity.contactName = request.contactName;
                entity.setContactEmailList(request.contactEmails);
                entity.createdAt = LocalDateTime.now();
                entity.updatedAt = LocalDateTime.now();
                
                return apiRepository.create(entity)
                    .onItem().transformToUni(createdApi -> {
                        // Handle tags
                        if (request.tags != null && !request.tags.isEmpty()) {
                            return associateTagsToApi(createdApi.id, request.tags)
                                .onItem().transformToUni(v -> 
                                    apiRepository.findById(createdApi.id)
                                        .onItem().transform(api -> toDTO(api, system.name, Collections.emptyList()))
                                );
                        }
                        return Uni.createFrom().item(toDTO(createdApi, system.name, Collections.emptyList()));
                    });
            });
    }
    
    public Uni<ApiDTO> getApiById(UUID id) {
        return apiRepository.findById(id)
            .onItem().transformToUni(entity -> {
                if (entity == null) {
                    return Uni.createFrom().failure(
                        new ResourceNotFoundException("API", id)
                    );
                }
                
                return systemRepository.findById(entity.systemId)
                    .onItem().transform(system -> 
                        toDTO(entity, system != null ? system.name : null, Collections.emptyList())
                    );
            });
    }
    
    public Uni<List<ApiDTO>> getAllApis() {
        return apiRepository.findAll()
            .onItem().transformToUni(this::enrichApisWithSystemNames);
    }
    
    public Uni<List<ApiDTO>> getApisBySystemId(UUID systemId) {
        return systemRepository.findById(systemId)
            .onItem().transformToUni(system -> {
                if (system == null) {
                    return Uni.createFrom().failure(
                        new ResourceNotFoundException("System", systemId)
                    );
                }
                
                return apiRepository.findBySystemId(systemId)
                    .onItem().transform(apis -> 
                        apis.stream()
                            .map(api -> toDTO(api, system.name, Collections.emptyList()))
                            .collect(Collectors.toList())
                    );
            });
    }
    
    public Uni<List<ApiDTO>> getApisByTags(Set<String> tags) {
        if (tags == null || tags.isEmpty()) {
            return getAllApis();
        }
        
        return apiRepository.findByTags(tags)
            .onItem().transformToUni(this::enrichApisWithSystemNames);
    }
    
    public Uni<ApiDTO> updateApi(UUID id, UpdateApiRequest request) {
        // Validate email formats if provided
        if (request.contactEmails != null) {
            validateEmails(request.contactEmails);
        }
        
        return apiRepository.findById(id)
            .onItem().transformToUni(entity -> {
                if (entity == null) {
                    return Uni.createFrom().failure(
                        new ResourceNotFoundException("API", id)
                    );
                }
                
                // Update fields
                if (request.name != null) {
                    entity.name = request.name;
                }
                if (request.description != null) {
                    entity.description = request.description;
                }
                if (request.authType != null) {
                    entity.authType = request.authType;
                }
                if (request.specLink != null) {
                    entity.specLink = request.specLink;
                }
                if (request.department != null) {
                    entity.department = request.department;
                }
                if (request.contactName != null) {
                    entity.contactName = request.contactName;
                }
                if (request.contactEmails != null) {
                    entity.setContactEmailList(request.contactEmails);
                }
                entity.updatedAt = LocalDateTime.now();
                
                return apiRepository.update(entity)
                    .onItem().transformToUni(updatedApi -> {
                        // Handle tags update
                        if (request.tags != null) {
                            return apiRepository.clearTags(id)
                                .onItem().transformToUni(v -> 
                                    associateTagsToApi(id, request.tags)
                                        .onItem().transformToUni(v2 -> 
                                            apiRepository.findById(id)
                                                .onItem().transformToUni(api -> 
                                                    systemRepository.findById(api.systemId)
                                                        .onItem().transform(system -> 
                                                            toDTO(api, system != null ? system.name : null, Collections.emptyList())
                                                        )
                                                )
                                        )
                                );
                        }
                        
                        return systemRepository.findById(updatedApi.systemId)
                            .onItem().transform(system -> 
                                toDTO(updatedApi, system != null ? system.name : null, Collections.emptyList())
                            );
                    });
            });
    }
    
    public Uni<Void> deleteApi(UUID id) {
        return apiRepository.findById(id)
            .onItem().transformToUni(entity -> {
                if (entity == null) {
                    return Uni.createFrom().failure(
                        new ResourceNotFoundException("API", id)
                    );
                }
                
                return apiRepository.delete(id)
                    .onItem().transform(deleted -> null);
            });
    }
    
    private Uni<Void> associateTagsToApi(UUID apiId, Set<String> tagNames) {
        if (tagNames == null || tagNames.isEmpty()) {
            return Uni.createFrom().voidItem();
        }
        
        // Find or create tags
        List<Uni<TagEntity>> tagUnis = tagNames.stream()
            .map(tagRepository::findOrCreate)
            .collect(Collectors.toList());
        
        return Uni.combine().all().unis(tagUnis)
            .combinedWith(tags -> {
                Set<UUID> tagIds = tags.stream()
                    .map(tag -> ((TagEntity) tag).id)
                    .collect(Collectors.toSet());
                return tagIds;
            })
            .onItem().transformToUni(tagIds -> 
                apiRepository.associateTags(apiId, tagIds)
            );
    }
    
    private Uni<List<ApiDTO>> enrichApisWithSystemNames(List<ApiEntity> apis) {
        if (apis.isEmpty()) {
            return Uni.createFrom().item(Collections.emptyList());
        }
        
        // Get unique system IDs
        Set<UUID> systemIds = apis.stream()
            .map(api -> api.systemId)
            .collect(Collectors.toSet());
        
        // Fetch all systems
        return systemRepository.findAll()
            .onItem().transform(systems -> {
                Map<UUID, String> systemNameMap = systems.stream()
                    .collect(Collectors.toMap(s -> s.id, s -> s.name));
                
                return apis.stream()
                    .map(api -> toDTO(api, systemNameMap.get(api.systemId), Collections.emptyList()))
                    .collect(Collectors.toList());
            });
    }
    
    private void validateEmails(List<String> emails) {
        if (emails == null || emails.isEmpty()) {
            throw new ValidationException("At least one contact email is required");
        }
        
        if (emails.size() > 10) {
            throw new ValidationException("Maximum 10 contact emails allowed");
        }
        
        for (String email : emails) {
            if (email == null || email.trim().isEmpty()) {
                throw new ValidationException("Email cannot be empty");
            }
            
            if (!EMAIL_PATTERN.matcher(email.trim()).matches()) {
                throw new ValidationException("Invalid email format: " + email);
            }
        }
    }
    
    private ApiDTO toDTO(ApiEntity entity, String systemName, List<Object> endpoints) {
        return new ApiDTO(
            entity.id,
            entity.systemId,
            systemName,
            entity.name,
            entity.description,
            entity.authType,
            entity.specLink,
            entity.department,
            entity.contactName,
            entity.getContactEmailList(),
            entity.tags,
            Collections.emptyList(), // endpoints will be populated by controller if needed
            entity.createdAt,
            entity.updatedAt
        );
    }
}

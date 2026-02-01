package com.company.apimgmt.service;

import com.company.apimgmt.dto.CreateSystemRequest;
import com.company.apimgmt.dto.SystemDTO;
import com.company.apimgmt.dto.UpdateSystemRequest;
import com.company.apimgmt.entity.SystemEntity;
import com.company.apimgmt.exception.DuplicateResourceException;
import com.company.apimgmt.exception.ResourceNotFoundException;
import com.company.apimgmt.exception.ValidationException;
import com.company.apimgmt.repository.SystemRepository;
import io.smallrye.mutiny.Uni;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@ApplicationScoped
public class SystemService {

    @Inject
    SystemRepository systemRepository;

    public Uni<SystemDTO> createSystem(CreateSystemRequest request) {
        // Validate system name uniqueness
        return systemRepository.findByName(request.name)
                .onItem().transformToUni(existing -> {
                    if (existing != null) {
                        return Uni.createFrom().failure(
                                new DuplicateResourceException("System", "name", request.name));
                    }

                    // Create new system entity
                    SystemEntity entity = new SystemEntity();
                    entity.id = UUID.randomUUID();
                    entity.name = request.name;
                    entity.description = request.description;
                    entity.createdAt = LocalDateTime.now();
                    entity.updatedAt = LocalDateTime.now();

                    return systemRepository.create(entity)
                            .onItem().transform(this::toDTO);
                });
    }

    public Uni<SystemDTO> getSystemById(UUID id) {
        return systemRepository.findById(id)
                .onItem().transform(entity -> {
                    if (entity == null) {
                        throw new ResourceNotFoundException("System", id);
                    }
                    return toDTO(entity);
                });
    }

    public Uni<List<SystemDTO>> getAllSystems() {
        return systemRepository.findAll()
                .onItem().transform(entities -> entities.stream()
                        .map(this::toDTO)
                        .collect(Collectors.toList()));
    }

    public Uni<SystemDTO> updateSystem(UUID id, UpdateSystemRequest request) {
        return systemRepository.findById(id)
                .onItem().transformToUni(entity -> {
                    if (entity == null) {
                        return Uni.createFrom().failure(
                                new ResourceNotFoundException("System", id));
                    }

                    // Check name uniqueness if name is being updated
                    if (request.name != null && !request.name.equals(entity.name)) {
                        return systemRepository.findByName(request.name)
                                .onItem().transformToUni(existing -> {
                                    if (existing != null) {
                                        return Uni.createFrom().failure(
                                                new DuplicateResourceException("System", "name", request.name));
                                    }
                                    return updateSystemEntity(entity, request);
                                });
                    } else {
                        return updateSystemEntity(entity, request);
                    }
                });
    }

    private Uni<SystemDTO> updateSystemEntity(SystemEntity entity, UpdateSystemRequest request) {
        if (request.name != null) {
            entity.name = request.name;
        }
        if (request.description != null) {
            entity.description = request.description;
        }
        entity.updatedAt = LocalDateTime.now();

        return systemRepository.update(entity)
                .onItem().transform(this::toDTO);
    }

    public Uni<Void> deleteSystem(UUID id) {
        return systemRepository.findById(id)
                .onItem().transformToUni(entity -> {
                    if (entity == null) {
                        return Uni.createFrom().failure(
                                new ResourceNotFoundException("System", id));
                    }

                    // Check for cascade constraints - ensure no APIs reference this system
                    return systemRepository.countApisBySystemId(id)
                            .onItem().transformToUni(count -> {
                                if (count > 0) {
                                    return Uni.createFrom().failure(
                                            new ValidationException(
                                                    String.format(
                                                            "Cannot delete system. %d API(s) are still associated with this system",
                                                            count)));
                                }

                                return systemRepository.delete(id)
                                        .onItem().transform(deleted -> null);
                            });
                });
    }

    private SystemDTO toDTO(SystemEntity entity) {
        return new SystemDTO(
                entity.id,
                entity.name,
                entity.description,
                entity.createdAt,
                entity.updatedAt);
    }
}

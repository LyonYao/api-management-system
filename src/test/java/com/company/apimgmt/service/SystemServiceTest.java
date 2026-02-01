package com.company.apimgmt.service;

import com.company.apimgmt.UnitTestProfile;
import com.company.apimgmt.dto.CreateSystemRequest;
import com.company.apimgmt.dto.SystemDTO;
import com.company.apimgmt.dto.UpdateSystemRequest;
import com.company.apimgmt.entity.SystemEntity;
import com.company.apimgmt.exception.DuplicateResourceException;
import com.company.apimgmt.exception.ResourceNotFoundException;
import com.company.apimgmt.exception.ValidationException;
import com.company.apimgmt.repository.SystemRepository;
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
import static org.mockito.Mockito.when;

@QuarkusTest
@TestProfile(UnitTestProfile.class)
public class SystemServiceTest {
    
    @Inject
    SystemService systemService;
    
    @InjectMock
    SystemRepository systemRepository;
    
    @Test
    public void testCreateSystem_Success() {
        CreateSystemRequest request = new CreateSystemRequest();
        request.name = "Test System";
        request.description = "Test Description";
        
        SystemEntity entity = createSystemEntity(UUID.randomUUID(), "Test System", "Test Description");
        
        when(systemRepository.findByName("Test System"))
            .thenReturn(Uni.createFrom().nullItem());
        when(systemRepository.create(any(SystemEntity.class)))
            .thenReturn(Uni.createFrom().item(entity));
        
        SystemDTO result = systemService.createSystem(request).await().indefinitely();
        
        assertNotNull(result);
        assertEquals("Test System", result.name);
        assertEquals("Test Description", result.description);
    }
    
    @Test
    public void testCreateSystem_DuplicateName() {
        CreateSystemRequest request = new CreateSystemRequest();
        request.name = "Duplicate System";
        request.description = "Test";
        
        SystemEntity existing = createSystemEntity(UUID.randomUUID(), "Duplicate System", "Existing");
        
        when(systemRepository.findByName("Duplicate System"))
            .thenReturn(Uni.createFrom().item(existing));
        
        assertThrows(DuplicateResourceException.class, () -> {
            systemService.createSystem(request).await().indefinitely();
        });
    }
    
    @Test
    public void testGetSystemById_Success() {
        UUID id = UUID.randomUUID();
        SystemEntity entity = createSystemEntity(id, "Test System", "Test");
        
        when(systemRepository.findById(id))
            .thenReturn(Uni.createFrom().item(entity));
        
        SystemDTO result = systemService.getSystemById(id).await().indefinitely();
        
        assertNotNull(result);
        assertEquals(id, result.id);
        assertEquals("Test System", result.name);
    }
    
    @Test
    public void testGetSystemById_NotFound() {
        UUID id = UUID.randomUUID();
        
        when(systemRepository.findById(id))
            .thenReturn(Uni.createFrom().nullItem());
        
        assertThrows(ResourceNotFoundException.class, () -> {
            systemService.getSystemById(id).await().indefinitely();
        });
    }
    
    @Test
    public void testGetAllSystems() {
        SystemEntity entity1 = createSystemEntity(UUID.randomUUID(), "System 1", "Desc 1");
        SystemEntity entity2 = createSystemEntity(UUID.randomUUID(), "System 2", "Desc 2");
        
        when(systemRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(entity1, entity2)));
        
        List<SystemDTO> results = systemService.getAllSystems().await().indefinitely();
        
        assertEquals(2, results.size());
        assertEquals("System 1", results.get(0).name);
        assertEquals("System 2", results.get(1).name);
    }
    
    @Test
    public void testUpdateSystem_Success() {
        UUID id = UUID.randomUUID();
        SystemEntity entity = createSystemEntity(id, "Original Name", "Original Desc");
        
        UpdateSystemRequest request = new UpdateSystemRequest();
        request.name = "Updated Name";
        request.description = "Updated Desc";
        
        SystemEntity updated = createSystemEntity(id, "Updated Name", "Updated Desc");
        
        when(systemRepository.findById(id))
            .thenReturn(Uni.createFrom().item(entity));
        when(systemRepository.findByName("Updated Name"))
            .thenReturn(Uni.createFrom().nullItem());
        when(systemRepository.update(any(SystemEntity.class)))
            .thenReturn(Uni.createFrom().item(updated));
        
        SystemDTO result = systemService.updateSystem(id, request).await().indefinitely();
        
        assertEquals("Updated Name", result.name);
        assertEquals("Updated Desc", result.description);
    }
    
    @Test
    public void testUpdateSystem_NotFound() {
        UUID id = UUID.randomUUID();
        UpdateSystemRequest request = new UpdateSystemRequest();
        request.name = "New Name";
        
        when(systemRepository.findById(id))
            .thenReturn(Uni.createFrom().nullItem());
        
        assertThrows(ResourceNotFoundException.class, () -> {
            systemService.updateSystem(id, request).await().indefinitely();
        });
    }
    
    @Test
    public void testUpdateSystem_DuplicateName() {
        UUID id = UUID.randomUUID();
        SystemEntity entity = createSystemEntity(id, "Original", "Desc");
        SystemEntity existing = createSystemEntity(UUID.randomUUID(), "Existing Name", "Desc");
        
        UpdateSystemRequest request = new UpdateSystemRequest();
        request.name = "Existing Name";
        
        when(systemRepository.findById(id))
            .thenReturn(Uni.createFrom().item(entity));
        when(systemRepository.findByName("Existing Name"))
            .thenReturn(Uni.createFrom().item(existing));
        
        assertThrows(DuplicateResourceException.class, () -> {
            systemService.updateSystem(id, request).await().indefinitely();
        });
    }
    
    @Test
    public void testDeleteSystem_Success() {
        UUID id = UUID.randomUUID();
        SystemEntity entity = createSystemEntity(id, "Test System", "Test");
        
        when(systemRepository.findById(id))
            .thenReturn(Uni.createFrom().item(entity));
        when(systemRepository.countApisBySystemId(id))
            .thenReturn(Uni.createFrom().item(0L));
        when(systemRepository.delete(id))
            .thenReturn(Uni.createFrom().item(true));
        
        assertDoesNotThrow(() -> {
            systemService.deleteSystem(id).await().indefinitely();
        });
    }
    
    @Test
    public void testDeleteSystem_NotFound() {
        UUID id = UUID.randomUUID();
        
        when(systemRepository.findById(id))
            .thenReturn(Uni.createFrom().nullItem());
        
        assertThrows(ResourceNotFoundException.class, () -> {
            systemService.deleteSystem(id).await().indefinitely();
        });
    }
    
    @Test
    public void testDeleteSystem_HasAssociatedApis() {
        UUID id = UUID.randomUUID();
        SystemEntity entity = createSystemEntity(id, "Test System", "Test");
        
        when(systemRepository.findById(id))
            .thenReturn(Uni.createFrom().item(entity));
        when(systemRepository.countApisBySystemId(id))
            .thenReturn(Uni.createFrom().item(3L));
        
        assertThrows(ValidationException.class, () -> {
            systemService.deleteSystem(id).await().indefinitely();
        });
    }
    
    private SystemEntity createSystemEntity(UUID id, String name, String description) {
        SystemEntity entity = new SystemEntity();
        entity.id = id;
        entity.name = name;
        entity.description = description;
        entity.createdAt = LocalDateTime.now();
        entity.updatedAt = LocalDateTime.now();
        return entity;
    }
}

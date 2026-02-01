package com.company.apimgmt.service;

import com.company.apimgmt.UnitTestProfile;

import com.company.apimgmt.dto.ApiDTO;
import com.company.apimgmt.dto.CreateApiRequest;
import com.company.apimgmt.dto.UpdateApiRequest;
import com.company.apimgmt.entity.ApiEntity;
import com.company.apimgmt.entity.SystemEntity;
import com.company.apimgmt.enums.AuthType;
import com.company.apimgmt.exception.ResourceNotFoundException;
import com.company.apimgmt.exception.ValidationException;
import com.company.apimgmt.repository.ApiRepository;
import com.company.apimgmt.repository.SystemRepository;
import com.company.apimgmt.repository.TagRepository;
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
public class ApiServiceTest {
    
    @Inject
    ApiService apiService;
    
    @InjectMock
    ApiRepository apiRepository;
    
    @InjectMock
    SystemRepository systemRepository;
    
    @InjectMock
    TagRepository tagRepository;
    
    @Test
    public void testCreateApi_Success() {
        UUID systemId = UUID.randomUUID();
        SystemEntity system = createSystemEntity(systemId, "Test System");
        
        CreateApiRequest request = new CreateApiRequest();
        request.systemId = systemId;
        request.name = "Test API";
        request.description = "Test Description";
        request.authType = AuthType.API_KEY;
        request.department = "Engineering";
        request.contactName = "John Doe";
        request.contactEmails = Arrays.asList("john@example.com");
        
        ApiEntity entity = createApiEntity(UUID.randomUUID(), systemId, "Test API");
        
        when(systemRepository.findById(systemId))
            .thenReturn(Uni.createFrom().item(system));
        when(apiRepository.create(any(ApiEntity.class)))
            .thenReturn(Uni.createFrom().item(entity));
        
        ApiDTO result = apiService.createApi(request).await().indefinitely();
        
        assertNotNull(result);
        assertEquals("Test API", result.name);
        assertEquals(systemId, result.systemId);
    }
    
    @Test
    public void testCreateApi_SystemNotFound() {
        UUID systemId = UUID.randomUUID();
        
        CreateApiRequest request = new CreateApiRequest();
        request.systemId = systemId;
        request.name = "Test API";
        request.contactEmails = Arrays.asList("test@example.com");
        
        when(systemRepository.findById(systemId))
            .thenReturn(Uni.createFrom().nullItem());
        
        assertThrows(ResourceNotFoundException.class, () -> {
            apiService.createApi(request).await().indefinitely();
        });
    }
    
    @Test
    public void testCreateApi_InvalidEmail() {
        UUID systemId = UUID.randomUUID();
        
        CreateApiRequest request = new CreateApiRequest();
        request.systemId = systemId;
        request.name = "Test API";
        request.contactEmails = Arrays.asList("invalid-email");
        
        assertThrows(ValidationException.class, () -> {
            apiService.createApi(request).await().indefinitely();
        });
    }
    
    @Test
    public void testCreateApi_NoEmails() {
        UUID systemId = UUID.randomUUID();
        
        CreateApiRequest request = new CreateApiRequest();
        request.systemId = systemId;
        request.name = "Test API";
        request.contactEmails = Arrays.asList();
        
        assertThrows(ValidationException.class, () -> {
            apiService.createApi(request).await().indefinitely();
        });
    }
    
    @Test
    public void testGetApiById_Success() {
        UUID id = UUID.randomUUID();
        UUID systemId = UUID.randomUUID();
        ApiEntity entity = createApiEntity(id, systemId, "Test API");
        SystemEntity system = createSystemEntity(systemId, "Test System");
        
        when(apiRepository.findById(id))
            .thenReturn(Uni.createFrom().item(entity));
        when(systemRepository.findById(systemId))
            .thenReturn(Uni.createFrom().item(system));
        
        ApiDTO result = apiService.getApiById(id).await().indefinitely();
        
        assertNotNull(result);
        assertEquals(id, result.id);
        assertEquals("Test API", result.name);
    }
    
    @Test
    public void testGetApiById_NotFound() {
        UUID id = UUID.randomUUID();
        
        when(apiRepository.findById(id))
            .thenReturn(Uni.createFrom().nullItem());
        
        assertThrows(ResourceNotFoundException.class, () -> {
            apiService.getApiById(id).await().indefinitely();
        });
    }
    
    @Test
    public void testGetAllApis() {
        UUID systemId = UUID.randomUUID();
        ApiEntity entity1 = createApiEntity(UUID.randomUUID(), systemId, "API 1");
        ApiEntity entity2 = createApiEntity(UUID.randomUUID(), systemId, "API 2");
        SystemEntity system = createSystemEntity(systemId, "Test System");
        
        when(apiRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(entity1, entity2)));
        when(systemRepository.findAll())
            .thenReturn(Uni.createFrom().item(Arrays.asList(system)));
        
        List<ApiDTO> results = apiService.getAllApis().await().indefinitely();
        
        assertEquals(2, results.size());
    }
    
    @Test
    public void testUpdateApi_Success() {
        UUID id = UUID.randomUUID();
        UUID systemId = UUID.randomUUID();
        ApiEntity entity = createApiEntity(id, systemId, "Original Name");
        SystemEntity system = createSystemEntity(systemId, "Test System");
        
        UpdateApiRequest request = new UpdateApiRequest();
        request.name = "Updated Name";
        request.description = "Updated Description";
        
        ApiEntity updated = createApiEntity(id, systemId, "Updated Name");
        
        when(apiRepository.findById(id))
            .thenReturn(Uni.createFrom().item(entity));
        when(apiRepository.update(any(ApiEntity.class)))
            .thenReturn(Uni.createFrom().item(updated));
        when(systemRepository.findById(systemId))
            .thenReturn(Uni.createFrom().item(system));
        
        ApiDTO result = apiService.updateApi(id, request).await().indefinitely();
        
        assertEquals("Updated Name", result.name);
    }
    
    @Test
    public void testUpdateApi_NotFound() {
        UUID id = UUID.randomUUID();
        UpdateApiRequest request = new UpdateApiRequest();
        request.name = "New Name";
        
        when(apiRepository.findById(id))
            .thenReturn(Uni.createFrom().nullItem());
        
        assertThrows(ResourceNotFoundException.class, () -> {
            apiService.updateApi(id, request).await().indefinitely();
        });
    }
    
    @Test
    public void testDeleteApi_Success() {
        UUID id = UUID.randomUUID();
        ApiEntity entity = createApiEntity(id, UUID.randomUUID(), "Test API");
        
        when(apiRepository.findById(id))
            .thenReturn(Uni.createFrom().item(entity));
        when(apiRepository.delete(id))
            .thenReturn(Uni.createFrom().item(true));
        
        assertDoesNotThrow(() -> {
            apiService.deleteApi(id).await().indefinitely();
        });
    }
    
    @Test
    public void testDeleteApi_NotFound() {
        UUID id = UUID.randomUUID();
        
        when(apiRepository.findById(id))
            .thenReturn(Uni.createFrom().nullItem());
        
        assertThrows(ResourceNotFoundException.class, () -> {
            apiService.deleteApi(id).await().indefinitely();
        });
    }
    
    private SystemEntity createSystemEntity(UUID id, String name) {
        SystemEntity entity = new SystemEntity();
        entity.id = id;
        entity.name = name;
        entity.description = "Test";
        entity.createdAt = LocalDateTime.now();
        entity.updatedAt = LocalDateTime.now();
        return entity;
    }
    
    private ApiEntity createApiEntity(UUID id, UUID systemId, String name) {
        ApiEntity entity = new ApiEntity();
        entity.id = id;
        entity.systemId = systemId;
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
}

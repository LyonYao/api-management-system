package com.company.apimgmt.dto;

import com.company.apimgmt.enums.AuthType;
import org.eclipse.microprofile.openapi.annotations.media.Schema;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Set;
import java.util.UUID;

@Schema(description = "API entity information with metadata and endpoints")
public class ApiDTO {
    @Schema(description = "Unique identifier of the API", example = "223e4567-e89b-12d3-a456-426614174001")
    public UUID id;
    
    @Schema(description = "ID of the system this API belongs to", example = "123e4567-e89b-12d3-a456-426614174000")
    public UUID systemId;
    
    @Schema(description = "Name of the system this API belongs to", example = "User Service")
    public String systemName;
    
    @Schema(description = "Name of the API", example = "User Management API", required = true)
    public String name;
    
    @Schema(description = "Description of the API", example = "Provides endpoints for user CRUD operations")
    public String description;
    
    @Schema(description = "Authentication type required for this API", example = "JWT")
    public AuthType authType;
    
    @Schema(description = "Link to the API specification document", example = "https://docs.example.com/api/user-management")
    public String specLink;
    
    @Schema(description = "Department responsible for this API", example = "Engineering")
    public String department;
    
    @Schema(description = "Name of the contact person", example = "John Doe")
    public String contactName;
    
    @Schema(description = "List of contact email addresses", example = "[\"john.doe@example.com\", \"team@example.com\"]")
    public List<String> contactEmails;
    
    @Schema(description = "Tags associated with this API", example = "[\"user\", \"authentication\", \"core\"]")
    public Set<String> tags;
    
    @Schema(description = "List of endpoints belonging to this API")
    public List<EndpointDTO> endpoints;
    
    @Schema(description = "Timestamp when the API was created", example = "2024-01-15T10:30:00")
    public LocalDateTime createdAt;
    
    @Schema(description = "Timestamp when the API was last updated", example = "2024-01-20T14:45:00")
    public LocalDateTime updatedAt;

    public ApiDTO() {
    }

    public ApiDTO(UUID id, UUID systemId, String systemName, String name, String description,
                  AuthType authType, String specLink, String department, String contactName,
                  List<String> contactEmails, Set<String> tags, List<EndpointDTO> endpoints,
                  LocalDateTime createdAt, LocalDateTime updatedAt) {
        this.id = id;
        this.systemId = systemId;
        this.systemName = systemName;
        this.name = name;
        this.description = description;
        this.authType = authType;
        this.specLink = specLink;
        this.department = department;
        this.contactName = contactName;
        this.contactEmails = contactEmails;
        this.tags = tags;
        this.endpoints = endpoints;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }
}

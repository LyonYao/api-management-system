package com.company.apimgmt.dto;

import com.company.apimgmt.enums.AuthType;
import com.company.apimgmt.enums.EntityType;
import com.company.apimgmt.enums.HttpMethod;
import org.eclipse.microprofile.openapi.annotations.media.Schema;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.UUID;

@Schema(description = "API call relationship information between systems or APIs")
public class RelationshipDTO {
    @Schema(description = "Unique identifier of the relationship", example = "423e4567-e89b-12d3-a456-426614174003")
    public UUID id;
    
    @Schema(description = "Type of the caller entity", example = "SYSTEM", enumeration = {"SYSTEM", "API"}, required = true)
    public EntityType callerType;
    
    @Schema(description = "ID of the caller entity", example = "123e4567-e89b-12d3-a456-426614174000", required = true)
    public UUID callerId;
    
    @Schema(description = "Name of the caller entity", example = "Order Service")
    public String callerName;
    
    @Schema(description = "Type of the callee entity", example = "API", enumeration = {"SYSTEM", "API"}, required = true)
    public EntityType calleeType;
    
    @Schema(description = "ID of the callee entity", example = "223e4567-e89b-12d3-a456-426614174001", required = true)
    public UUID calleeId;
    
    @Schema(description = "Name of the callee entity", example = "User Management API")
    public String calleeName;
    
    @Schema(description = "ID of the specific endpoint being called", example = "323e4567-e89b-12d3-a456-426614174002", required = true)
    public UUID endpointId;
    
    @Schema(description = "Path of the endpoint being called", example = "/api/v1/users/{id}")
    public String endpointPath;
    
    @Schema(description = "HTTP method of the endpoint being called", example = "GET")
    public HttpMethod endpointMethod;
    
    @Schema(description = "Authentication type used for this call", example = "JWT")
    public AuthType authType;
    
    @Schema(description = "Authentication configuration details", example = "{\"header\": \"Authorization\", \"prefix\": \"Bearer\"}")
    public Map<String, Object> authConfig;
    
    @Schema(description = "Description of this call relationship", example = "Order service calls user API to validate user permissions")
    public String description;
    
    @Schema(description = "Timestamp when the relationship was created", example = "2024-01-15T10:30:00")
    public LocalDateTime createdAt;
    
    @Schema(description = "Timestamp when the relationship was last updated", example = "2024-01-20T14:45:00")
    public LocalDateTime updatedAt;

    public RelationshipDTO() {
    }

    public RelationshipDTO(UUID id, EntityType callerType, UUID callerId, String callerName,
                          EntityType calleeType, UUID calleeId, String calleeName,
                          UUID endpointId, String endpointPath, HttpMethod endpointMethod,
                          AuthType authType, Map<String, Object> authConfig, String description,
                          LocalDateTime createdAt, LocalDateTime updatedAt) {
        this.id = id;
        this.callerType = callerType;
        this.callerId = callerId;
        this.callerName = callerName;
        this.calleeType = calleeType;
        this.calleeId = calleeId;
        this.calleeName = calleeName;
        this.endpointId = endpointId;
        this.endpointPath = endpointPath;
        this.endpointMethod = endpointMethod;
        this.authType = authType;
        this.authConfig = authConfig;
        this.description = description;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }
}

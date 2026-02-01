package com.company.apimgmt.dto;

import com.company.apimgmt.enums.AuthType;
import com.company.apimgmt.enums.EntityType;
import jakarta.validation.constraints.Size;
import org.eclipse.microprofile.openapi.annotations.media.Schema;

import java.util.Map;
import java.util.UUID;

@Schema(description = "Request to update an existing call relationship")
public class UpdateRelationshipRequest {
    @Schema(description = "Updated caller type", example = "API", enumeration = {"SYSTEM", "API"})
    public EntityType callerType;

    @Schema(description = "Updated caller ID", example = "223e4567-e89b-12d3-a456-426614174001")
    public UUID callerId;

    @Schema(description = "Updated callee type", example = "SYSTEM", enumeration = {"SYSTEM", "API"})
    public EntityType calleeType;

    @Schema(description = "Updated callee ID", example = "123e4567-e89b-12d3-a456-426614174000")
    public UUID calleeId;

    @Schema(description = "Updated endpoint ID", example = "323e4567-e89b-12d3-a456-426614174002")
    public UUID endpointId;

    @Schema(description = "Updated authentication type", example = "OAUTH2", enumeration = {"API_KEY", "OAUTH2", "BASIC_AUTH", "JWT", "NONE"})
    public AuthType authType;

    @Schema(description = "Updated authentication configuration", example = "{\"clientId\": \"abc123\", \"scope\": \"read:users\"}")
    public Map<String, Object> authConfig;

    @Size(max = 2000, message = "Description must not exceed 2000 characters")
    @Schema(description = "Updated description", example = "Order service calls user API with OAuth2 for enhanced security", maxLength = 2000)
    public String description;

    public UpdateRelationshipRequest() {
    }

    public UpdateRelationshipRequest(EntityType callerType, UUID callerId, EntityType calleeType,
                                    UUID calleeId, UUID endpointId, AuthType authType,
                                    Map<String, Object> authConfig, String description) {
        this.callerType = callerType;
        this.callerId = callerId;
        this.calleeType = calleeType;
        this.calleeId = calleeId;
        this.endpointId = endpointId;
        this.authType = authType;
        this.authConfig = authConfig;
        this.description = description;
    }
}

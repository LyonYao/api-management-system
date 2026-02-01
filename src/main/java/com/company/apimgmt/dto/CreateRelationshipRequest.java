package com.company.apimgmt.dto;

import com.company.apimgmt.enums.AuthType;
import com.company.apimgmt.enums.EntityType;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import org.eclipse.microprofile.openapi.annotations.media.Schema;

import java.util.Map;
import java.util.UUID;

@Schema(description = "Request to create a new call relationship")
public class CreateRelationshipRequest {
    @NotNull(message = "Caller type is required")
    @Schema(description = "Type of the caller entity (SYSTEM or API)", example = "SYSTEM", required = true, enumeration = {"SYSTEM", "API"})
    public EntityType callerType;

    @NotNull(message = "Caller ID is required")
    @Schema(description = "ID of the caller entity", example = "123e4567-e89b-12d3-a456-426614174000", required = true)
    public UUID callerId;

    @NotNull(message = "Callee type is required")
    @Schema(description = "Type of the callee entity (SYSTEM or API)", example = "API", required = true, enumeration = {"SYSTEM", "API"})
    public EntityType calleeType;

    @NotNull(message = "Callee ID is required")
    @Schema(description = "ID of the callee entity", example = "223e4567-e89b-12d3-a456-426614174001", required = true)
    public UUID calleeId;

    @NotNull(message = "Endpoint ID is required")
    @Schema(description = "ID of the specific endpoint being called", example = "323e4567-e89b-12d3-a456-426614174002", required = true)
    public UUID endpointId;

    @Schema(description = "Authentication type used for this call", example = "JWT", enumeration = {"API_KEY", "OAUTH2", "BASIC_AUTH", "JWT", "NONE"})
    public AuthType authType;

    @Schema(description = "Authentication configuration details", example = "{\"header\": \"Authorization\", \"prefix\": \"Bearer\"}")
    public Map<String, Object> authConfig;

    @Size(max = 2000, message = "Description must not exceed 2000 characters")
    @Schema(description = "Description of this call relationship", example = "Order service calls user API to validate user permissions", maxLength = 2000)
    public String description;

    public CreateRelationshipRequest() {
    }

    public CreateRelationshipRequest(EntityType callerType, UUID callerId, EntityType calleeType,
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

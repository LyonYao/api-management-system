package com.company.apimgmt.dto;

import com.company.apimgmt.enums.AuthType;
import org.eclipse.microprofile.openapi.annotations.media.Schema;

import java.util.Map;
import java.util.UUID;

@Schema(description = "Edge in the topology graph representing a call relationship")
public class EdgeDTO {
    @Schema(description = "Unique identifier of the relationship", example = "423e4567-e89b-12d3-a456-426614174003")
    public UUID id;
    
    @Schema(description = "ID of the source node (caller)", example = "123e4567-e89b-12d3-a456-426614174000")
    public UUID sourceId;
    
    @Schema(description = "ID of the target node (callee)", example = "223e4567-e89b-12d3-a456-426614174001")
    public UUID targetId;
    
    @Schema(description = "Authentication type used for this call", example = "JWT")
    public AuthType authType;
    
    @Schema(description = "Additional metadata about the relationship", example = "{\"endpointPath\": \"/api/v1/users/{id}\", \"method\": \"GET\"}")
    public Map<String, Object> metadata;

    public EdgeDTO() {
    }

    public EdgeDTO(UUID id, UUID sourceId, UUID targetId, AuthType authType, Map<String, Object> metadata) {
        this.id = id;
        this.sourceId = sourceId;
        this.targetId = targetId;
        this.authType = authType;
        this.metadata = metadata;
    }
}

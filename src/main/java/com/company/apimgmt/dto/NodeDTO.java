package com.company.apimgmt.dto;

import com.company.apimgmt.enums.EntityType;
import org.eclipse.microprofile.openapi.annotations.media.Schema;

import java.util.Map;
import java.util.UUID;

@Schema(description = "Node in the topology graph representing a system or API")
public class NodeDTO {
    @Schema(description = "Unique identifier of the node", example = "123e4567-e89b-12d3-a456-426614174000")
    public UUID id;
    
    @Schema(description = "Name of the node", example = "User Service")
    public String name;
    
    @Schema(description = "Type of the node", example = "SYSTEM", enumeration = {"SYSTEM", "API"})
    public EntityType type;
    
    @Schema(description = "Additional metadata about the node", example = "{\"department\": \"Engineering\", \"tags\": [\"core\", \"user\"]}")
    public Map<String, Object> metadata;

    public NodeDTO() {
    }

    public NodeDTO(UUID id, String name, EntityType type, Map<String, Object> metadata) {
        this.id = id;
        this.name = name;
        this.type = type;
        this.metadata = metadata;
    }
}

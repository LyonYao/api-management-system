package com.company.apimgmt.dto;

import org.eclipse.microprofile.openapi.annotations.media.Schema;

import java.time.LocalDateTime;
import java.util.UUID;

@Schema(description = "System information")
public class SystemDTO {
    @Schema(description = "Unique identifier of the system", example = "123e4567-e89b-12d3-a456-426614174000")
    public UUID id;
    
    @Schema(description = "Name of the system", example = "User Service", required = true)
    public String name;
    
    @Schema(description = "Description of the system", example = "Handles user authentication and profile management")
    public String description;
    
    @Schema(description = "Timestamp when the system was created", example = "2024-01-15T10:30:00")
    public LocalDateTime createdAt;
    
    @Schema(description = "Timestamp when the system was last updated", example = "2024-01-20T14:45:00")
    public LocalDateTime updatedAt;

    public SystemDTO() {
    }

    public SystemDTO(UUID id, String name, String description, LocalDateTime createdAt, LocalDateTime updatedAt) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }
}

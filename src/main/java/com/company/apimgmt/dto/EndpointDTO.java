package com.company.apimgmt.dto;

import com.company.apimgmt.enums.HttpMethod;
import org.eclipse.microprofile.openapi.annotations.media.Schema;

import java.time.LocalDateTime;
import java.util.UUID;

@Schema(description = "API endpoint information")
public class EndpointDTO {
    @Schema(description = "Unique identifier of the endpoint", example = "323e4567-e89b-12d3-a456-426614174002")
    public UUID id;
    
    @Schema(description = "ID of the API this endpoint belongs to", example = "223e4567-e89b-12d3-a456-426614174001")
    public UUID apiId;
    
    @Schema(description = "URL path of the endpoint", example = "/api/v1/users/{id}", required = true)
    public String path;
    
    @Schema(description = "HTTP method for this endpoint", example = "GET", required = true)
    public HttpMethod httpMethod;
    
    @Schema(description = "Description of what this endpoint does", example = "Retrieves a user by their unique identifier")
    public String description;
    
    @Schema(description = "Timestamp when the endpoint was created", example = "2024-01-15T10:30:00")
    public LocalDateTime createdAt;
    
    @Schema(description = "Timestamp when the endpoint was last updated", example = "2024-01-20T14:45:00")
    public LocalDateTime updatedAt;

    public EndpointDTO() {
    }

    public EndpointDTO(UUID id, UUID apiId, String path, HttpMethod httpMethod,
                       String description, LocalDateTime createdAt, LocalDateTime updatedAt) {
        this.id = id;
        this.apiId = apiId;
        this.path = path;
        this.httpMethod = httpMethod;
        this.description = description;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }
}

package com.company.apimgmt.dto;

import com.company.apimgmt.enums.HttpMethod;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import org.eclipse.microprofile.openapi.annotations.media.Schema;

import java.util.UUID;

@Schema(description = "Request to create a new API endpoint")
public class CreateEndpointRequest {
    @NotNull(message = "API ID is required")
    @Schema(description = "ID of the API this endpoint belongs to", example = "223e4567-e89b-12d3-a456-426614174001", required = true)
    public UUID apiId;

    @NotBlank(message = "Path is required")
    @Size(max = 1000, message = "Path must not exceed 1000 characters")
    @Schema(description = "URL path of the endpoint", example = "/api/v1/users/{id}", required = true, maxLength = 1000)
    public String path;

    @NotNull(message = "HTTP method is required")
    @Schema(description = "HTTP method for this endpoint", example = "GET", required = true, enumeration = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"})
    public HttpMethod httpMethod;

    @Size(max = 2000, message = "Description must not exceed 2000 characters")
    @Schema(description = "Description of what this endpoint does", example = "Retrieves a user by their unique identifier", maxLength = 2000)
    public String description;

    public CreateEndpointRequest() {
    }

    public CreateEndpointRequest(UUID apiId, String path, HttpMethod httpMethod, String description) {
        this.apiId = apiId;
        this.path = path;
        this.httpMethod = httpMethod;
        this.description = description;
    }
}

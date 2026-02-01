package com.company.apimgmt.dto;

import com.company.apimgmt.enums.HttpMethod;
import jakarta.validation.constraints.Size;
import org.eclipse.microprofile.openapi.annotations.media.Schema;

@Schema(description = "Request to update an existing endpoint")
public class UpdateEndpointRequest {
    @Size(max = 1000, message = "Path must not exceed 1000 characters")
    @Schema(description = "Updated URL path of the endpoint", example = "/api/v2/users/{id}", maxLength = 1000)
    public String path;

    @Schema(description = "Updated HTTP method", example = "POST", enumeration = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"})
    public HttpMethod httpMethod;

    @Size(max = 2000, message = "Description must not exceed 2000 characters")
    @Schema(description = "Updated description", example = "Creates or updates a user by their unique identifier", maxLength = 2000)
    public String description;

    public UpdateEndpointRequest() {
    }

    public UpdateEndpointRequest(String path, HttpMethod httpMethod, String description) {
        this.path = path;
        this.httpMethod = httpMethod;
        this.description = description;
    }
}

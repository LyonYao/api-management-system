package com.company.apimgmt.dto;

import jakarta.validation.constraints.Size;
import org.eclipse.microprofile.openapi.annotations.media.Schema;

@Schema(description = "Request to update an existing system")
public class UpdateSystemRequest {
    @Size(max = 255, message = "System name must not exceed 255 characters")
    @Schema(description = "Updated name of the system", example = "User Service v2", maxLength = 255)
    public String name;

    @Size(max = 2000, message = "Description must not exceed 2000 characters")
    @Schema(description = "Updated description of the system", example = "Enhanced user authentication and profile management with OAuth2 support", maxLength = 2000)
    public String description;

    public UpdateSystemRequest() {
    }

    public UpdateSystemRequest(String name, String description) {
        this.name = name;
        this.description = description;
    }
}

package com.company.apimgmt.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import org.eclipse.microprofile.openapi.annotations.media.Schema;

@Schema(description = "Request to create a new system")
public class CreateSystemRequest {
    @NotBlank(message = "System name is required")
    @Size(max = 255, message = "System name must not exceed 255 characters")
    @Schema(description = "Name of the system", example = "User Service", required = true, maxLength = 255)
    public String name;

    @Size(max = 2000, message = "Description must not exceed 2000 characters")
    @Schema(description = "Description of the system", example = "Handles user authentication and profile management", maxLength = 2000)
    public String description;

    public CreateSystemRequest() {
    }

    public CreateSystemRequest(String name, String description) {
        this.name = name;
        this.description = description;
    }
}

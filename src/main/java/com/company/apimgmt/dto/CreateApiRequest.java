package com.company.apimgmt.dto;

import com.company.apimgmt.enums.AuthType;
import com.company.apimgmt.validation.ValidEmailList;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import org.eclipse.microprofile.openapi.annotations.media.Schema;

import java.util.List;
import java.util.Set;
import java.util.UUID;

@Schema(description = "Request to create a new API entity")
public class CreateApiRequest {
    @NotNull(message = "System ID is required")
    @Schema(description = "ID of the system this API belongs to", example = "123e4567-e89b-12d3-a456-426614174000", required = true)
    public UUID systemId;

    @NotBlank(message = "API name is required")
    @Size(max = 255, message = "API name must not exceed 255 characters")
    @Schema(description = "Name of the API", example = "User Management API", required = true, maxLength = 255)
    public String name;

    @Size(max = 2000, message = "Description must not exceed 2000 characters")
    @Schema(description = "Description of the API", example = "Provides endpoints for user CRUD operations", maxLength = 2000)
    public String description;

    @Schema(description = "Authentication type required for this API", example = "JWT", enumeration = {"API_KEY", "OAUTH2", "BASIC_AUTH", "JWT", "NONE"})
    public AuthType authType;

    @Size(max = 1000, message = "Spec link must not exceed 1000 characters")
    @Schema(description = "Link to the API specification document", example = "https://docs.example.com/api/user-management", maxLength = 1000)
    public String specLink;

    @Size(max = 255, message = "Department must not exceed 255 characters")
    @Schema(description = "Department responsible for this API", example = "Engineering", maxLength = 255)
    public String department;

    @Size(max = 255, message = "Contact name must not exceed 255 characters")
    @Schema(description = "Name of the contact person", example = "John Doe", maxLength = 255)
    public String contactName;

    @NotNull(message = "Contact emails list is required")
    @ValidEmailList(max = 10, message = "Contact emails must be valid and not exceed 10 addresses")
    @Schema(description = "List of contact email addresses (max 10)", example = "[\"john.doe@example.com\", \"team@example.com\"]", required = true)
    public List<String> contactEmails;

    @Schema(description = "Tags to categorize this API", example = "[\"user\", \"authentication\", \"core\"]")
    public Set<String> tags;

    public CreateApiRequest() {
    }

    public CreateApiRequest(UUID systemId, String name, String description, AuthType authType,
                           String specLink, String department, String contactName,
                           List<String> contactEmails, Set<String> tags) {
        this.systemId = systemId;
        this.name = name;
        this.description = description;
        this.authType = authType;
        this.specLink = specLink;
        this.department = department;
        this.contactName = contactName;
        this.contactEmails = contactEmails;
        this.tags = tags;
    }
}

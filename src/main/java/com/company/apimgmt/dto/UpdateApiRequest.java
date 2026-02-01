package com.company.apimgmt.dto;

import com.company.apimgmt.enums.AuthType;
import com.company.apimgmt.validation.ValidEmailList;
import jakarta.validation.constraints.Size;
import org.eclipse.microprofile.openapi.annotations.media.Schema;

import java.util.List;
import java.util.Set;

@Schema(description = "Request to update an existing API entity")
public class UpdateApiRequest {
    @Size(max = 255, message = "API name must not exceed 255 characters")
    @Schema(description = "Updated name of the API", example = "User Management API v2", maxLength = 255)
    public String name;

    @Size(max = 2000, message = "Description must not exceed 2000 characters")
    @Schema(description = "Updated description of the API", example = "Enhanced user CRUD operations with role-based access", maxLength = 2000)
    public String description;

    @Schema(description = "Updated authentication type", example = "OAUTH2", enumeration = {"API_KEY", "OAUTH2", "BASIC_AUTH", "JWT", "NONE"})
    public AuthType authType;

    @Size(max = 1000, message = "Spec link must not exceed 1000 characters")
    @Schema(description = "Updated link to the API specification", example = "https://docs.example.com/api/user-management/v2", maxLength = 1000)
    public String specLink;

    @Size(max = 255, message = "Department must not exceed 255 characters")
    @Schema(description = "Updated department", example = "Platform Engineering", maxLength = 255)
    public String department;

    @Size(max = 255, message = "Contact name must not exceed 255 characters")
    @Schema(description = "Updated contact person name", example = "Jane Smith", maxLength = 255)
    public String contactName;

    @ValidEmailList(max = 10, message = "Contact emails must be valid and not exceed 10 addresses")
    @Schema(description = "Updated list of contact emails (max 10)", example = "[\"jane.smith@example.com\", \"platform-team@example.com\"]")
    public List<String> contactEmails;

    @Schema(description = "Updated tags", example = "[\"user\", \"oauth2\", \"core\", \"v2\"]")
    public Set<String> tags;

    public UpdateApiRequest() {
    }

    public UpdateApiRequest(String name, String description, AuthType authType, String specLink,
                           String department, String contactName, List<String> contactEmails,
                           Set<String> tags) {
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

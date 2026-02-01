package com.company.apimgmt.dto;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import org.eclipse.microprofile.openapi.annotations.media.Schema;

import java.util.List;
import java.util.UUID;

@Schema(description = "Request to perform batch health checks on multiple endpoints")
public class BatchHealthCheckRequest {
    @NotNull(message = "Endpoint IDs list is required")
    @Size(min = 1, message = "At least one endpoint ID is required")
    @Schema(description = "List of endpoint IDs to check", example = "[\"323e4567-e89b-12d3-a456-426614174002\", \"423e4567-e89b-12d3-a456-426614174003\"]", required = true)
    public List<UUID> endpointIds;

    public BatchHealthCheckRequest() {
    }

    public BatchHealthCheckRequest(List<UUID> endpointIds) {
        this.endpointIds = endpointIds;
    }
}

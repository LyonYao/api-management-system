package com.company.apimgmt.dto;

import org.eclipse.microprofile.openapi.annotations.media.Schema;

import java.time.LocalDateTime;
import java.util.Map;

@Schema(description = "Error response returned when an API request fails")
public class ErrorResponse {
    @Schema(description = "Error type or code", example = "ResourceNotFoundException")
    public String error;
    
    @Schema(description = "Human-readable error message", example = "System with ID 123e4567-e89b-12d3-a456-426614174000 not found")
    public String message;
    
    @Schema(description = "Request path that caused the error", example = "/api/v1/systems/123e4567-e89b-12d3-a456-426614174000")
    public String path;
    
    @Schema(description = "Timestamp when the error occurred", example = "2024-01-20T15:30:00")
    public LocalDateTime timestamp;
    
    @Schema(description = "Additional error details", example = "{\"field\": \"name\", \"issue\": \"must not be blank\"}")
    public Map<String, String> details;

    public ErrorResponse() {
        this.timestamp = LocalDateTime.now();
    }

    public ErrorResponse(String error, String message, String path) {
        this.error = error;
        this.message = message;
        this.path = path;
        this.timestamp = LocalDateTime.now();
    }

    public ErrorResponse(String error, String message, String path, Map<String, String> details) {
        this.error = error;
        this.message = message;
        this.path = path;
        this.timestamp = LocalDateTime.now();
        this.details = details;
    }
}

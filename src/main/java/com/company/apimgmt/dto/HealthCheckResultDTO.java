package com.company.apimgmt.dto;

import com.company.apimgmt.enums.HealthCheckStatus;
import com.company.apimgmt.enums.HttpMethod;
import org.eclipse.microprofile.openapi.annotations.media.Schema;

import java.time.LocalDateTime;
import java.util.UUID;

@Schema(description = "Health check result for an API endpoint")
public class HealthCheckResultDTO {
    @Schema(description = "ID of the endpoint that was checked", example = "323e4567-e89b-12d3-a456-426614174002")
    public UUID endpointId;
    
    @Schema(description = "Path of the endpoint", example = "/api/v1/users/{id}")
    public String endpointPath;
    
    @Schema(description = "HTTP method of the endpoint", example = "GET")
    public HttpMethod httpMethod;
    
    @Schema(description = "Status of the health check", example = "SUCCESS", enumeration = {"SUCCESS", "FAILURE", "TIMEOUT"})
    public HealthCheckStatus status;
    
    @Schema(description = "HTTP response code received", example = "200")
    public Integer responseCode;
    
    @Schema(description = "Response time in milliseconds", example = "145")
    public Integer responseTimeMs;
    
    @Schema(description = "Error message if the check failed", example = "Connection timeout")
    public String errorMessage;
    
    @Schema(description = "Timestamp when the check was performed", example = "2024-01-20T15:30:00")
    public LocalDateTime checkedAt;

    public HealthCheckResultDTO() {
    }

    public HealthCheckResultDTO(UUID endpointId, String endpointPath, HttpMethod httpMethod,
                               HealthCheckStatus status, Integer responseCode, Integer responseTimeMs,
                               String errorMessage, LocalDateTime checkedAt) {
        this.endpointId = endpointId;
        this.endpointPath = endpointPath;
        this.httpMethod = httpMethod;
        this.status = status;
        this.responseCode = responseCode;
        this.responseTimeMs = responseTimeMs;
        this.errorMessage = errorMessage;
        this.checkedAt = checkedAt;
    }
}

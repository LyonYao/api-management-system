package com.company.apimgmt.dto;

import org.eclipse.microprofile.openapi.annotations.media.Schema;

import java.util.List;
import java.util.UUID;

@Schema(description = "Response containing batch health check results")
public class BatchHealthCheckResponse {
    @Schema(description = "Unique identifier for this batch check", example = "523e4567-e89b-12d3-a456-426614174004")
    public UUID batchId;
    
    @Schema(description = "List of health check results for each endpoint")
    public List<HealthCheckResultDTO> results;
    
    @Schema(description = "Total number of endpoints checked", example = "10")
    public int totalCount;
    
    @Schema(description = "Number of successful checks", example = "8")
    public int successCount;
    
    @Schema(description = "Number of failed checks", example = "2")
    public int failureCount;

    public BatchHealthCheckResponse() {
    }

    public BatchHealthCheckResponse(UUID batchId, List<HealthCheckResultDTO> results,
                                   int totalCount, int successCount, int failureCount) {
        this.batchId = batchId;
        this.results = results;
        this.totalCount = totalCount;
        this.successCount = successCount;
        this.failureCount = failureCount;
    }
}

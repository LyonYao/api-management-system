package com.company.apimgmt.controller;

import com.company.apimgmt.dto.BatchHealthCheckRequest;
import com.company.apimgmt.dto.BatchHealthCheckResponse;
import com.company.apimgmt.service.HealthCheckService;
import io.smallrye.mutiny.Uni;
import jakarta.inject.Inject;
import jakarta.validation.Valid;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import org.eclipse.microprofile.openapi.annotations.Operation;
import org.eclipse.microprofile.openapi.annotations.media.Content;
import org.eclipse.microprofile.openapi.annotations.media.Schema;
import org.eclipse.microprofile.openapi.annotations.parameters.Parameter;
import org.eclipse.microprofile.openapi.annotations.responses.APIResponse;
import org.eclipse.microprofile.openapi.annotations.responses.APIResponses;
import org.eclipse.microprofile.openapi.annotations.tags.Tag;

import java.util.UUID;

@Path("/api/v1/health-check")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@Tag(name = "Health Check", description = "API health check operations")
public class HealthCheckController {

    @Inject
    HealthCheckService healthCheckService;

    @POST
    @Path("/batch")
    @Operation(summary = "Batch health check", description = "Performs health checks on multiple endpoints")
    @APIResponses(value = {
        @APIResponse(responseCode = "200", description = "Health check completed",
            content = @Content(schema = @Schema(implementation = BatchHealthCheckResponse.class))),
        @APIResponse(responseCode = "400", description = "Invalid request")
    })
    public Uni<BatchHealthCheckResponse> batchHealthCheck(@Valid BatchHealthCheckRequest request) {
        return healthCheckService.batchHealthCheck(request.endpointIds);
    }

    @POST
    @Path("/system/{systemId}")
    @Operation(summary = "System health check", description = "Performs health checks on all endpoints of a system")
    @APIResponses(value = {
        @APIResponse(responseCode = "200", description = "Health check completed",
            content = @Content(schema = @Schema(implementation = BatchHealthCheckResponse.class))),
        @APIResponse(responseCode = "404", description = "System not found")
    })
    public Uni<BatchHealthCheckResponse> systemHealthCheck(
        @Parameter(description = "System ID", required = true)
        @PathParam("systemId") UUID systemId) {
        return healthCheckService.healthCheckBySystem(systemId);
    }

    @GET
    @Path("/history/{endpointId}")
    @Operation(summary = "Get health check history", description = "Retrieves the health check history for an endpoint")
    @APIResponses(value = {
        @APIResponse(responseCode = "200", description = "History retrieved successfully"),
        @APIResponse(responseCode = "404", description = "Endpoint not found")
    })
    public Uni<java.util.List<com.company.apimgmt.dto.HealthCheckResultDTO>> getHealthCheckHistory(
        @Parameter(description = "Endpoint ID", required = true)
        @PathParam("endpointId") UUID endpointId) {
        return healthCheckService.getHealthCheckHistory(endpointId);
    }
}

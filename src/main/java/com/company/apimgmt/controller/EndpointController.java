package com.company.apimgmt.controller;

import com.company.apimgmt.dto.CreateEndpointRequest;
import com.company.apimgmt.dto.EndpointDTO;
import com.company.apimgmt.dto.UpdateEndpointRequest;
import com.company.apimgmt.service.EndpointService;
import io.smallrye.mutiny.Uni;
import jakarta.inject.Inject;
import jakarta.validation.Valid;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import org.eclipse.microprofile.openapi.annotations.Operation;
import org.eclipse.microprofile.openapi.annotations.media.Content;
import org.eclipse.microprofile.openapi.annotations.media.Schema;
import org.eclipse.microprofile.openapi.annotations.parameters.Parameter;
import org.eclipse.microprofile.openapi.annotations.responses.APIResponse;
import org.eclipse.microprofile.openapi.annotations.responses.APIResponses;
import org.eclipse.microprofile.openapi.annotations.tags.Tag;

import java.util.List;
import java.util.UUID;

@Path("/api/v1/endpoints")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@Tag(name = "Endpoints", description = "API endpoint management operations")
public class EndpointController {

    @Inject
    EndpointService endpointService;

    @POST
    @Operation(summary = "Create a new endpoint", description = "Creates a new endpoint for an API")
    @APIResponses(value = {
        @APIResponse(responseCode = "201", description = "Endpoint created successfully",
            content = @Content(schema = @Schema(implementation = EndpointDTO.class))),
        @APIResponse(responseCode = "400", description = "Invalid request"),
        @APIResponse(responseCode = "404", description = "API not found"),
        @APIResponse(responseCode = "409", description = "Endpoint with same path and method already exists")
    })
    public Uni<Response> createEndpoint(@Valid CreateEndpointRequest request) {
        return endpointService.createEndpoint(request)
            .map(endpoint -> Response.status(Response.Status.CREATED).entity(endpoint).build());
    }

    @GET
    @Path("/{id}")
    @Operation(summary = "Get endpoint by ID", description = "Retrieves detailed information about a specific endpoint")
    @APIResponses(value = {
        @APIResponse(responseCode = "200", description = "Endpoint found",
            content = @Content(schema = @Schema(implementation = EndpointDTO.class))),
        @APIResponse(responseCode = "404", description = "Endpoint not found")
    })
    public Uni<EndpointDTO> getEndpointById(
        @Parameter(description = "Endpoint ID", required = true)
        @PathParam("id") UUID id) {
        return endpointService.getEndpointById(id);
    }

    @PUT
    @Path("/{id}")
    @Operation(summary = "Update endpoint", description = "Updates an existing endpoint's information")
    @APIResponses(value = {
        @APIResponse(responseCode = "200", description = "Endpoint updated successfully",
            content = @Content(schema = @Schema(implementation = EndpointDTO.class))),
        @APIResponse(responseCode = "404", description = "Endpoint not found"),
        @APIResponse(responseCode = "400", description = "Invalid request")
    })
    public Uni<EndpointDTO> updateEndpoint(
        @Parameter(description = "Endpoint ID", required = true)
        @PathParam("id") UUID id,
        @Valid UpdateEndpointRequest request) {
        return endpointService.updateEndpoint(id, request);
    }

    @DELETE
    @Path("/{id}")
    @Operation(summary = "Delete endpoint", description = "Deletes an endpoint")
    @APIResponses(value = {
        @APIResponse(responseCode = "204", description = "Endpoint deleted successfully"),
        @APIResponse(responseCode = "404", description = "Endpoint not found")
    })
    public Uni<Response> deleteEndpoint(
        @Parameter(description = "Endpoint ID", required = true)
        @PathParam("id") UUID id) {
        return endpointService.deleteEndpoint(id)
            .map(deleted -> Response.noContent().build());
    }

    @GET
    @Operation(summary = "List all endpoints", description = "Retrieves a list of all endpoints")
    @APIResponses(value = {
        @APIResponse(responseCode = "200", description = "Endpoints retrieved successfully",
            content = @Content(schema = @Schema(implementation = EndpointDTO.class)))
    })
    public Uni<List<EndpointDTO>> listEndpoints() {
        return endpointService.getAllEndpoints();
    }

    @GET
    @Path("/api/{apiId}")
    @Operation(summary = "Get endpoints by API", description = "Retrieves all endpoints for a specific API")
    @APIResponses(value = {
        @APIResponse(responseCode = "200", description = "Endpoints retrieved successfully",
            content = @Content(schema = @Schema(implementation = EndpointDTO.class))),
        @APIResponse(responseCode = "404", description = "API not found")
    })
    public Uni<List<EndpointDTO>> getEndpointsByApi(
        @Parameter(description = "API ID", required = true)
        @PathParam("apiId") UUID apiId) {
        return endpointService.getEndpointsByApiId(apiId);
    }
}

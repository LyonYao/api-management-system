package com.company.apimgmt.controller;

import com.company.apimgmt.dto.ApiDTO;
import com.company.apimgmt.dto.CreateApiRequest;
import com.company.apimgmt.dto.UpdateApiRequest;
import com.company.apimgmt.service.ApiService;
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
import java.util.Set;
import java.util.UUID;

@Path("/api/v1/apis")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@Tag(name = "APIs", description = "API entity management operations")
public class ApiController {

    @Inject
    ApiService apiService;

    @POST
    @Operation(summary = "Create a new API", description = "Creates a new API entity with metadata and tags")
    @APIResponses(value = {
        @APIResponse(responseCode = "201", description = "API created successfully",
            content = @Content(schema = @Schema(implementation = ApiDTO.class))),
        @APIResponse(responseCode = "400", description = "Invalid request"),
        @APIResponse(responseCode = "404", description = "System not found")
    })
    public Uni<Response> createApi(@Valid CreateApiRequest request) {
        return apiService.createApi(request)
            .map(api -> Response.status(Response.Status.CREATED).entity(api).build());
    }

    @GET
    @Path("/{id}")
    @Operation(summary = "Get API by ID", description = "Retrieves detailed information about a specific API including its endpoints")
    @APIResponses(value = {
        @APIResponse(responseCode = "200", description = "API found",
            content = @Content(schema = @Schema(implementation = ApiDTO.class))),
        @APIResponse(responseCode = "404", description = "API not found")
    })
    public Uni<ApiDTO> getApiById(
        @Parameter(description = "API ID", required = true)
        @PathParam("id") UUID id) {
        return apiService.getApiById(id);
    }

    @PUT
    @Path("/{id}")
    @Operation(summary = "Update API", description = "Updates an existing API's information and tags")
    @APIResponses(value = {
        @APIResponse(responseCode = "200", description = "API updated successfully",
            content = @Content(schema = @Schema(implementation = ApiDTO.class))),
        @APIResponse(responseCode = "404", description = "API not found"),
        @APIResponse(responseCode = "400", description = "Invalid request")
    })
    public Uni<ApiDTO> updateApi(
        @Parameter(description = "API ID", required = true)
        @PathParam("id") UUID id,
        @Valid UpdateApiRequest request) {
        return apiService.updateApi(id, request);
    }

    @DELETE
    @Path("/{id}")
    @Operation(summary = "Delete API", description = "Deletes an API and its associated endpoints")
    @APIResponses(value = {
        @APIResponse(responseCode = "204", description = "API deleted successfully"),
        @APIResponse(responseCode = "404", description = "API not found")
    })
    public Uni<Response> deleteApi(
        @Parameter(description = "API ID", required = true)
        @PathParam("id") UUID id) {
        return apiService.deleteApi(id)
            .map(deleted -> Response.noContent().build());
    }

    @GET
    @Operation(summary = "List APIs", description = "Retrieves a list of APIs with optional tag filtering")
    @APIResponses(value = {
        @APIResponse(responseCode = "200", description = "APIs retrieved successfully",
            content = @Content(schema = @Schema(implementation = ApiDTO.class)))
    })
    public Uni<List<ApiDTO>> listApis(
        @Parameter(description = "Filter by tags (comma-separated)")
        @QueryParam("tags") String tags) {
        if (tags != null && !tags.isEmpty()) {
            Set<String> tagSet = Set.of(tags.split(","));
            return apiService.getApisByTags(tagSet);
        }
        return apiService.getAllApis();
    }

    @GET
    @Path("/search")
    @Operation(summary = "Search APIs by system", description = "Retrieves all APIs belonging to a specific system")
    @APIResponses(value = {
        @APIResponse(responseCode = "200", description = "APIs retrieved successfully",
            content = @Content(schema = @Schema(implementation = ApiDTO.class))),
        @APIResponse(responseCode = "400", description = "System ID is required")
    })
    public Uni<List<ApiDTO>> searchApisBySystem(
        @Parameter(description = "System ID", required = true)
        @QueryParam("systemId") UUID systemId) {
        if (systemId == null) {
            throw new BadRequestException("System ID is required");
        }
        return apiService.getApisBySystemId(systemId);
    }
}

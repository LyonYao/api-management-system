package com.company.apimgmt.controller;

import com.company.apimgmt.dto.CreateSystemRequest;
import com.company.apimgmt.dto.SystemDTO;
import com.company.apimgmt.dto.UpdateSystemRequest;
import com.company.apimgmt.service.SystemService;
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

@Path("/api/v1/systems")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@Tag(name = "Systems", description = "System management operations")
public class SystemController {

    @Inject
    SystemService systemService;

    @POST
    @Operation(
        summary = "Create a new system", 
        description = "Creates a new system in the API management platform. System names must be unique."
    )
    @APIResponses(value = {
        @APIResponse(
            responseCode = "201", 
            description = "System created successfully",
            content = @Content(
                mediaType = MediaType.APPLICATION_JSON,
                schema = @Schema(implementation = SystemDTO.class)
            )
        ),
        @APIResponse(
            responseCode = "400", 
            description = "Invalid request - validation failed",
            content = @Content(
                mediaType = MediaType.APPLICATION_JSON,
                schema = @Schema(implementation = com.company.apimgmt.dto.ErrorResponse.class)
            )
        ),
        @APIResponse(
            responseCode = "409", 
            description = "System with the same name already exists",
            content = @Content(
                mediaType = MediaType.APPLICATION_JSON,
                schema = @Schema(implementation = com.company.apimgmt.dto.ErrorResponse.class)
            )
        ),
        @APIResponse(
            responseCode = "500", 
            description = "Internal server error",
            content = @Content(
                mediaType = MediaType.APPLICATION_JSON,
                schema = @Schema(implementation = com.company.apimgmt.dto.ErrorResponse.class)
            )
        )
    })
    public Uni<Response> createSystem(@Valid CreateSystemRequest request) {
        return systemService.createSystem(request)
            .map(system -> Response.status(Response.Status.CREATED).entity(system).build());
    }

    @GET
    @Path("/{id}")
    @Operation(
        summary = "Get system by ID", 
        description = "Retrieves detailed information about a specific system including its metadata"
    )
    @APIResponses(value = {
        @APIResponse(
            responseCode = "200", 
            description = "System found",
            content = @Content(
                mediaType = MediaType.APPLICATION_JSON,
                schema = @Schema(implementation = SystemDTO.class)
            )
        ),
        @APIResponse(
            responseCode = "404", 
            description = "System not found",
            content = @Content(
                mediaType = MediaType.APPLICATION_JSON,
                schema = @Schema(implementation = com.company.apimgmt.dto.ErrorResponse.class)
            )
        ),
        @APIResponse(
            responseCode = "500", 
            description = "Internal server error",
            content = @Content(
                mediaType = MediaType.APPLICATION_JSON,
                schema = @Schema(implementation = com.company.apimgmt.dto.ErrorResponse.class)
            )
        )
    })
    public Uni<SystemDTO> getSystemById(
        @Parameter(description = "Unique identifier of the system", required = true, example = "123e4567-e89b-12d3-a456-426614174000")
        @PathParam("id") UUID id) {
        return systemService.getSystemById(id);
    }

    @PUT
    @Path("/{id}")
    @Operation(
        summary = "Update system", 
        description = "Updates an existing system's information. Only provided fields will be updated."
    )
    @APIResponses(value = {
        @APIResponse(
            responseCode = "200", 
            description = "System updated successfully",
            content = @Content(
                mediaType = MediaType.APPLICATION_JSON,
                schema = @Schema(implementation = SystemDTO.class)
            )
        ),
        @APIResponse(
            responseCode = "400", 
            description = "Invalid request - validation failed",
            content = @Content(
                mediaType = MediaType.APPLICATION_JSON,
                schema = @Schema(implementation = com.company.apimgmt.dto.ErrorResponse.class)
            )
        ),
        @APIResponse(
            responseCode = "404", 
            description = "System not found",
            content = @Content(
                mediaType = MediaType.APPLICATION_JSON,
                schema = @Schema(implementation = com.company.apimgmt.dto.ErrorResponse.class)
            )
        ),
        @APIResponse(
            responseCode = "500", 
            description = "Internal server error",
            content = @Content(
                mediaType = MediaType.APPLICATION_JSON,
                schema = @Schema(implementation = com.company.apimgmt.dto.ErrorResponse.class)
            )
        )
    })
    public Uni<SystemDTO> updateSystem(
        @Parameter(description = "Unique identifier of the system", required = true, example = "123e4567-e89b-12d3-a456-426614174000")
        @PathParam("id") UUID id,
        @Valid UpdateSystemRequest request) {
        return systemService.updateSystem(id, request);
    }

    @DELETE
    @Path("/{id}")
    @Operation(
        summary = "Delete system", 
        description = "Deletes a system from the platform. This will cascade delete all associated APIs and endpoints."
    )
    @APIResponses(value = {
        @APIResponse(
            responseCode = "204", 
            description = "System deleted successfully"
        ),
        @APIResponse(
            responseCode = "404", 
            description = "System not found",
            content = @Content(
                mediaType = MediaType.APPLICATION_JSON,
                schema = @Schema(implementation = com.company.apimgmt.dto.ErrorResponse.class)
            )
        ),
        @APIResponse(
            responseCode = "409", 
            description = "System cannot be deleted due to existing dependencies",
            content = @Content(
                mediaType = MediaType.APPLICATION_JSON,
                schema = @Schema(implementation = com.company.apimgmt.dto.ErrorResponse.class)
            )
        ),
        @APIResponse(
            responseCode = "500", 
            description = "Internal server error",
            content = @Content(
                mediaType = MediaType.APPLICATION_JSON,
                schema = @Schema(implementation = com.company.apimgmt.dto.ErrorResponse.class)
            )
        )
    })
    public Uni<Response> deleteSystem(
        @Parameter(description = "Unique identifier of the system", required = true, example = "123e4567-e89b-12d3-a456-426614174000")
        @PathParam("id") UUID id) {
        return systemService.deleteSystem(id)
            .map(deleted -> Response.noContent().build());
    }

    @GET
    @Operation(
        summary = "List all systems", 
        description = "Retrieves a list of all systems registered in the platform"
    )
    @APIResponses(value = {
        @APIResponse(
            responseCode = "200", 
            description = "Systems retrieved successfully",
            content = @Content(
                mediaType = MediaType.APPLICATION_JSON,
                schema = @Schema(implementation = SystemDTO.class, type = org.eclipse.microprofile.openapi.annotations.enums.SchemaType.ARRAY)
            )
        ),
        @APIResponse(
            responseCode = "500", 
            description = "Internal server error",
            content = @Content(
                mediaType = MediaType.APPLICATION_JSON,
                schema = @Schema(implementation = com.company.apimgmt.dto.ErrorResponse.class)
            )
        )
    })
    public Uni<List<SystemDTO>> listSystems() {
        return systemService.getAllSystems();
    }
}

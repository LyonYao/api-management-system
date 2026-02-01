package com.company.apimgmt.controller;

import com.company.apimgmt.dto.CreateRelationshipRequest;
import com.company.apimgmt.dto.RelationshipDTO;
import com.company.apimgmt.dto.UpdateRelationshipRequest;
import com.company.apimgmt.service.RelationshipService;
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

@Path("/api/v1/relationships")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@Tag(name = "Relationships", description = "API call relationship management operations")
public class RelationshipController {

    @Inject
    RelationshipService relationshipService;

    @POST
    @Operation(summary = "Create a new relationship", description = "Creates a new call relationship between systems or APIs")
    @APIResponses(value = {
        @APIResponse(responseCode = "201", description = "Relationship created successfully",
            content = @Content(schema = @Schema(implementation = RelationshipDTO.class))),
        @APIResponse(responseCode = "400", description = "Invalid request"),
        @APIResponse(responseCode = "404", description = "Caller, callee, or endpoint not found")
    })
    public Uni<Response> createRelationship(@Valid CreateRelationshipRequest request) {
        return relationshipService.createRelationship(request)
            .map(relationship -> Response.status(Response.Status.CREATED).entity(relationship).build());
    }

    @GET
    @Path("/{id}")
    @Operation(summary = "Get relationship by ID", description = "Retrieves detailed information about a specific call relationship")
    @APIResponses(value = {
        @APIResponse(responseCode = "200", description = "Relationship found",
            content = @Content(schema = @Schema(implementation = RelationshipDTO.class))),
        @APIResponse(responseCode = "404", description = "Relationship not found")
    })
    public Uni<RelationshipDTO> getRelationshipById(
        @Parameter(description = "Relationship ID", required = true)
        @PathParam("id") UUID id) {
        return relationshipService.getRelationshipById(id);
    }

    @PUT
    @Path("/{id}")
    @Operation(summary = "Update relationship", description = "Updates an existing call relationship")
    @APIResponses(value = {
        @APIResponse(responseCode = "200", description = "Relationship updated successfully",
            content = @Content(schema = @Schema(implementation = RelationshipDTO.class))),
        @APIResponse(responseCode = "404", description = "Relationship not found"),
        @APIResponse(responseCode = "400", description = "Invalid request")
    })
    public Uni<RelationshipDTO> updateRelationship(
        @Parameter(description = "Relationship ID", required = true)
        @PathParam("id") UUID id,
        @Valid UpdateRelationshipRequest request) {
        return relationshipService.updateRelationship(id, request);
    }

    @DELETE
    @Path("/{id}")
    @Operation(summary = "Delete relationship", description = "Deletes a call relationship")
    @APIResponses(value = {
        @APIResponse(responseCode = "204", description = "Relationship deleted successfully"),
        @APIResponse(responseCode = "404", description = "Relationship not found")
    })
    public Uni<Response> deleteRelationship(
        @Parameter(description = "Relationship ID", required = true)
        @PathParam("id") UUID id) {
        return relationshipService.deleteRelationship(id)
            .map(deleted -> Response.noContent().build());
    }

    @GET
    @Operation(summary = "List all relationships", description = "Retrieves a list of all call relationships")
    @APIResponses(value = {
        @APIResponse(responseCode = "200", description = "Relationships retrieved successfully",
            content = @Content(schema = @Schema(implementation = RelationshipDTO.class)))
    })
    public Uni<List<RelationshipDTO>> listRelationships() {
        return relationshipService.getAllRelationships();
    }
}

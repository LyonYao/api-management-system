package com.company.apimgmt.controller;

import com.company.apimgmt.dto.TopologyDTO;
import com.company.apimgmt.service.TopologyService;
import io.smallrye.mutiny.Uni;
import jakarta.inject.Inject;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import org.eclipse.microprofile.openapi.annotations.Operation;
import org.eclipse.microprofile.openapi.annotations.media.Content;
import org.eclipse.microprofile.openapi.annotations.media.Schema;
import org.eclipse.microprofile.openapi.annotations.parameters.Parameter;
import org.eclipse.microprofile.openapi.annotations.responses.APIResponse;
import org.eclipse.microprofile.openapi.annotations.responses.APIResponses;
import org.eclipse.microprofile.openapi.annotations.tags.Tag;

import java.util.Set;

@Path("/api/v1/topology")
@Produces(MediaType.APPLICATION_JSON)
@Tag(name = "Topology", description = "API topology visualization operations")
public class TopologyController {

    @Inject
    TopologyService topologyService;

    @GET
    @Operation(summary = "Get complete topology", description = "Retrieves the complete topology graph of all systems, APIs, and their relationships")
    @APIResponses(value = {
        @APIResponse(responseCode = "200", description = "Topology retrieved successfully",
            content = @Content(schema = @Schema(implementation = TopologyDTO.class)))
    })
    public Uni<TopologyDTO> getTopology() {
        return topologyService.getFullTopology();
    }

    @GET
    @Path("/filter")
    @Operation(summary = "Get filtered topology", description = "Retrieves a filtered topology graph based on tags")
    @APIResponses(value = {
        @APIResponse(responseCode = "200", description = "Filtered topology retrieved successfully",
            content = @Content(schema = @Schema(implementation = TopologyDTO.class)))
    })
    public Uni<TopologyDTO> getFilteredTopology(
        @Parameter(description = "Filter by tags (comma-separated)")
        @QueryParam("tags") String tags) {
        if (tags != null && !tags.isEmpty()) {
            Set<String> tagSet = Set.of(tags.split(","));
            return topologyService.getTopologyByTags(tagSet);
        }
        return topologyService.getFullTopology();
    }
}

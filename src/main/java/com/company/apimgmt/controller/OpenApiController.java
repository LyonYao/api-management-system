package com.company.apimgmt.controller;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.PathParam;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import org.eclipse.microprofile.openapi.annotations.Operation;
import org.eclipse.microprofile.openapi.annotations.responses.APIResponse;
import org.eclipse.microprofile.openapi.annotations.responses.APIResponses;
import org.eclipse.microprofile.openapi.annotations.tags.Tag;

import java.net.URI;

/**
 * Controller for OpenAPI specification access.
 * 
 * Note: Quarkus automatically generates the OpenAPI specification at /api/v1/openapi
 * based on the configuration in application.properties. This controller provides
 * additional convenience endpoints and documentation.
 */
@Path("/api/v1")
@Tag(name = "OpenAPI", description = "OpenAPI specification access")
public class OpenApiController {

    @GET
    @Path("/openapi.json")
    @Produces(MediaType.APPLICATION_JSON)
    @Operation(summary = "Get OpenAPI specification", 
               description = "Retrieves the OpenAPI 3.0 specification document in JSON format")
    @APIResponses(value = {
        @APIResponse(responseCode = "307", description = "Redirect to OpenAPI specification"),
        @APIResponse(responseCode = "200", description = "OpenAPI specification retrieved successfully")
    })
    public Response getOpenApiJson() {
        // Redirect to the Quarkus-generated OpenAPI endpoint
        return Response.temporaryRedirect(URI.create("/api/v1/openapi")).build();
    }

    @GET
    @Path("/openapi.yaml")
    @Produces("application/x-yaml")
    @Operation(summary = "Get OpenAPI specification in YAML", 
               description = "Retrieves the OpenAPI 3.0 specification document in YAML format")
    @APIResponses(value = {
        @APIResponse(responseCode = "307", description = "Redirect to OpenAPI specification"),
        @APIResponse(responseCode = "200", description = "OpenAPI specification retrieved successfully")
    })
    public Response getOpenApiYaml() {
        // Redirect to the Quarkus-generated OpenAPI endpoint with YAML format
        return Response.temporaryRedirect(URI.create("/api/v1/openapi?format=yaml")).build();
    }

    @GET
    @Path("/swagger-ui{tail:.*}")
    @Operation(summary = "Swagger UI redirect", description = "Redirects any swagger-ui variant to the hosted Swagger UI")
    @APIResponses(value = {
        @APIResponse(responseCode = "307", description = "Redirect to Swagger UI")
    })
    public Response redirectSwaggerUi(@PathParam("tail") String tail) {
        return Response.temporaryRedirect(URI.create("/q/swagger-ui?url=/api/v1/openapi")).build();
    }
}

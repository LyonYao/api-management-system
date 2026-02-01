package com.company.apimgmt;

import jakarta.ws.rs.ApplicationPath;
import jakarta.ws.rs.core.Application;
import org.eclipse.microprofile.openapi.annotations.OpenAPIDefinition;
import org.eclipse.microprofile.openapi.annotations.enums.SecuritySchemeType;
import org.eclipse.microprofile.openapi.annotations.info.Contact;
import org.eclipse.microprofile.openapi.annotations.info.Info;
import org.eclipse.microprofile.openapi.annotations.info.License;
import org.eclipse.microprofile.openapi.annotations.security.SecurityScheme;
import org.eclipse.microprofile.openapi.annotations.servers.Server;
import org.eclipse.microprofile.openapi.annotations.tags.Tag;

@ApplicationPath("/")
@OpenAPIDefinition(
    info = @Info(
        title = "API Management System",
        version = "1.0.0",
        description = "Microservice API management and topology visualization system. " +
                      "This system provides comprehensive API metadata management, call relationship tracking, " +
                      "topology visualization, and health check capabilities for microservice architectures.",
        contact = @Contact(
            name = "API Management Team",
            email = "api-management@company.com"
        ),
        license = @License(
            name = "Proprietary",
            url = "https://company.com/license"
        )
    ),
    servers = {
        @Server(url = "http://localhost:8080", description = "Development Server"),
        @Server(url = "https://api.company.com", description = "Production Server")
    },
    tags = {
        @Tag(name = "Systems", description = "System management operations"),
        @Tag(name = "APIs", description = "API entity management operations"),
        @Tag(name = "Endpoints", description = "API endpoint management operations"),
        @Tag(name = "Relationships", description = "API call relationship management operations"),
        @Tag(name = "Topology", description = "API topology visualization operations"),
        @Tag(name = "Health Check", description = "API health check operations"),
        @Tag(name = "OpenAPI", description = "OpenAPI specification access")
    }
)
@SecurityScheme(
    securitySchemeName = "bearerAuth",
    type = SecuritySchemeType.HTTP,
    scheme = "bearer",
    bearerFormat = "JWT",
    description = "JWT Bearer token authentication. Include the token in the Authorization header as: Bearer <token>"
)
public class ApiManagementApplication extends Application {
    // JAX-RS application configuration
}

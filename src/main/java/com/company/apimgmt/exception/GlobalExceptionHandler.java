package com.company.apimgmt.exception;

import com.company.apimgmt.dto.ErrorResponse;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.ConstraintViolationException;
import jakarta.ws.rs.core.Context;
import jakarta.ws.rs.core.Response;
import jakarta.ws.rs.core.UriInfo;
import jakarta.ws.rs.ext.ExceptionMapper;
import jakarta.ws.rs.ext.Provider;

import java.util.HashMap;
import java.util.Map;
import java.util.stream.Collectors;

@Provider
public class GlobalExceptionHandler implements ExceptionMapper<Exception> {

    @Context
    UriInfo uriInfo;

    @Override
    public Response toResponse(Exception exception) {
        if (exception instanceof ResourceNotFoundException) {
            return handleResourceNotFoundException((ResourceNotFoundException) exception);
        } else if (exception instanceof DuplicateResourceException) {
            return handleDuplicateResourceException((DuplicateResourceException) exception);
        } else if (exception instanceof ValidationException) {
            return handleValidationException((ValidationException) exception);
        } else if (exception instanceof ConstraintViolationException) {
            return handleConstraintViolationException((ConstraintViolationException) exception);
        } else if (exception instanceof IllegalArgumentException) {
            return handleIllegalArgumentException((IllegalArgumentException) exception);
        } else {
            return handleGenericException(exception);
        }
    }

    private Response handleResourceNotFoundException(ResourceNotFoundException exception) {
        ErrorResponse errorResponse = new ErrorResponse(
            "NOT_FOUND",
            exception.getMessage(),
            getPath()
        );
        return Response.status(Response.Status.NOT_FOUND)
                .entity(errorResponse)
                .build();
    }

    private Response handleDuplicateResourceException(DuplicateResourceException exception) {
        ErrorResponse errorResponse = new ErrorResponse(
            "CONFLICT",
            exception.getMessage(),
            getPath()
        );
        return Response.status(Response.Status.CONFLICT)
                .entity(errorResponse)
                .build();
    }

    private Response handleValidationException(ValidationException exception) {
        ErrorResponse errorResponse = new ErrorResponse(
            "VALIDATION_ERROR",
            exception.getMessage(),
            getPath(),
            exception.getErrors()
        );
        return Response.status(Response.Status.BAD_REQUEST)
                .entity(errorResponse)
                .build();
    }

    private Response handleConstraintViolationException(ConstraintViolationException exception) {
        Map<String, String> errors = exception.getConstraintViolations().stream()
                .collect(Collectors.toMap(
                    violation -> getFieldName(violation),
                    ConstraintViolation::getMessage,
                    (existing, replacement) -> existing
                ));

        ErrorResponse errorResponse = new ErrorResponse(
            "VALIDATION_ERROR",
            "Request validation failed",
            getPath(),
            errors
        );
        return Response.status(Response.Status.BAD_REQUEST)
                .entity(errorResponse)
                .build();
    }

    private Response handleIllegalArgumentException(IllegalArgumentException exception) {
        ErrorResponse errorResponse = new ErrorResponse(
            "BAD_REQUEST",
            exception.getMessage(),
            getPath()
        );
        return Response.status(Response.Status.BAD_REQUEST)
                .entity(errorResponse)
                .build();
    }

    private Response handleGenericException(Exception exception) {
        ErrorResponse errorResponse = new ErrorResponse(
            "INTERNAL_SERVER_ERROR",
            "An unexpected error occurred: " + exception.getMessage(),
            getPath()
        );
        return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                .entity(errorResponse)
                .build();
    }

    private String getPath() {
        return uriInfo != null ? uriInfo.getPath() : "unknown";
    }

    private String getFieldName(ConstraintViolation<?> violation) {
        String propertyPath = violation.getPropertyPath().toString();
        // Extract the field name from the property path
        String[] parts = propertyPath.split("\\.");
        return parts[parts.length - 1];
    }
}

package com.company.apimgmt.service;

import com.company.apimgmt.dto.BatchHealthCheckResponse;
import com.company.apimgmt.dto.HealthCheckResultDTO;
import com.company.apimgmt.entity.EndpointEntity;
import com.company.apimgmt.entity.HealthCheckResultEntity;
import com.company.apimgmt.enums.HealthCheckStatus;
import com.company.apimgmt.exception.ResourceNotFoundException;
import com.company.apimgmt.repository.ApiRepository;
import com.company.apimgmt.repository.EndpointRepository;
import com.company.apimgmt.repository.HealthCheckResultRepository;
import io.smallrye.mutiny.Uni;
import io.vertx.mutiny.core.Vertx;
import io.vertx.mutiny.ext.web.client.WebClient;
import io.vertx.ext.web.client.WebClientOptions;
import jakarta.annotation.PostConstruct;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@ApplicationScoped
public class HealthCheckService {
    
    private static final int REQUEST_TIMEOUT_MS = 5000;
    
    @Inject
    EndpointRepository endpointRepository;
    
    @Inject
    ApiRepository apiRepository;
    
    @Inject
    HealthCheckResultRepository healthCheckResultRepository;
    
    @Inject
    Vertx vertx;
    
    private WebClient webClient;
    
    @PostConstruct
    void init() {
        WebClientOptions options = new WebClientOptions()
            .setConnectTimeout(REQUEST_TIMEOUT_MS)
            .setIdleTimeout(REQUEST_TIMEOUT_MS);
        webClient = WebClient.create(vertx, options);
    }
    
    public Uni<BatchHealthCheckResponse> batchHealthCheck(List<UUID> endpointIds) {
        UUID batchId = UUID.randomUUID();
        
        // Perform health checks for all endpoints
        List<Uni<HealthCheckResultDTO>> checkUnis = endpointIds.stream()
            .map(this::performHealthCheck)
            .collect(Collectors.toList());
        
        return Uni.combine().all().unis(checkUnis)
            .combinedWith(results -> {
                List<HealthCheckResultDTO> resultList = results.stream()
                    .map(r -> (HealthCheckResultDTO) r)
                    .collect(Collectors.toList());
                
                int successCount = (int) resultList.stream()
                    .filter(r -> r.status == HealthCheckStatus.SUCCESS)
                    .count();
                
                int failureCount = resultList.size() - successCount;
                
                return new BatchHealthCheckResponse(
                    batchId,
                    resultList,
                    resultList.size(),
                    successCount,
                    failureCount
                );
            });
    }
    
    public Uni<BatchHealthCheckResponse> healthCheckBySystem(UUID systemId) {
        // Get all APIs for the system
        return apiRepository.findBySystemId(systemId)
            .onItem().transformToUni(apis -> {
                if (apis.isEmpty()) {
                    return Uni.createFrom().failure(
                        new ResourceNotFoundException("No APIs found for System", systemId)
                    );
                }
                
                // Get all endpoint IDs for these APIs
                List<UUID> apiIds = apis.stream()
                    .map(api -> api.id)
                    .collect(Collectors.toList());
                
                // Get all endpoints for these APIs
                List<Uni<List<EndpointEntity>>> endpointUnis = apiIds.stream()
                    .map(endpointRepository::findByApiId)
                    .collect(Collectors.toList());
                
                return Uni.combine().all().unis(endpointUnis)
                    .combinedWith(endpointLists -> {
                        List<UUID> endpointIds = endpointLists.stream()
                            .flatMap(list -> ((List<EndpointEntity>) list).stream())
                            .map(endpoint -> endpoint.id)
                            .collect(Collectors.toList());
                        
                        return endpointIds;
                    })
                    .onItem().transformToUni(this::batchHealthCheck);
            });
    }
    
    public Uni<HealthCheckResultDTO> performHealthCheck(UUID endpointId) {
        return endpointRepository.findById(endpointId)
            .onItem().transformToUni(endpoint -> {
                if (endpoint == null) {
                    return Uni.createFrom().failure(
                        new ResourceNotFoundException("Endpoint", endpointId)
                    );
                }
                
                return executeHealthCheck(endpoint)
                    .onItem().transformToUni(result -> 
                        saveHealthCheckResult(result)
                            .onItem().transform(saved -> 
                                toDTO(saved, endpoint.path, endpoint.httpMethod)
                            )
                    );
            });
    }
    
    private Uni<HealthCheckResultEntity> executeHealthCheck(EndpointEntity endpoint) {
        long startTime = System.currentTimeMillis();
        
        // Build the request based on HTTP method
        var request = switch (endpoint.httpMethod) {
            case GET -> webClient.getAbs(endpoint.path);
            case POST -> webClient.postAbs(endpoint.path);
            case PUT -> webClient.putAbs(endpoint.path);
            case DELETE -> webClient.deleteAbs(endpoint.path);
            case PATCH -> webClient.patchAbs(endpoint.path);
            case HEAD -> webClient.headAbs(endpoint.path);
            case OPTIONS -> webClient.requestAbs(io.vertx.core.http.HttpMethod.OPTIONS, endpoint.path);
        };
        
        return request.send()
            .onItem().transform(response -> {
                long endTime = System.currentTimeMillis();
                int responseTimeMs = (int) (endTime - startTime);
                
                HealthCheckResultEntity result = new HealthCheckResultEntity();
                result.id = UUID.randomUUID();
                result.endpointId = endpoint.id;
                result.responseCode = response.statusCode();
                result.responseTimeMs = responseTimeMs;
                result.checkedAt = LocalDateTime.now();
                
                // Consider 2xx and 3xx as success
                if (response.statusCode() >= 200 && response.statusCode() < 400) {
                    result.status = HealthCheckStatus.SUCCESS;
                } else {
                    result.status = HealthCheckStatus.FAILURE;
                    result.errorMessage = "HTTP " + response.statusCode() + ": " + response.statusMessage();
                }
                
                return result;
            })
            .onFailure().recoverWithItem(throwable -> {
                long endTime = System.currentTimeMillis();
                int responseTimeMs = (int) (endTime - startTime);
                
                HealthCheckResultEntity result = new HealthCheckResultEntity();
                result.id = UUID.randomUUID();
                result.endpointId = endpoint.id;
                result.responseTimeMs = responseTimeMs;
                result.checkedAt = LocalDateTime.now();
                
                // Determine if it's a timeout or other failure
                if (throwable.getMessage() != null && 
                    (throwable.getMessage().contains("timeout") || 
                     throwable.getMessage().contains("timed out"))) {
                    result.status = HealthCheckStatus.TIMEOUT;
                    result.errorMessage = "Request timeout after " + REQUEST_TIMEOUT_MS + "ms";
                } else {
                    result.status = HealthCheckStatus.FAILURE;
                    result.errorMessage = throwable.getMessage();
                }
                
                return result;
            });
    }
    
    private Uni<HealthCheckResultEntity> saveHealthCheckResult(HealthCheckResultEntity result) {
        return healthCheckResultRepository.create(result);
    }
    
    public Uni<List<HealthCheckResultDTO>> getHealthCheckHistory(UUID endpointId) {
        return endpointRepository.findById(endpointId)
            .onItem().transformToUni(endpoint -> {
                if (endpoint == null) {
                    return Uni.createFrom().failure(
                        new ResourceNotFoundException("Endpoint", endpointId)
                    );
                }
                
                return healthCheckResultRepository.findByEndpointId(endpointId)
                    .onItem().transform(results -> 
                        results.stream()
                            .map(result -> toDTO(result, endpoint.path, endpoint.httpMethod))
                            .collect(Collectors.toList())
                    );
            });
    }
    
    private HealthCheckResultDTO toDTO(HealthCheckResultEntity entity, String path, 
                                      com.company.apimgmt.enums.HttpMethod method) {
        return new HealthCheckResultDTO(
            entity.endpointId,
            path,
            method,
            entity.status,
            entity.responseCode,
            entity.responseTimeMs,
            entity.errorMessage,
            entity.checkedAt
        );
    }
}

package com.company.apimgmt.entity;

import com.company.apimgmt.enums.HealthCheckStatus;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * 健康检查结果实体类
 * 对应health_check_results表
 */
public class HealthCheckResultEntity {
    public UUID id;
    public UUID endpointId;
    public HealthCheckStatus status;
    public Integer responseCode;
    public Integer responseTimeMs;
    public String errorMessage;
    public LocalDateTime checkedAt;

    public HealthCheckResultEntity() {
    }

    public HealthCheckResultEntity(UUID id, UUID endpointId, HealthCheckStatus status,
                                   Integer responseCode, Integer responseTimeMs,
                                   String errorMessage, LocalDateTime checkedAt) {
        this.id = id;
        this.endpointId = endpointId;
        this.status = status;
        this.responseCode = responseCode;
        this.responseTimeMs = responseTimeMs;
        this.errorMessage = errorMessage;
        this.checkedAt = checkedAt;
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public UUID getEndpointId() {
        return endpointId;
    }

    public void setEndpointId(UUID endpointId) {
        this.endpointId = endpointId;
    }

    public HealthCheckStatus getStatus() {
        return status;
    }

    public void setStatus(HealthCheckStatus status) {
        this.status = status;
    }

    public Integer getResponseCode() {
        return responseCode;
    }

    public void setResponseCode(Integer responseCode) {
        this.responseCode = responseCode;
    }

    public Integer getResponseTimeMs() {
        return responseTimeMs;
    }

    public void setResponseTimeMs(Integer responseTimeMs) {
        this.responseTimeMs = responseTimeMs;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    public LocalDateTime getCheckedAt() {
        return checkedAt;
    }

    public void setCheckedAt(LocalDateTime checkedAt) {
        this.checkedAt = checkedAt;
    }
}

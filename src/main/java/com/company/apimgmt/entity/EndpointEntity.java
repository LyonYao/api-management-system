package com.company.apimgmt.entity;

import com.company.apimgmt.enums.HttpMethod;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Endpoint实体类
 * 对应endpoints表
 */
public class EndpointEntity {
    public UUID id;
    public UUID apiId;
    public String path;
    public HttpMethod httpMethod;
    public String description;
    public LocalDateTime createdAt;
    public LocalDateTime updatedAt;

    public EndpointEntity() {
    }

    public EndpointEntity(UUID id, UUID apiId, String path, HttpMethod httpMethod,
                          String description, LocalDateTime createdAt, LocalDateTime updatedAt) {
        this.id = id;
        this.apiId = apiId;
        this.path = path;
        this.httpMethod = httpMethod;
        this.description = description;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public UUID getApiId() {
        return apiId;
    }

    public void setApiId(UUID apiId) {
        this.apiId = apiId;
    }

    public String getPath() {
        return path;
    }

    public void setPath(String path) {
        this.path = path;
    }

    public HttpMethod getHttpMethod() {
        return httpMethod;
    }

    public void setHttpMethod(HttpMethod httpMethod) {
        this.httpMethod = httpMethod;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
}

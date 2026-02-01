package com.company.apimgmt.entity;

import com.company.apimgmt.enums.AuthType;
import com.company.apimgmt.enums.EntityType;
import io.vertx.core.json.JsonObject;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * 调用关系实体类
 * 对应relationships表
 */
public class RelationshipEntity {
    public UUID id;
    public EntityType callerType;
    public UUID callerId;
    public EntityType calleeType;
    public UUID calleeId;
    public UUID endpointId; // 具体调用的endpoint
    public AuthType authType;
    public JsonObject authConfig; // Vert.x JsonObject for JSONB
    public String description; // 调用关系的描述信息
    public LocalDateTime createdAt;
    public LocalDateTime updatedAt;

    public RelationshipEntity() {
    }

    public RelationshipEntity(UUID id, EntityType callerType, UUID callerId, EntityType calleeType,
                              UUID calleeId, UUID endpointId, AuthType authType, JsonObject authConfig,
                              String description, LocalDateTime createdAt, LocalDateTime updatedAt) {
        this.id = id;
        this.callerType = callerType;
        this.callerId = callerId;
        this.calleeType = calleeType;
        this.calleeId = calleeId;
        this.endpointId = endpointId;
        this.authType = authType;
        this.authConfig = authConfig;
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

    public EntityType getCallerType() {
        return callerType;
    }

    public void setCallerType(EntityType callerType) {
        this.callerType = callerType;
    }

    public UUID getCallerId() {
        return callerId;
    }

    public void setCallerId(UUID callerId) {
        this.callerId = callerId;
    }

    public EntityType getCalleeType() {
        return calleeType;
    }

    public void setCalleeType(EntityType calleeType) {
        this.calleeType = calleeType;
    }

    public UUID getCalleeId() {
        return calleeId;
    }

    public void setCalleeId(UUID calleeId) {
        this.calleeId = calleeId;
    }

    public UUID getEndpointId() {
        return endpointId;
    }

    public void setEndpointId(UUID endpointId) {
        this.endpointId = endpointId;
    }

    public AuthType getAuthType() {
        return authType;
    }

    public void setAuthType(AuthType authType) {
        this.authType = authType;
    }

    public JsonObject getAuthConfig() {
        return authConfig;
    }

    public void setAuthConfig(JsonObject authConfig) {
        this.authConfig = authConfig;
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

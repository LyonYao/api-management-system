package com.company.apimgmt.entity;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * 标签实体类
 * 对应tags表
 */
public class TagEntity {
    public UUID id;
    public String name;
    public LocalDateTime createdAt;

    public TagEntity() {
    }

    public TagEntity(UUID id, String name, LocalDateTime createdAt) {
        this.id = id;
        this.name = name;
        this.createdAt = createdAt;
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}

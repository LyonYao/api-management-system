package com.company.apimgmt.entity;

import com.company.apimgmt.enums.AuthType;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * API实体类
 * 对应apis表
 */
public class ApiEntity {
    public UUID id;
    public UUID systemId;
    public String name;
    public String description;
    public AuthType authType;
    public String specLink;
    public String department;
    public String contactName;
    public String contactEmails; // 逗号分隔的邮箱列表
    public LocalDateTime createdAt;
    public LocalDateTime updatedAt;
    public Set<String> tags; // Tag names

    public ApiEntity() {
    }

    public ApiEntity(UUID id, UUID systemId, String name, String description, AuthType authType,
                     String specLink, String department, String contactName, String contactEmails,
                     LocalDateTime createdAt, LocalDateTime updatedAt, Set<String> tags) {
        this.id = id;
        this.systemId = systemId;
        this.name = name;
        this.description = description;
        this.authType = authType;
        this.specLink = specLink;
        this.department = department;
        this.contactName = contactName;
        this.contactEmails = contactEmails;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.tags = tags;
    }

    // Helper methods for contactEmails
    public List<String> getContactEmailList() {
        if (contactEmails == null || contactEmails.isEmpty()) {
            return Collections.emptyList();
        }
        return Arrays.stream(contactEmails.split(","))
            .map(String::trim)
            .filter(s -> !s.isEmpty())
            .collect(Collectors.toList());
    }

    public void setContactEmailList(List<String> emails) {
        this.contactEmails = emails == null ? null : String.join(",", emails);
    }

    // Getters and Setters
    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public UUID getSystemId() {
        return systemId;
    }

    public void setSystemId(UUID systemId) {
        this.systemId = systemId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public AuthType getAuthType() {
        return authType;
    }

    public void setAuthType(AuthType authType) {
        this.authType = authType;
    }

    public String getSpecLink() {
        return specLink;
    }

    public void setSpecLink(String specLink) {
        this.specLink = specLink;
    }

    public String getDepartment() {
        return department;
    }

    public void setDepartment(String department) {
        this.department = department;
    }

    public String getContactName() {
        return contactName;
    }

    public void setContactName(String contactName) {
        this.contactName = contactName;
    }

    public String getContactEmails() {
        return contactEmails;
    }

    public void setContactEmails(String contactEmails) {
        this.contactEmails = contactEmails;
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

    public Set<String> getTags() {
        return tags;
    }

    public void setTags(Set<String> tags) {
        this.tags = tags;
    }
}

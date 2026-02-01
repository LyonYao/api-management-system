package com.company.apimgmt.repository;

import com.company.apimgmt.entity.ApiEntity;
import com.company.apimgmt.enums.AuthType;
import io.smallrye.mutiny.Uni;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import io.vertx.mutiny.pgclient.PgPool;
import io.vertx.mutiny.sqlclient.Row;
import io.vertx.mutiny.sqlclient.RowSet;
import io.vertx.mutiny.sqlclient.Tuple;

import java.util.*;
import java.util.stream.Collectors;

@ApplicationScoped
public class ApiRepository {
    
    @Inject
    PgPool client;
    
    public Uni<ApiEntity> create(ApiEntity api) {
        return client.preparedQuery(
            "INSERT INTO apis (id, system_id, name, description, auth_type, spec_link, " +
            "department, contact_name, contact_emails, created_at, updated_at) " +
            "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11) RETURNING *")
            .execute(Tuple.from(java.util.Arrays.asList(
                api.id,
                api.systemId,
                api.name,
                api.description,
                api.authType != null ? api.authType.name() : null,
                api.specLink,
                api.department,
                api.contactName,
                api.contactEmails,
                api.createdAt,
                api.updatedAt
            )))
            .onItem().transform(rows -> mapToApiEntity(rows.iterator().next()));
    }
    
    public Uni<ApiEntity> findById(UUID id) {
        return client.preparedQuery(
            "SELECT a.*, " +
            "COALESCE(array_agg(t.name) FILTER (WHERE t.name IS NOT NULL), '{}') as tag_names " +
            "FROM apis a " +
            "LEFT JOIN api_tags at ON a.id = at.api_id " +
            "LEFT JOIN tags t ON at.tag_id = t.id " +
            "WHERE a.id = $1 " +
            "GROUP BY a.id")
            .execute(Tuple.of(id))
            .onItem().transform(rows -> {
                var iterator = rows.iterator();
                return iterator.hasNext() ? mapToApiEntityWithTags(iterator.next()) : null;
            });
    }
    
    public Uni<List<ApiEntity>> findAll() {
        return client.query(
            "SELECT a.*, " +
            "COALESCE(array_agg(t.name) FILTER (WHERE t.name IS NOT NULL), '{}') as tag_names " +
            "FROM apis a " +
            "LEFT JOIN api_tags at ON a.id = at.api_id " +
            "LEFT JOIN tags t ON at.tag_id = t.id " +
            "GROUP BY a.id " +
            "ORDER BY a.name")
            .execute()
            .onItem().transform(this::mapToApiEntityListWithTags);
    }
    
    public Uni<List<ApiEntity>> findBySystemId(UUID systemId) {
        return client.preparedQuery(
            "SELECT a.*, " +
            "COALESCE(array_agg(t.name) FILTER (WHERE t.name IS NOT NULL), '{}') as tag_names " +
            "FROM apis a " +
            "LEFT JOIN api_tags at ON a.id = at.api_id " +
            "LEFT JOIN tags t ON at.tag_id = t.id " +
            "WHERE a.system_id = $1 " +
            "GROUP BY a.id " +
            "ORDER BY a.name")
            .execute(Tuple.of(systemId))
            .onItem().transform(this::mapToApiEntityListWithTags);
    }
    
    public Uni<List<ApiEntity>> findByTags(Set<String> tags) {
        if (tags == null || tags.isEmpty()) {
            return findAll();
        }
        
        String placeholders = tags.stream()
            .map(t -> "?")
            .collect(Collectors.joining(","));
        
        return client.preparedQuery(
            "SELECT a.*, " +
            "COALESCE(array_agg(t.name) FILTER (WHERE t.name IS NOT NULL), '{}') as tag_names " +
            "FROM apis a " +
            "INNER JOIN api_tags at ON a.id = at.api_id " +
            "INNER JOIN tags t ON at.tag_id = t.id " +
            "WHERE t.name = ANY($1) " +
            "GROUP BY a.id " +
            "HAVING COUNT(DISTINCT t.name) = $2 " +
            "ORDER BY a.name")
            .execute(Tuple.of(tags.toArray(new String[0]), tags.size()))
            .onItem().transform(this::mapToApiEntityListWithTags);
    }
    
    public Uni<ApiEntity> update(ApiEntity api) {
        return client.preparedQuery(
            "UPDATE apis SET name = $1, description = $2, auth_type = $3, spec_link = $4, " +
            "department = $5, contact_name = $6, contact_emails = $7, updated_at = $8 " +
            "WHERE id = $9 RETURNING *")
            .execute(Tuple.from(java.util.Arrays.asList(
                api.name,
                api.description,
                api.authType != null ? api.authType.name() : null,
                api.specLink,
                api.department,
                api.contactName,
                api.contactEmails,
                api.updatedAt,
                api.id
            )))
            .onItem().transform(rows -> {
                var iterator = rows.iterator();
                return iterator.hasNext() ? mapToApiEntity(iterator.next()) : null;
            });
    }
    
    public Uni<Boolean> delete(UUID id) {
        return client.preparedQuery("DELETE FROM apis WHERE id = $1")
            .execute(Tuple.of(id))
            .onItem().transform(rows -> rows.rowCount() > 0);
    }
    
    public Uni<Void> associateTags(UUID apiId, Set<UUID> tagIds) {
        if (tagIds == null || tagIds.isEmpty()) {
            return Uni.createFrom().voidItem();
        }
        
        // Build batch insert
        List<Tuple> batch = new ArrayList<>();
        for (UUID tagId : tagIds) {
            batch.add(Tuple.of(apiId, tagId));
        }
        
        return client.preparedQuery(
            "INSERT INTO api_tags (api_id, tag_id) VALUES ($1, $2) ON CONFLICT DO NOTHING")
            .executeBatch(batch)
            .onItem().transform(rows -> null);
    }
    
    public Uni<Void> clearTags(UUID apiId) {
        return client.preparedQuery("DELETE FROM api_tags WHERE api_id = $1")
            .execute(Tuple.of(apiId))
            .onItem().transform(rows -> null);
    }
    
    private ApiEntity mapToApiEntity(Row row) {
        ApiEntity entity = new ApiEntity();
        entity.id = row.getUUID("id");
        entity.systemId = row.getUUID("system_id");
        entity.name = row.getString("name");
        entity.description = row.getString("description");
        
        String authTypeStr = row.getString("auth_type");
        entity.authType = authTypeStr != null ? AuthType.valueOf(authTypeStr) : null;
        
        entity.specLink = row.getString("spec_link");
        entity.department = row.getString("department");
        entity.contactName = row.getString("contact_name");
        entity.contactEmails = row.getString("contact_emails");
        entity.createdAt = row.getLocalDateTime("created_at");
        entity.updatedAt = row.getLocalDateTime("updated_at");
        entity.tags = new HashSet<>();
        
        return entity;
    }
    
    private ApiEntity mapToApiEntityWithTags(Row row) {
        ApiEntity entity = mapToApiEntity(row);
        
        // Extract tags from array
        Object tagNamesObj = row.getValue("tag_names");
        if (tagNamesObj instanceof String[]) {
            String[] tagNames = (String[]) tagNamesObj;
            entity.tags = Arrays.stream(tagNames)
                .filter(name -> name != null && !name.isEmpty())
                .collect(Collectors.toSet());
        }
        
        return entity;
    }
    
    private List<ApiEntity> mapToApiEntityListWithTags(RowSet<Row> rows) {
        List<ApiEntity> list = new ArrayList<>();
        for (Row row : rows) {
            list.add(mapToApiEntityWithTags(row));
        }
        return list;
    }
}

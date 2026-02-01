package com.company.apimgmt.repository;

import com.company.apimgmt.entity.RelationshipEntity;
import com.company.apimgmt.enums.AuthType;
import com.company.apimgmt.enums.EntityType;
import io.smallrye.mutiny.Uni;
import io.vertx.core.json.JsonObject;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import io.vertx.mutiny.pgclient.PgPool;
import io.vertx.mutiny.sqlclient.Row;
import io.vertx.mutiny.sqlclient.RowSet;
import io.vertx.mutiny.sqlclient.Tuple;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@ApplicationScoped
public class RelationshipRepository {
    
    @Inject
    PgPool client;
    
    public Uni<RelationshipEntity> create(RelationshipEntity relationship) {
        return client.preparedQuery(
            "INSERT INTO relationships (id, caller_type, caller_id, callee_type, callee_id, " +
            "endpoint_id, auth_type, auth_config, description, created_at, updated_at) " +
            "VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9, $10, $11) RETURNING *")
            .execute(Tuple.from(java.util.Arrays.asList(
                relationship.id,
                relationship.callerType.name(),
                relationship.callerId,
                relationship.calleeType.name(),
                relationship.calleeId,
                relationship.endpointId,
                relationship.authType != null ? relationship.authType.name() : null,
                relationship.authConfig != null ? relationship.authConfig.encode() : null,
                relationship.description,
                relationship.createdAt,
                relationship.updatedAt
            )))
            .onItem().transform(rows -> mapToRelationshipEntity(rows.iterator().next()));
    }
    
    public Uni<RelationshipEntity> findById(UUID id) {
        return client.preparedQuery("SELECT * FROM relationships WHERE id = $1")
            .execute(Tuple.of(id))
            .onItem().transform(rows -> {
                var iterator = rows.iterator();
                return iterator.hasNext() ? mapToRelationshipEntity(iterator.next()) : null;
            });
    }
    
    public Uni<List<RelationshipEntity>> findAll() {
        return client.query("SELECT * FROM relationships ORDER BY created_at DESC")
            .execute()
            .onItem().transform(this::mapToRelationshipEntityList);
    }
    
    public Uni<List<RelationshipEntity>> findByCaller(EntityType type, UUID id) {
        return client.preparedQuery(
            "SELECT * FROM relationships WHERE caller_type = $1 AND caller_id = $2 ORDER BY created_at DESC")
            .execute(Tuple.of(type.name(), id))
            .onItem().transform(this::mapToRelationshipEntityList);
    }
    
    public Uni<List<RelationshipEntity>> findByCallee(EntityType type, UUID id) {
        return client.preparedQuery(
            "SELECT * FROM relationships WHERE callee_type = $1 AND callee_id = $2 ORDER BY created_at DESC")
            .execute(Tuple.of(type.name(), id))
            .onItem().transform(this::mapToRelationshipEntityList);
    }
    
    public Uni<RelationshipEntity> update(RelationshipEntity relationship) {
        return client.preparedQuery(
            "UPDATE relationships SET caller_type = $1, caller_id = $2, callee_type = $3, " +
            "callee_id = $4, endpoint_id = $5, auth_type = $6, auth_config = $7::jsonb, " +
            "description = $8, updated_at = $9 WHERE id = $10 RETURNING *")
            .execute(Tuple.from(java.util.Arrays.asList(
                relationship.callerType.name(),
                relationship.callerId,
                relationship.calleeType.name(),
                relationship.calleeId,
                relationship.endpointId,
                relationship.authType != null ? relationship.authType.name() : null,
                relationship.authConfig != null ? relationship.authConfig.encode() : null,
                relationship.description,
                relationship.updatedAt,
                relationship.id
            )))
            .onItem().transform(rows -> {
                var iterator = rows.iterator();
                return iterator.hasNext() ? mapToRelationshipEntity(iterator.next()) : null;
            });
    }
    
    public Uni<Boolean> delete(UUID id) {
        return client.preparedQuery("DELETE FROM relationships WHERE id = $1")
            .execute(Tuple.of(id))
            .onItem().transform(rows -> rows.rowCount() > 0);
    }
    
    private RelationshipEntity mapToRelationshipEntity(Row row) {
        RelationshipEntity entity = new RelationshipEntity();
        entity.id = row.getUUID("id");
        entity.callerType = EntityType.valueOf(row.getString("caller_type"));
        entity.callerId = row.getUUID("caller_id");
        entity.calleeType = EntityType.valueOf(row.getString("callee_type"));
        entity.calleeId = row.getUUID("callee_id");
        entity.endpointId = row.getUUID("endpoint_id");
        
        String authTypeStr = row.getString("auth_type");
        entity.authType = authTypeStr != null ? AuthType.valueOf(authTypeStr) : null;
        
        Object authConfigObj = row.getValue("auth_config");
        if (authConfigObj != null) {
            entity.authConfig = new JsonObject(authConfigObj.toString());
        }
        
        entity.description = row.getString("description");
        entity.createdAt = row.getLocalDateTime("created_at");
        entity.updatedAt = row.getLocalDateTime("updated_at");
        
        return entity;
    }
    
    private List<RelationshipEntity> mapToRelationshipEntityList(RowSet<Row> rows) {
        List<RelationshipEntity> list = new ArrayList<>();
        for (Row row : rows) {
            list.add(mapToRelationshipEntity(row));
        }
        return list;
    }
}

package com.company.apimgmt.repository;

import com.company.apimgmt.entity.SystemEntity;
import io.smallrye.mutiny.Uni;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import io.vertx.mutiny.pgclient.PgPool;
import io.vertx.mutiny.sqlclient.Row;
import io.vertx.mutiny.sqlclient.RowSet;
import io.vertx.mutiny.sqlclient.Tuple;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@ApplicationScoped
public class SystemRepository {
    
    @Inject
    PgPool client;
    
    public Uni<SystemEntity> create(SystemEntity system) {
        return client.preparedQuery(
            "INSERT INTO systems (id, name, description, created_at, updated_at) " +
            "VALUES ($1, $2, $3, $4, $5) RETURNING *")
            .execute(Tuple.of(
                system.id,
                system.name,
                system.description,
                system.createdAt,
                system.updatedAt
            ))
            .onItem().transform(rows -> mapToSystemEntity(rows.iterator().next()));
    }
    
    public Uni<SystemEntity> findById(UUID id) {
        return client.preparedQuery("SELECT * FROM systems WHERE id = $1")
            .execute(Tuple.of(id))
            .onItem().transform(rows -> {
                var iterator = rows.iterator();
                return iterator.hasNext() ? mapToSystemEntity(iterator.next()) : null;
            });
    }
    
    public Uni<SystemEntity> findByName(String name) {
        return client.preparedQuery("SELECT * FROM systems WHERE name = $1")
            .execute(Tuple.of(name))
            .onItem().transform(rows -> {
                var iterator = rows.iterator();
                return iterator.hasNext() ? mapToSystemEntity(iterator.next()) : null;
            });
    }
    
    public Uni<List<SystemEntity>> findAll() {
        return client.query("SELECT * FROM systems ORDER BY name")
            .execute()
            .onItem().transform(this::mapToSystemEntityList);
    }
    
    public Uni<SystemEntity> update(SystemEntity system) {
        return client.preparedQuery(
            "UPDATE systems SET name = $1, description = $2, updated_at = $3 " +
            "WHERE id = $4 RETURNING *")
            .execute(Tuple.of(
                system.name,
                system.description,
                system.updatedAt,
                system.id
            ))
            .onItem().transform(rows -> {
                var iterator = rows.iterator();
                return iterator.hasNext() ? mapToSystemEntity(iterator.next()) : null;
            });
    }
    
    public Uni<Boolean> delete(UUID id) {
        return client.preparedQuery("DELETE FROM systems WHERE id = $1")
            .execute(Tuple.of(id))
            .onItem().transform(rows -> rows.rowCount() > 0);
    }
    
    public Uni<Long> countApisBySystemId(UUID systemId) {
        return client.preparedQuery("SELECT COUNT(*) FROM apis WHERE system_id = $1")
            .execute(Tuple.of(systemId))
            .onItem().transform(rows -> {
                var iterator = rows.iterator();
                return iterator.hasNext() ? iterator.next().getLong(0) : 0L;
            });
    }
    
    private SystemEntity mapToSystemEntity(Row row) {
        SystemEntity entity = new SystemEntity();
        entity.id = row.getUUID("id");
        entity.name = row.getString("name");
        entity.description = row.getString("description");
        entity.createdAt = row.getLocalDateTime("created_at");
        entity.updatedAt = row.getLocalDateTime("updated_at");
        return entity;
    }
    
    private List<SystemEntity> mapToSystemEntityList(RowSet<Row> rows) {
        List<SystemEntity> list = new ArrayList<>();
        for (Row row : rows) {
            list.add(mapToSystemEntity(row));
        }
        return list;
    }
}

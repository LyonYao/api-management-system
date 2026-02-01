package com.company.apimgmt.repository;

import com.company.apimgmt.entity.EndpointEntity;
import com.company.apimgmt.enums.HttpMethod;
import io.smallrye.mutiny.Uni;
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
public class EndpointRepository {
    
    @Inject
    PgPool client;
    
    public Uni<EndpointEntity> create(EndpointEntity endpoint) {
        return client.preparedQuery(
            "INSERT INTO endpoints (id, api_id, path, http_method, description, created_at, updated_at) " +
            "VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *")
            .execute(Tuple.from(java.util.Arrays.asList(
                endpoint.id,
                endpoint.apiId,
                endpoint.path,
                endpoint.httpMethod.name(),
                endpoint.description,
                endpoint.createdAt,
                endpoint.updatedAt
            )))
            .onItem().transform(rows -> mapToEndpointEntity(rows.iterator().next()));
    }
    
    public Uni<EndpointEntity> findById(UUID id) {
        return client.preparedQuery("SELECT * FROM endpoints WHERE id = $1")
            .execute(Tuple.of(id))
            .onItem().transform(rows -> {
                var iterator = rows.iterator();
                return iterator.hasNext() ? mapToEndpointEntity(iterator.next()) : null;
            });
    }
    
    public Uni<List<EndpointEntity>> findByApiId(UUID apiId) {
        return client.preparedQuery("SELECT * FROM endpoints WHERE api_id = $1 ORDER BY path, http_method")
            .execute(Tuple.of(apiId))
            .onItem().transform(this::mapToEndpointEntityList);
    }
    
    public Uni<List<EndpointEntity>> findAll() {
        return client.query("SELECT * FROM endpoints ORDER BY path, http_method")
            .execute()
            .onItem().transform(this::mapToEndpointEntityList);
    }
    
    public Uni<EndpointEntity> findByApiIdPathAndMethod(UUID apiId, String path, HttpMethod httpMethod) {
        return client.preparedQuery(
            "SELECT * FROM endpoints WHERE api_id = $1 AND path = $2 AND http_method = $3")
            .execute(Tuple.of(apiId, path, httpMethod.name()))
            .onItem().transform(rows -> {
                var iterator = rows.iterator();
                return iterator.hasNext() ? mapToEndpointEntity(iterator.next()) : null;
            });
    }
    
    public Uni<EndpointEntity> update(EndpointEntity endpoint) {
        return client.preparedQuery(
            "UPDATE endpoints SET path = $1, http_method = $2, description = $3, updated_at = $4 " +
            "WHERE id = $5 RETURNING *")
            .execute(Tuple.of(
                endpoint.path,
                endpoint.httpMethod.name(),
                endpoint.description,
                endpoint.updatedAt,
                endpoint.id
            ))
            .onItem().transform(rows -> {
                var iterator = rows.iterator();
                return iterator.hasNext() ? mapToEndpointEntity(iterator.next()) : null;
            });
    }
    
    public Uni<Boolean> delete(UUID id) {
        return client.preparedQuery("DELETE FROM endpoints WHERE id = $1")
            .execute(Tuple.of(id))
            .onItem().transform(rows -> rows.rowCount() > 0);
    }
    
    private EndpointEntity mapToEndpointEntity(Row row) {
        EndpointEntity entity = new EndpointEntity();
        entity.id = row.getUUID("id");
        entity.apiId = row.getUUID("api_id");
        entity.path = row.getString("path");
        entity.httpMethod = HttpMethod.valueOf(row.getString("http_method"));
        entity.description = row.getString("description");
        entity.createdAt = row.getLocalDateTime("created_at");
        entity.updatedAt = row.getLocalDateTime("updated_at");
        return entity;
    }
    
    private List<EndpointEntity> mapToEndpointEntityList(RowSet<Row> rows) {
        List<EndpointEntity> list = new ArrayList<>();
        for (Row row : rows) {
            list.add(mapToEndpointEntity(row));
        }
        return list;
    }
}

package com.company.apimgmt.repository;

import com.company.apimgmt.entity.HealthCheckResultEntity;
import com.company.apimgmt.enums.HealthCheckStatus;
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
public class HealthCheckResultRepository {
    
    @Inject
    PgPool client;
    
    public Uni<HealthCheckResultEntity> create(HealthCheckResultEntity result) {
        return client.preparedQuery(
            "INSERT INTO health_check_results (id, endpoint_id, status, response_code, " +
            "response_time_ms, error_message, checked_at) " +
            "VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *")
            .execute(Tuple.from(java.util.Arrays.asList(
                result.id,
                result.endpointId,
                result.status.name(),
                result.responseCode,
                result.responseTimeMs,
                result.errorMessage,
                result.checkedAt
            )))
            .onItem().transform(rows -> mapToHealthCheckResultEntity(rows.iterator().next()));
    }
    
    public Uni<List<HealthCheckResultEntity>> findByEndpointId(UUID endpointId) {
        return client.preparedQuery(
            "SELECT * FROM health_check_results WHERE endpoint_id = $1 ORDER BY checked_at DESC")
            .execute(Tuple.of(endpointId))
            .onItem().transform(this::mapToHealthCheckResultEntityList);
    }
    
    public Uni<List<HealthCheckResultEntity>> findRecent(int limit) {
        return client.preparedQuery(
            "SELECT * FROM health_check_results ORDER BY checked_at DESC LIMIT $1")
            .execute(Tuple.of(limit))
            .onItem().transform(this::mapToHealthCheckResultEntityList);
    }
    
    private HealthCheckResultEntity mapToHealthCheckResultEntity(Row row) {
        HealthCheckResultEntity entity = new HealthCheckResultEntity();
        entity.id = row.getUUID("id");
        entity.endpointId = row.getUUID("endpoint_id");
        entity.status = HealthCheckStatus.valueOf(row.getString("status"));
        entity.responseCode = row.getInteger("response_code");
        entity.responseTimeMs = row.getInteger("response_time_ms");
        entity.errorMessage = row.getString("error_message");
        entity.checkedAt = row.getLocalDateTime("checked_at");
        return entity;
    }
    
    private List<HealthCheckResultEntity> mapToHealthCheckResultEntityList(RowSet<Row> rows) {
        List<HealthCheckResultEntity> list = new ArrayList<>();
        for (Row row : rows) {
            list.add(mapToHealthCheckResultEntity(row));
        }
        return list;
    }
}

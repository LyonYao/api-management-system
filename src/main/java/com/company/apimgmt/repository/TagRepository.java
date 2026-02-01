package com.company.apimgmt.repository;

import com.company.apimgmt.entity.TagEntity;
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
public class TagRepository {
    
    @Inject
    PgPool client;
    
    public Uni<TagEntity> create(String name) {
        UUID id = UUID.randomUUID();
        LocalDateTime now = LocalDateTime.now();
        
        return client.preparedQuery(
            "INSERT INTO tags (id, name, created_at) VALUES ($1, $2, $3) RETURNING *")
            .execute(Tuple.of(id, name, now))
            .onItem().transform(rows -> mapToTagEntity(rows.iterator().next()));
    }
    
    public Uni<TagEntity> findByName(String name) {
        return client.preparedQuery("SELECT * FROM tags WHERE name = $1")
            .execute(Tuple.of(name))
            .onItem().transform(rows -> {
                var iterator = rows.iterator();
                return iterator.hasNext() ? mapToTagEntity(iterator.next()) : null;
            });
    }
    
    public Uni<List<TagEntity>> findAll() {
        return client.query("SELECT * FROM tags ORDER BY name")
            .execute()
            .onItem().transform(this::mapToTagEntityList);
    }
    
    public Uni<Boolean> delete(UUID id) {
        return client.preparedQuery("DELETE FROM tags WHERE id = $1")
            .execute(Tuple.of(id))
            .onItem().transform(rows -> rows.rowCount() > 0);
    }
    
    public Uni<TagEntity> findOrCreate(String name) {
        return findByName(name)
            .onItem().transformToUni(existing -> {
                if (existing != null) {
                    return Uni.createFrom().item(existing);
                }
                return create(name);
            });
    }
    
    private TagEntity mapToTagEntity(Row row) {
        TagEntity entity = new TagEntity();
        entity.id = row.getUUID("id");
        entity.name = row.getString("name");
        entity.createdAt = row.getLocalDateTime("created_at");
        return entity;
    }
    
    private List<TagEntity> mapToTagEntityList(RowSet<Row> rows) {
        List<TagEntity> list = new ArrayList<>();
        for (Row row : rows) {
            list.add(mapToTagEntity(row));
        }
        return list;
    }
}

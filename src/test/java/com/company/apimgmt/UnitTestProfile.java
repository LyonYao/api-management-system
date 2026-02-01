package com.company.apimgmt;

import io.quarkus.test.junit.QuarkusTestProfile;
import io.vertx.mutiny.pgclient.PgPool;
import io.vertx.mutiny.sqlclient.Pool;

import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * 专门用于单元测试的配置文件，完全禁用所有外部依赖
 */
public class UnitTestProfile implements QuarkusTestProfile {

    @Override
    public List<TestResourceEntry> testResources() {
        return Collections.emptyList();
    }

    @Override
    public Map<String, String> getConfigOverrides() {
        return Map.of(
                // 完全禁用数据源
                "quarkus.datasource.devservices.enabled", "false",
                "quarkus.datasource.active", "false",
                "quarkus.flyway.migrate-at-start", "false",
                // 禁用HTTP服务器
                "quarkus.http.test-port", "0",
                "quarkus.http.host", "localhost",
                // 禁用Lambda相关配置
                "quarkus.lambda.enable-polling-jvm-mode", "false"
        );
    }

    @Override
    public Set<Class<?>> getEnabledAlternatives() {
        return Set.of(MockDatabaseProducer.class);
    }

    /**
     * 提供所有数据库相关的Mock对象
     */
    @jakarta.enterprise.inject.Alternative
    @jakarta.enterprise.context.ApplicationScoped
    public static class MockDatabaseProducer {
        
        @jakarta.enterprise.inject.Produces
        @jakarta.enterprise.context.ApplicationScoped
        public PgPool pgPool() {
            return org.mockito.Mockito.mock(PgPool.class);
        }

        @jakarta.enterprise.inject.Produces
        @jakarta.enterprise.context.ApplicationScoped
        public Pool pool() {
            return org.mockito.Mockito.mock(Pool.class);
        }
    }
}
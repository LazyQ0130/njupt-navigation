package cn.edu.njupt.map.integration;

import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.is;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.httpBasic;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.multipart;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.nio.charset.StandardCharsets;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.DockerImageName;

@SpringBootTest
@AutoConfigureMockMvc
@Testcontainers(disabledWithoutDocker = true)
class PhaseZeroIntegrationTest {

    private static final DockerImageName POSTGIS_IMAGE = DockerImageName
            .parse("postgis/postgis:16-3.4-alpine")
            .asCompatibleSubstituteFor("postgres");

    @Container
    static final PostgreSQLContainer<?> POSTGRES = new PostgreSQLContainer<>(POSTGIS_IMAGE)
            .withDatabaseName("njupt_map_test")
            .withUsername("njupt")
            .withPassword("test-only-password");

    @Autowired
    private MockMvc mockMvc;

    @DynamicPropertySource
    static void databaseProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", POSTGRES::getJdbcUrl);
        registry.add("spring.datasource.username", POSTGRES::getUsername);
        registry.add("spring.datasource.password", POSTGRES::getPassword);
        registry.add("app.security.bootstrap-user", () -> "test-admin");
        registry.add("app.security.bootstrap-password", () -> "test-password");
    }

    @Test
    void flywayBootstrapAndGeoJsonImportWorkTogether() throws Exception {
        mockMvc.perform(get("/map/bootstrap"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.campuses", hasSize(1)))
                .andExpect(jsonPath("$.campuses[0].code", is("NJUPT_XIANLIN")))
                .andExpect(jsonPath("$.campuses[0].data.buildings", is(0)));

        String geoJson = """
                {
                  "type": "FeatureCollection",
                  "features": [{
                    "type": "Feature",
                    "properties": {
                      "featureType": "POI",
                      "externalId": "integration-poi-1",
                      "name": "集成测试服务点",
                      "aliases": ["测试点"],
                      "keywords": ["测试"],
                      "category": "SERVICE"
                    },
                    "geometry": {"type": "Point", "coordinates": [118.91, 32.10]}
                  }]
                }
                """;
        MockMultipartFile file = new MockMultipartFile(
                "file", "test.geojson", "application/geo+json", geoJson.getBytes(StandardCharsets.UTF_8)
        );

        mockMvc.perform(multipart("/admin/imports/geojson")
                        .file(file)
                        .with(httpBasic("test-admin", "test-password")))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.succeeded", is(1)))
                .andExpect(jsonPath("$.created", is(1)));

        mockMvc.perform(get("/map/bootstrap"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.campuses[0].data.pois", is(1)));

        mockMvc.perform(get("/map/features"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.type", is("FeatureCollection")))
                .andExpect(jsonPath("$.features", hasSize(1)))
                .andExpect(jsonPath("$.features[0].id", is("integration-poi-1")))
                .andExpect(jsonPath("$.features[0].geometry.coordinates[0]", is(118.91)))
                .andExpect(jsonPath("$.features[0].geometry.coordinates[1]", is(32.10)));
    }

    @Test
    void importRequiresAuthentication() throws Exception {
        MockMultipartFile file = new MockMultipartFile(
                "file", "empty.geojson", "application/geo+json", "{}".getBytes(StandardCharsets.UTF_8)
        );

        mockMvc.perform(multipart("/admin/imports/geojson").file(file))
                .andExpect(status().isUnauthorized());
    }
}

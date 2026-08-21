package cn.edu.njupt.map.importer;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import cn.edu.njupt.map.domain.Campus;
import cn.edu.njupt.map.repository.BuildingRepository;
import cn.edu.njupt.map.repository.CampusRepository;
import cn.edu.njupt.map.repository.PoiRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class GeoJsonImportServiceTest {

    private CampusRepository campusRepository;
    private BuildingRepository buildingRepository;
    private PoiRepository poiRepository;
    private GeoJsonImportService service;

    @BeforeEach
    void setUp() {
        campusRepository = mock(CampusRepository.class);
        buildingRepository = mock(BuildingRepository.class);
        poiRepository = mock(PoiRepository.class);
        service = new GeoJsonImportService(
                new ObjectMapper(), campusRepository, buildingRepository, poiRepository, 10
        );
        when(campusRepository.findByCodeAndEnabledTrue("NJUPT_XIANLIN"))
                .thenReturn(Optional.of(mock(Campus.class)));
    }

    @Test
    void importsValidPointAndReportsInvalidFeatureWithoutAbortingBatch() throws Exception {
        String geoJson = """
                {
                  "type": "FeatureCollection",
                  "features": [
                    {
                      "type": "Feature",
                      "properties": {
                        "featureType": "POI",
                        "externalId": "test-poi-1",
                        "name": "测试服务点",
                        "category": "SERVICE"
                      },
                      "geometry": {"type": "Point", "coordinates": [118.91, 32.10]}
                    },
                    {
                      "type": "Feature",
                      "properties": {
                        "featureType": "POI",
                        "externalId": "bad-poi",
                        "name": "坐标错误",
                        "category": "SERVICE"
                      },
                      "geometry": {"type": "Point", "coordinates": [218.91, 32.10]}
                    }
                  ]
                }
                """;

        GeoJsonImportResult result = service.importFeatureCollection(stream(geoJson));

        assertThat(result.total()).isEqualTo(2);
        assertThat(result.succeeded()).isEqualTo(1);
        assertThat(result.failed()).isEqualTo(1);
        assertThat(result.created()).isEqualTo(1);
        assertThat(result.errors().getFirst().externalId()).isEqualTo("bad-poi");
        verify(poiRepository).save(any());
    }

    @Test
    void rejectsNonFeatureCollection() {
        String geoJson = "{\"type\":\"Feature\",\"geometry\":null}";

        assertThatThrownBy(() -> service.importFeatureCollection(stream(geoJson)))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("FeatureCollection");
    }

    @Test
    void enforcesConfiguredFeatureLimit() {
        StringBuilder features = new StringBuilder();
        for (int index = 0; index < 11; index++) {
            if (index > 0) {
                features.append(',');
            }
            features.append("{\"type\":\"Feature\"}");
        }
        String geoJson = "{\"type\":\"FeatureCollection\",\"features\":[" + features + "]}";

        assertThatThrownBy(() -> service.importFeatureCollection(stream(geoJson)))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("最多允许 10");
    }

    private ByteArrayInputStream stream(String text) {
        return new ByteArrayInputStream(text.getBytes(StandardCharsets.UTF_8));
    }
}


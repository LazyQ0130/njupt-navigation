package cn.edu.njupt.map.importer;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import org.mockito.ArgumentCaptor;

import cn.edu.njupt.map.domain.Campus;
import cn.edu.njupt.map.domain.MapFeature;
import cn.edu.njupt.map.domain.Building;
import cn.edu.njupt.map.domain.Poi;
import cn.edu.njupt.map.repository.BuildingRepository;
import cn.edu.njupt.map.repository.BuildingEntranceRepository;
import cn.edu.njupt.map.repository.CampusRepository;
import cn.edu.njupt.map.repository.PoiRepository;
import cn.edu.njupt.map.repository.MapFeatureRepository;
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
    private MapFeatureRepository mapFeatureRepository;
    private BuildingEntranceRepository buildingEntranceRepository;
    private GeoJsonImportService service;

    @BeforeEach
    void setUp() {
        campusRepository = mock(CampusRepository.class);
        buildingRepository = mock(BuildingRepository.class);
        poiRepository = mock(PoiRepository.class);
        mapFeatureRepository = mock(MapFeatureRepository.class);
        buildingEntranceRepository = mock(BuildingEntranceRepository.class);
        service = new GeoJsonImportService(
                new ObjectMapper(), campusRepository, buildingRepository, poiRepository,
                mapFeatureRepository, buildingEntranceRepository, 10
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
    void rejectsSelfIntersectingGeometry() throws Exception {
        String geoJson = """
                {"type":"FeatureCollection","features":[{
                "type":"Feature","properties":{"featureType":"GREEN",
                "externalId":"invalid-bow-tie","name":"无效多边形"},
                "geometry":{"type":"Polygon","coordinates":[[[118.92,32.11],
                [118.93,32.12],[118.93,32.11],[118.92,32.12],[118.92,32.11]]]}}]}
                """;

        GeoJsonImportResult result = service.importFeatureCollection(stream(geoJson));

        assertThat(result.failed()).isEqualTo(1);
        assertThat(result.errors().getFirst().reason()).contains("Geometry 不合法");
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

    @Test
    void importsSourceMetadataAndUsesExternalIdForIdempotentUpdate() throws Exception {
        MapFeature existing = new MapFeature();
        when(mapFeatureRepository.findByExternalId("osm:way:89910254"))
                .thenReturn(Optional.of(existing));
        String geoJson = """
                {"type":"FeatureCollection","metadata":{"dataSource":"OPENSTREETMAP",
                "verificationStatus":"SOURCE_VERIFIED","sourceId":"osm-test"},"features":[{
                "type":"Feature","properties":{"featureType":"CAMPUS_BOUNDARY",
                "externalId":"osm:way:89910254","name":"测试校界"},
                "geometry":{"type":"Polygon","coordinates":[[[118.92,32.11],[118.93,32.11],
                [118.93,32.12],[118.92,32.11]]]}}]}
                """;

        GeoJsonImportResult result = service.importFeatureCollection(stream(geoJson));

        assertThat(result.updated()).isEqualTo(1);
        ArgumentCaptor<MapFeature> captor = ArgumentCaptor.forClass(MapFeature.class);
        verify(mapFeatureRepository).save(captor.capture());
        assertThat(captor.getValue().getDataSource()).isEqualTo("OPENSTREETMAP");
        assertThat(captor.getValue().getVerificationStatus()).isEqualTo("SOURCE_VERIFIED");
        assertThat(captor.getValue().getSourceId()).isEqualTo("osm-test");
    }

    @Test
    void importsNamingSemanticsAndLinksPoiToBuilding() throws Exception {
        Building building = new Building();
        when(buildingRepository.findByExternalId("osm:way:library"))
                .thenReturn(Optional.of(building));
        String geoJson = """
                {"type":"FeatureCollection","features":[{
                "type":"Feature","properties":{"featureType":"POI","externalId":"library-poi",
                "name":"仙林校区图书馆","officialName":"仙林校区图书馆","displayName":"图书馆",
                "labelVisible":true,"aliases":["仙林图书馆"],"keywords":[],"category":"LIBRARY",
                "buildingExternalId":"osm:way:library"},
                "geometry":{"type":"Point","coordinates":[118.92,32.11]}}]}
                """;

        service.importFeatureCollection(stream(geoJson));

        ArgumentCaptor<Poi> captor = ArgumentCaptor.forClass(Poi.class);
        verify(poiRepository).save(captor.capture());
        assertThat(captor.getValue().getDisplayName()).isEqualTo("图书馆");
        assertThat(captor.getValue().getOfficialName()).isEqualTo("仙林校区图书馆");
        assertThat(captor.getValue().getAliases()).containsExactly("仙林图书馆");
        assertThat(captor.getValue().getBuilding()).isSameAs(building);
    }

    @Test
    void importsDormitoryZonePointAndRejectsAnInferredPolygon() throws Exception {
        String geoJson = """
                {"type":"FeatureCollection","features":[
                {"type":"Feature","properties":{"featureType":"DORMITORY_ZONE",
                "externalId":"zone-liu","name":"柳苑","priority":80},
                "geometry":{"type":"Point","coordinates":[118.9291,32.1203]}},
                {"type":"Feature","properties":{"featureType":"DORMITORY_ZONE",
                "externalId":"zone-fake-polygon","name":"伪边界"},
                "geometry":{"type":"Polygon","coordinates":[[[118.92,32.11],[118.93,32.11],
                [118.93,32.12],[118.92,32.11]]]}}]}
                """;

        GeoJsonImportResult result = service.importFeatureCollection(stream(geoJson));

        assertThat(result.succeeded()).isEqualTo(1);
        assertThat(result.failed()).isEqualTo(1);
        assertThat(result.errors().getFirst().reason()).contains("必须是 Point");
        verify(mapFeatureRepository).save(any(MapFeature.class));
    }

    @Test
    void authoritativeRefreshDisablesExistingRowsBeforeUpsert() {
        service.prepareDatasetRefresh("real");

        verify(buildingRepository).setEnabledByDataSource("OPENSTREETMAP", false);
        verify(poiRepository).setEnabledByDataSource("OPENSTREETMAP", false);
        verify(mapFeatureRepository).setEnabledByDataSource("OPENSTREETMAP", false);
        verify(buildingEntranceRepository).setEnabledByDataSource("OPENSTREETMAP", false);
        verify(buildingRepository).setEnabledByDataSource("MANUAL", false);
        verify(poiRepository).setEnabledByDataSource("SYNTHETIC", false);
    }

    @Test
    void authoritativeRefreshRejectsUnknownMode() {
        assertThatThrownBy(() -> service.prepareDatasetRefresh("unknown"))
                .isInstanceOf(IllegalArgumentException.class);
    }

    private ByteArrayInputStream stream(String text) {
        return new ByteArrayInputStream(text.getBytes(StandardCharsets.UTF_8));
    }
}

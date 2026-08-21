package cn.edu.njupt.map.map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import cn.edu.njupt.map.domain.Building;
import cn.edu.njupt.map.domain.Campus;
import cn.edu.njupt.map.repository.BuildingRepository;
import cn.edu.njupt.map.repository.CampusRepository;
import cn.edu.njupt.map.repository.MapFeatureRepository;
import cn.edu.njupt.map.repository.PoiRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.locationtech.jts.geom.Coordinate;
import org.locationtech.jts.geom.GeometryFactory;
import org.locationtech.jts.geom.Polygon;

class MapFeatureServiceTest {

    private static final String CAMPUS_CODE = "NJUPT_XIANLIN";

    private final CampusRepository campusRepository = mock(CampusRepository.class);
    private final BuildingRepository buildingRepository = mock(BuildingRepository.class);
    private final PoiRepository poiRepository = mock(PoiRepository.class);
    private final MapFeatureRepository mapFeatureRepository = mock(MapFeatureRepository.class);
    private MapFeatureService service;

    @BeforeEach
    void setUp() {
        service = new MapFeatureService(
                new ObjectMapper(), campusRepository, buildingRepository, poiRepository, mapFeatureRepository
        );
        when(campusRepository.findByCodeAndEnabledTrue(CAMPUS_CODE))
                .thenReturn(Optional.of(mock(Campus.class)));
        when(mapFeatureRepository.findAllByCampusCodeAndEnabledTrueOrderByPriorityDescNameAsc(CAMPUS_CODE))
                .thenReturn(List.of());
        when(buildingRepository.findAllByCampusCodeAndEnabledTrueOrderByNameAsc(CAMPUS_CODE))
                .thenReturn(List.of());
        when(poiRepository.findAllByCampusCodeAndEnabledTrueOrderByNameAsc(CAMPUS_CODE))
                .thenReturn(List.of());
    }

    @Test
    void returnsAnEmptyFeatureCollectionWhenCampusHasNoData() {
        ObjectNode result = service.load(CAMPUS_CODE);

        assertThat(result.path("type").asText()).isEqualTo("FeatureCollection");
        assertThat(result.path("features")).isEmpty();
    }

    @Test
    void serializesLongitudeBeforeLatitudeAndKeepsStableId() {
        GeometryFactory geometryFactory = new GeometryFactory();
        Polygon polygon = geometryFactory.createPolygon(new Coordinate[]{
                new Coordinate(118.9100, 32.1020),
                new Coordinate(118.9110, 32.1020),
                new Coordinate(118.9110, 32.1030),
                new Coordinate(118.9100, 32.1020)
        });
        polygon.setSRID(4326);
        Building building = new Building();
        building.updateFromImport(
                mock(Campus.class), "demo-building", "演示楼", "教学演示楼", "演示楼", true,
                List.of("演示教学楼"), "TEACHING",
                geometryFactory.createMultiPolygon(new Polygon[]{polygon}), 24.0, 0, "#8CA8C8",
                "OSM_HEIGHT", "OPENSTREETMAP", "SOURCE_VERIFIED", "osm-test", null, true
        );
        when(buildingRepository.findAllByCampusCodeAndEnabledTrueOrderByNameAsc(CAMPUS_CODE))
                .thenReturn(List.of(building));

        ObjectNode result = service.load(CAMPUS_CODE);

        assertThat(result.at("/features/0/id").asText()).isEqualTo("demo-building");
        assertThat(result.at("/features/0/properties/featureType").asText()).isEqualTo("BUILDING");
        assertThat(result.at("/features/0/properties/displayName").asText()).isEqualTo("演示楼");
        assertThat(result.at("/features/0/properties/officialName").asText()).isEqualTo("教学演示楼");
        assertThat(result.at("/features/0/properties/aliases/0").asText()).isEqualTo("演示教学楼");
        assertThat(result.at("/features/0/properties/labelVisible").asBoolean()).isTrue();
        assertThat(result.at("/features/0/geometry/coordinates/0/0/0/0").asDouble())
                .isEqualTo(118.9100);
        assertThat(result.at("/features/0/geometry/coordinates/0/0/0/1").asDouble())
                .isEqualTo(32.1020);
        assertThat(result.at("/features/0/geometry").has("crs")).isFalse();
    }
}

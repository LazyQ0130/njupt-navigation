package cn.edu.njupt.map.importer;

import cn.edu.njupt.map.domain.Building;
import cn.edu.njupt.map.domain.Campus;
import cn.edu.njupt.map.domain.Poi;
import cn.edu.njupt.map.domain.MapFeature;
import cn.edu.njupt.map.importer.GeoJsonImportResult.ImportError;
import cn.edu.njupt.map.repository.BuildingRepository;
import cn.edu.njupt.map.repository.CampusRepository;
import cn.edu.njupt.map.repository.PoiRepository;
import cn.edu.njupt.map.repository.MapFeatureRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import org.locationtech.jts.geom.Coordinate;
import org.locationtech.jts.geom.Geometry;
import org.locationtech.jts.geom.GeometryFactory;
import org.locationtech.jts.geom.MultiPolygon;
import org.locationtech.jts.geom.Point;
import org.locationtech.jts.geom.Polygon;
import org.locationtech.jts.io.ParseException;
import org.locationtech.jts.io.geojson.GeoJsonReader;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class GeoJsonImportService {

    private static final int WGS84_SRID = 4326;
    private static final String DEFAULT_CAMPUS_CODE = "NJUPT_XIANLIN";
    private static final List<String> BUILDING_CATEGORIES = List.of(
            "TEACHING", "DORMITORY", "DINING", "LIBRARY", "SPORT", "MEDICAL", "EXPRESS",
            "SHOP", "SERVICE", "ADMINISTRATION", "ENTRANCE", "NEW_STUDENT", "OTHER"
    );
    private static final List<String> POI_CATEGORIES = BUILDING_CATEGORIES;
    private static final List<String> MAP_FEATURE_TYPES = List.of(
            "CAMPUS_BOUNDARY", "GREEN", "WATER", "SPORT", "PLAZA",
            "ROAD_MAIN", "ROAD_PEDESTRIAN"
    );

    private final ObjectMapper objectMapper;
    private final CampusRepository campusRepository;
    private final BuildingRepository buildingRepository;
    private final PoiRepository poiRepository;
    private final MapFeatureRepository mapFeatureRepository;
    private final int maxFeatures;
    private final GeometryFactory geometryFactory = new GeometryFactory();

    public GeoJsonImportService(ObjectMapper objectMapper, CampusRepository campusRepository,
                                BuildingRepository buildingRepository, PoiRepository poiRepository,
                                MapFeatureRepository mapFeatureRepository,
                                @Value("${app.import.max-features:5000}") int maxFeatures) {
        this.objectMapper = objectMapper;
        this.campusRepository = campusRepository;
        this.buildingRepository = buildingRepository;
        this.poiRepository = poiRepository;
        this.mapFeatureRepository = mapFeatureRepository;
        this.maxFeatures = maxFeatures;
    }

    @Transactional
    public GeoJsonImportResult importFeatureCollection(InputStream inputStream) throws IOException {
        JsonNode root = objectMapper.readTree(inputStream);
        if (!"FeatureCollection".equals(root.path("type").asText())) {
            throw new IllegalArgumentException("GeoJSON 根对象必须是 FeatureCollection");
        }

        JsonNode features = root.path("features");
        if (!features.isArray()) {
            throw new IllegalArgumentException("GeoJSON features 必须是数组");
        }
        if (features.size() > maxFeatures) {
            throw new IllegalArgumentException("单次导入最多允许 " + maxFeatures + " 个 Feature");
        }

        List<ImportError> errors = new ArrayList<>();
        int created = 0;
        int updated = 0;

        for (int index = 0; index < features.size(); index++) {
            JsonNode feature = features.get(index);
            String externalId = feature.path("properties").path("externalId").asText(null);
            try {
                boolean wasCreated = importFeature(feature);
                if (wasCreated) {
                    created++;
                } else {
                    updated++;
                }
            } catch (IllegalArgumentException | ParseException exception) {
                errors.add(new ImportError(index, externalId, exception.getMessage()));
            }
        }

        int succeeded = created + updated;
        return new GeoJsonImportResult(features.size(), succeeded, errors.size(), created, updated, errors);
    }

    private boolean importFeature(JsonNode feature) throws ParseException {
        if (!"Feature".equals(feature.path("type").asText())) {
            throw new IllegalArgumentException("对象 type 必须是 Feature");
        }

        JsonNode properties = feature.path("properties");
        String featureType = requiredText(properties, "featureType").toUpperCase(Locale.ROOT);
        String campusCode = optionalText(properties, "campusCode").orElse(DEFAULT_CAMPUS_CODE);
        Campus campus = campusRepository.findByCodeAndEnabledTrue(campusCode)
                .orElseThrow(() -> new IllegalArgumentException("找不到启用的校区: " + campusCode));
        Geometry geometry = readGeometry(feature.path("geometry"));

        return switch (featureType) {
            case "BUILDING" -> importBuilding(campus, properties, geometry);
            case "POI" -> importPoi(campus, properties, geometry);
            case "CAMPUS_BOUNDARY", "GREEN", "WATER", "SPORT", "PLAZA",
                    "ROAD_MAIN", "ROAD_PEDESTRIAN" -> importMapFeature(
                            campus, featureType, properties, geometry
                    );
            default -> throw new IllegalArgumentException("不支持的 featureType: " + featureType);
        };
    }

    private boolean importMapFeature(Campus campus, String featureType, JsonNode properties,
                                     Geometry geometry) {
        if (!MAP_FEATURE_TYPES.contains(featureType)) {
            throw new IllegalArgumentException("不支持的地图要素类型: " + featureType);
        }
        boolean road = featureType.startsWith("ROAD_");
        boolean validType = road
                ? "LineString".equals(geometry.getGeometryType())
                        || "MultiLineString".equals(geometry.getGeometryType())
                : geometry instanceof Polygon || geometry instanceof MultiPolygon;
        if (!validType) {
            throw new IllegalArgumentException(road
                    ? "道路 Geometry 必须是 LineString 或 MultiLineString"
                    : "面状地图要素 Geometry 必须是 Polygon 或 MultiPolygon");
        }
        validateGeometry(geometry);

        String externalId = requiredText(properties, "externalId");
        Optional<MapFeature> existing = mapFeatureRepository.findByExternalId(externalId);
        MapFeature mapFeature = existing.orElseGet(MapFeature::new);
        mapFeature.updateFromImport(
                campus,
                externalId,
                requiredText(properties, "name"),
                featureType,
                geometry,
                optionalText(properties, "color").orElse(null),
                properties.path("priority").asInt(0),
                properties.path("enabled").asBoolean(true)
        );
        mapFeatureRepository.save(mapFeature);
        return existing.isEmpty();
    }

    private boolean importBuilding(Campus campus, JsonNode properties, Geometry geometry) {
        MultiPolygon multiPolygon = toMultiPolygon(geometry);
        validateGeometry(multiPolygon);

        String externalId = requiredText(properties, "externalId");
        String name = requiredText(properties, "name");
        String category = validatedCategory(properties, BUILDING_CATEGORIES);
        double height = properties.path("height").asDouble(10);
        double minHeight = properties.path("minHeight").asDouble(0);
        if (minHeight < 0 || height < minHeight) {
            throw new IllegalArgumentException("建筑高度必须满足 0 <= minHeight <= height");
        }

        Optional<Building> existing = buildingRepository.findByExternalId(externalId);
        Building building = existing.orElseGet(Building::new);
        building.updateFromImport(
                campus,
                externalId,
                name,
                textArray(properties, "aliases"),
                category,
                multiPolygon,
                height,
                minHeight,
                optionalText(properties, "color").orElse("#D7E3F4"),
                properties.path("enabled").asBoolean(true)
        );
        buildingRepository.save(building);
        return existing.isEmpty();
    }

    private boolean importPoi(Campus campus, JsonNode properties, Geometry geometry) {
        if (!(geometry instanceof Point point)) {
            throw new IllegalArgumentException("POI Geometry 必须是 Point");
        }
        validateGeometry(point);

        String externalId = requiredText(properties, "externalId");
        Optional<Poi> existing = poiRepository.findByExternalId(externalId);
        Poi poi = existing.orElseGet(Poi::new);
        poi.updateFromImport(
                campus,
                externalId,
                requiredText(properties, "name"),
                textArray(properties, "aliases"),
                textArray(properties, "keywords"),
                validatedCategory(properties, POI_CATEGORIES),
                point,
                properties.path("enabled").asBoolean(true)
        );
        poiRepository.save(poi);
        return existing.isEmpty();
    }

    private Geometry readGeometry(JsonNode geometryNode) throws ParseException {
        if (geometryNode.isMissingNode() || geometryNode.isNull()) {
            throw new IllegalArgumentException("Feature 缺少 geometry");
        }
        Geometry geometry = new GeoJsonReader(geometryFactory).read(geometryNode.toString());
        geometry.setSRID(WGS84_SRID);
        return geometry;
    }

    private MultiPolygon toMultiPolygon(Geometry geometry) {
        if (geometry instanceof MultiPolygon multiPolygon) {
            return multiPolygon;
        }
        if (geometry instanceof Polygon polygon) {
            MultiPolygon multiPolygon = geometryFactory.createMultiPolygon(new Polygon[]{polygon});
            multiPolygon.setSRID(WGS84_SRID);
            return multiPolygon;
        }
        throw new IllegalArgumentException("Building Geometry 必须是 Polygon 或 MultiPolygon");
    }

    private void validateGeometry(Geometry geometry) {
        if (geometry.isEmpty()) {
            throw new IllegalArgumentException("Geometry 不能为空");
        }
        if (!geometry.isValid()) {
            throw new IllegalArgumentException("Geometry 不合法（可能存在自交或未闭合）");
        }
        for (Coordinate coordinate : geometry.getCoordinates()) {
            if (!Double.isFinite(coordinate.x) || !Double.isFinite(coordinate.y)
                    || coordinate.x < -180 || coordinate.x > 180
                    || coordinate.y < -90 || coordinate.y > 90) {
                throw new IllegalArgumentException("坐标超出 WGS84 合法范围");
            }
        }
    }

    private String validatedCategory(JsonNode properties, List<String> allowed) {
        String category = requiredText(properties, "category").toUpperCase(Locale.ROOT);
        if (!allowed.contains(category)) {
            throw new IllegalArgumentException("不支持的 category: " + category);
        }
        return category;
    }

    private String requiredText(JsonNode node, String field) {
        return optionalText(node, field)
                .orElseThrow(() -> new IllegalArgumentException("缺少必填字段 properties." + field));
    }

    private Optional<String> optionalText(JsonNode node, String field) {
        String value = node.path(field).asText(null);
        if (value == null || value.isBlank()) {
            return Optional.empty();
        }
        return Optional.of(value.trim());
    }

    private List<String> textArray(JsonNode node, String field) {
        JsonNode value = node.path(field);
        if (value.isMissingNode() || value.isNull()) {
            return List.of();
        }
        if (!value.isArray()) {
            throw new IllegalArgumentException("properties." + field + " 必须是字符串数组");
        }

        List<String> result = new ArrayList<>();
        Iterator<JsonNode> elements = value.elements();
        while (elements.hasNext()) {
            JsonNode element = elements.next();
            if (!element.isTextual() || element.asText().isBlank()) {
                throw new IllegalArgumentException("properties." + field + " 必须只包含非空字符串");
            }
            result.add(element.asText().trim());
        }
        return List.copyOf(result);
    }
}

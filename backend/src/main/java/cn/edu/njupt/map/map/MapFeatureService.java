package cn.edu.njupt.map.map;

import cn.edu.njupt.map.domain.Building;
import cn.edu.njupt.map.domain.MapFeature;
import cn.edu.njupt.map.domain.Poi;
import cn.edu.njupt.map.repository.BuildingRepository;
import cn.edu.njupt.map.repository.CampusRepository;
import cn.edu.njupt.map.repository.MapFeatureRepository;
import cn.edu.njupt.map.repository.PoiRepository;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.util.function.Consumer;
import org.locationtech.jts.geom.Geometry;
import org.locationtech.jts.io.geojson.GeoJsonWriter;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class MapFeatureService {

    private static final String SCHEMA_VERSION = "2026-08-phase1";

    private final ObjectMapper objectMapper;
    private final CampusRepository campusRepository;
    private final BuildingRepository buildingRepository;
    private final PoiRepository poiRepository;
    private final MapFeatureRepository mapFeatureRepository;

    public MapFeatureService(ObjectMapper objectMapper, CampusRepository campusRepository,
                             BuildingRepository buildingRepository, PoiRepository poiRepository,
                             MapFeatureRepository mapFeatureRepository) {
        this.objectMapper = objectMapper;
        this.campusRepository = campusRepository;
        this.buildingRepository = buildingRepository;
        this.poiRepository = poiRepository;
        this.mapFeatureRepository = mapFeatureRepository;
    }

    @Transactional(readOnly = true)
    public ObjectNode load(String campusCode) {
        campusRepository.findByCodeAndEnabledTrue(campusCode)
                .orElseThrow(() -> new IllegalArgumentException("找不到启用的校区: " + campusCode));

        ObjectNode collection = objectMapper.createObjectNode();
        collection.put("type", "FeatureCollection");
        collection.put("schemaVersion", SCHEMA_VERSION);
        collection.put("campusCode", campusCode);
        ArrayNode features = collection.putArray("features");

        mapFeatureRepository.findAllByCampusCodeAndEnabledTrueOrderByPriorityDescNameAsc(campusCode)
                .forEach(item -> features.add(mapFeature(item)));
        buildingRepository.findAllByCampusCodeAndEnabledTrueOrderByNameAsc(campusCode)
                .forEach(item -> features.add(buildingFeature(item)));
        poiRepository.findAllByCampusCodeAndEnabledTrueOrderByNameAsc(campusCode)
                .forEach(item -> features.add(poiFeature(item)));
        return collection;
    }

    private ObjectNode mapFeature(MapFeature item) {
        return feature(
                item.getExternalId(), item.getName(), item.getFeatureType(), item.getGeometry(),
                properties -> {
                    putIfPresent(properties, "color", item.getColor());
                    properties.put("priority", item.getPriority());
                }
        );
    }

    private ObjectNode buildingFeature(Building item) {
        return feature(
                item.getExternalId(), item.getName(), "BUILDING", item.getGeometry(),
                properties -> {
                    properties.put("category", item.getCategory());
                    properties.put("height", item.getHeight());
                    properties.put("minHeight", item.getMinHeight());
                    putIfPresent(properties, "color", item.getColor());
                    properties.put("priority", buildingPriority(item.getCategory()));
                }
        );
    }

    private ObjectNode poiFeature(Poi item) {
        return feature(
                item.getExternalId(), item.getName(), "POI", item.getLocation(),
                properties -> {
                    properties.put("category", item.getCategory());
                    properties.put("priority", 40);
                }
        );
    }

    private ObjectNode feature(String externalId, String name, String featureType,
                               Geometry geometry, Consumer<ObjectNode> customProperties) {
        String stableId = externalId;
        ObjectNode feature = objectMapper.createObjectNode();
        feature.put("type", "Feature");
        feature.put("id", stableId);
        feature.set("geometry", geometryNode(geometry));
        ObjectNode properties = feature.putObject("properties");
        properties.put("id", stableId);
        properties.put("featureType", featureType);
        properties.put("name", name);
        customProperties.accept(properties);
        return feature;
    }

    private ObjectNode geometryNode(Geometry geometry) {
        try {
            GeoJsonWriter writer = new GeoJsonWriter();
            writer.setEncodeCRS(false);
            return (ObjectNode) objectMapper.readTree(writer.write(geometry));
        } catch (JsonProcessingException exception) {
            throw new IllegalStateException("地图要素序列化失败", exception);
        }
    }

    private int buildingPriority(String category) {
        return switch (category) {
            case "LIBRARY", "ADMINISTRATION", "MEDICAL" -> 90;
            case "TEACHING", "DINING", "SPORT" -> 70;
            default -> 50;
        };
    }

    private void putIfPresent(ObjectNode node, String field, String value) {
        if (value != null && !value.isBlank()) {
            node.put(field, value);
        }
    }
}

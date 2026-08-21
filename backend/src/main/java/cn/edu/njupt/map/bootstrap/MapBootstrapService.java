package cn.edu.njupt.map.bootstrap;

import cn.edu.njupt.map.bootstrap.MapBootstrapResponse.Camera;
import cn.edu.njupt.map.bootstrap.MapBootstrapResponse.Bounds;
import cn.edu.njupt.map.bootstrap.MapBootstrapResponse.CampusSummary;
import cn.edu.njupt.map.bootstrap.MapBootstrapResponse.DataSummary;
import cn.edu.njupt.map.bootstrap.MapBootstrapResponse.LayerAvailability;
import cn.edu.njupt.map.repository.BuildingRepository;
import cn.edu.njupt.map.repository.CampusRepository;
import cn.edu.njupt.map.repository.PoiRepository;
import cn.edu.njupt.map.repository.MapFeatureRepository;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class MapBootstrapService {

    private final CampusRepository campusRepository;
    private final BuildingRepository buildingRepository;
    private final PoiRepository poiRepository;
    private final MapFeatureRepository mapFeatureRepository;

    public MapBootstrapService(CampusRepository campusRepository, BuildingRepository buildingRepository,
                               PoiRepository poiRepository, MapFeatureRepository mapFeatureRepository) {
        this.campusRepository = campusRepository;
        this.buildingRepository = buildingRepository;
        this.poiRepository = poiRepository;
        this.mapFeatureRepository = mapFeatureRepository;
    }

    @Transactional(readOnly = true)
    public MapBootstrapResponse load() {
        List<CampusSummary> campuses = campusRepository.findAllByEnabledTrueOrderByNameAsc().stream()
                .map(campus -> {
                    long buildings = buildingRepository.countByCampusIdAndEnabledTrue(campus.getId());
                    long pois = poiRepository.countByCampusIdAndEnabledTrue(campus.getId());
                    long mapFeatures = mapFeatureRepository.countByCampusIdAndEnabledTrue(campus.getId());
                    boolean ground = mapFeatureRepository.existsByCampusIdAndFeatureTypeInAndEnabledTrue(
                            campus.getId(), List.of("CAMPUS_BOUNDARY", "GREEN", "WATER", "SPORT", "PLAZA")
                    );
                    boolean roads = mapFeatureRepository.existsByCampusIdAndFeatureTypeInAndEnabledTrue(
                            campus.getId(), List.of("ROAD_MAIN", "ROAD_PEDESTRIAN")
                    );
                    return new CampusSummary(
                        campus.getId(),
                        campus.getCode(),
                        campus.getName(),
                        new Camera(
                                campus.getDefaultLongitude(),
                                campus.getDefaultLatitude(),
                                campus.getDefaultZoom(),
                                campus.getDefaultPitch(),
                                campus.getDefaultBearing()
                        ),
                        new Bounds(
                                campus.getDefaultLongitude() - 0.0065,
                                campus.getDefaultLatitude() - 0.0045,
                                campus.getDefaultLongitude() + 0.0065,
                                campus.getDefaultLatitude() + 0.0045
                        ),
                        new DataSummary(buildings, pois, mapFeatures),
                        new LayerAvailability(buildings > 0, ground, roads, pois > 0)
                    );
                })
                .toList();

        return new MapBootstrapResponse("2026-08-phase1", campuses);
    }
}

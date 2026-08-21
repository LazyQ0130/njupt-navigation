package cn.edu.njupt.map.bootstrap;

import cn.edu.njupt.map.bootstrap.MapBootstrapResponse.Camera;
import cn.edu.njupt.map.bootstrap.MapBootstrapResponse.CampusSummary;
import cn.edu.njupt.map.bootstrap.MapBootstrapResponse.DataSummary;
import cn.edu.njupt.map.repository.BuildingRepository;
import cn.edu.njupt.map.repository.CampusRepository;
import cn.edu.njupt.map.repository.PoiRepository;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class MapBootstrapService {

    private final CampusRepository campusRepository;
    private final BuildingRepository buildingRepository;
    private final PoiRepository poiRepository;

    public MapBootstrapService(CampusRepository campusRepository, BuildingRepository buildingRepository,
                               PoiRepository poiRepository) {
        this.campusRepository = campusRepository;
        this.buildingRepository = buildingRepository;
        this.poiRepository = poiRepository;
    }

    @Transactional(readOnly = true)
    public MapBootstrapResponse load() {
        List<CampusSummary> campuses = campusRepository.findAllByEnabledTrueOrderByNameAsc().stream()
                .map(campus -> new CampusSummary(
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
                        new DataSummary(
                                buildingRepository.countByCampusIdAndEnabledTrue(campus.getId()),
                                poiRepository.countByCampusIdAndEnabledTrue(campus.getId())
                        )
                ))
                .toList();

        return new MapBootstrapResponse("2026-08-phase0", campuses);
    }
}


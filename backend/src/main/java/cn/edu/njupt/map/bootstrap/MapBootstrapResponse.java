package cn.edu.njupt.map.bootstrap;

import java.util.List;
import java.util.UUID;

public record MapBootstrapResponse(
        String schemaVersion,
        List<CampusSummary> campuses
) {

    public record CampusSummary(
            UUID id,
            String code,
            String name,
            Camera camera,
            DataSummary data
    ) {
    }

    public record Camera(
            double longitude,
            double latitude,
            double zoom,
            double pitch,
            double bearing
    ) {
    }

    public record DataSummary(long buildings, long pois) {
    }
}


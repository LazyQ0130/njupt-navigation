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
            Bounds bounds,
            DataSummary data,
            LayerAvailability layers
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

    public record Bounds(double west, double south, double east, double north) {
    }

    public record DataSummary(long buildings, long pois, long mapFeatures) {
    }

    public record LayerAvailability(boolean buildings, boolean ground, boolean roads, boolean pois) {
    }
}

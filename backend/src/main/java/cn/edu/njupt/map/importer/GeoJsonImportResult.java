package cn.edu.njupt.map.importer;

import java.util.List;

public record GeoJsonImportResult(
        int total,
        int succeeded,
        int failed,
        int created,
        int updated,
        List<ImportError> errors
) {

    public record ImportError(int featureIndex, String externalId, String reason) {
    }
}


package cn.edu.njupt.map.importer;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.boot.autoconfigure.condition.ConditionalOnExpression;
import org.springframework.stereotype.Component;
import org.springframework.context.annotation.Profile;

@Component
@Profile("!prod")
@ConditionalOnExpression("'${app.import.bootstrap-file:}'.length() > 0"
        + " or '${app.import.bootstrap-directory:}'.length() > 0")
public class BootstrapGeoJsonImporter implements ApplicationRunner {

    private static final Logger LOGGER = LoggerFactory.getLogger(BootstrapGeoJsonImporter.class);
    private static final List<String> REAL_DATA_FILES = List.of(
            "campus.geojson", "surfaces.geojson", "buildings.geojson",
            "pois.geojson", "roads.geojson", "entrances.geojson"
    );

    private final GeoJsonImportService importService;
    private final Path source;
    private final Path sourceDirectory;
    private final String datasetMode;

    public BootstrapGeoJsonImporter(
            GeoJsonImportService importService,
            @Value("${app.import.bootstrap-file:}") String source,
            @Value("${app.import.bootstrap-directory:}") String sourceDirectory,
            @Value("${app.import.bootstrap-dataset-mode:demo}") String datasetMode) {
        this.importService = importService;
        this.source = normalizedPath(source);
        this.sourceDirectory = normalizedPath(sourceDirectory);
        this.datasetMode = datasetMode;
    }

    @Override
    public void run(ApplicationArguments arguments) throws IOException {
        if (sourceDirectory != null) {
            importService.prepareDatasetRefresh(datasetMode);
            importDirectory();
            LOGGER.info("Bootstrap GeoJSON authoritative dataset refreshed: mode={}", datasetMode);
            return;
        }
        importFile(source);
    }

    private void importDirectory() throws IOException {
        if (!Files.isDirectory(sourceDirectory)) {
            throw new IllegalStateException("启动 GeoJSON 目录不存在: " + sourceDirectory);
        }
        for (String fileName : REAL_DATA_FILES) {
            importFile(sourceDirectory.resolve(fileName));
        }
    }

    private void importFile(Path file) throws IOException {
        if (file == null || !Files.isRegularFile(file)) {
            throw new IllegalStateException("启动 GeoJSON 文件不存在: " + file);
        }
        try (var inputStream = Files.newInputStream(file)) {
            GeoJsonImportResult result = importService.importFeatureCollection(inputStream);
            if (result.failed() > 0) {
                throw new IllegalStateException("启动 GeoJSON 导入失败: " + file + " " + result.errors());
            }
            LOGGER.info("Bootstrap GeoJSON imported: file={}, total={}, created={}, updated={}",
                    file, result.total(), result.created(), result.updated());
        }
    }

    private static Path normalizedPath(String value) {
        if (value == null || value.isBlank()) {
            return null;
        }
        return Path.of(value).toAbsolutePath().normalize();
    }
}

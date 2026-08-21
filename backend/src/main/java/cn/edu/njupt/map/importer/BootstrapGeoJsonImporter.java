package cn.edu.njupt.map.importer;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.boot.autoconfigure.condition.ConditionalOnExpression;
import org.springframework.stereotype.Component;

@Component
@ConditionalOnExpression("'${app.import.bootstrap-file:}'.length() > 0")
public class BootstrapGeoJsonImporter implements ApplicationRunner {

    private static final Logger LOGGER = LoggerFactory.getLogger(BootstrapGeoJsonImporter.class);

    private final GeoJsonImportService importService;
    private final Path source;

    public BootstrapGeoJsonImporter(
            GeoJsonImportService importService,
            @Value("${app.import.bootstrap-file}") String source) {
        this.importService = importService;
        this.source = Path.of(source).toAbsolutePath().normalize();
    }

    @Override
    public void run(ApplicationArguments arguments) throws IOException {
        if (!Files.isRegularFile(source)) {
            throw new IllegalStateException("启动 GeoJSON 文件不存在: " + source);
        }
        try (var inputStream = Files.newInputStream(source)) {
            GeoJsonImportResult result = importService.importFeatureCollection(inputStream);
            if (result.failed() > 0) {
                throw new IllegalStateException("启动 GeoJSON 导入失败: " + result.errors());
            }
            LOGGER.info("Bootstrap GeoJSON imported: total={}, created={}, updated={}",
                    result.total(), result.created(), result.updated());
        }
    }
}

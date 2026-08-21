package cn.edu.njupt.map.importer;

import java.io.IOException;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/admin/imports")
public class GeoJsonImportController {

    private final GeoJsonImportService importService;

    public GeoJsonImportController(GeoJsonImportService importService) {
        this.importService = importService;
    }

    @PostMapping(value = "/geojson", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public GeoJsonImportResult importGeoJson(@RequestPart("file") MultipartFile file) throws IOException {
        if (file.isEmpty()) {
            throw new IllegalArgumentException("上传文件不能为空");
        }
        try (var inputStream = file.getInputStream()) {
            return importService.importFeatureCollection(inputStream);
        }
    }
}


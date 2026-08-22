package cn.edu.njupt.map.map;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Map;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Profile;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/map/review")
@Profile("!prod")
public class GisReviewController {

    private static final Map<String, String> REVIEW_LAYERS = Map.of(
            "topology-gaps", "topology-gaps.geojson",
            "road-building-intersections", "road-building-intersections.geojson",
            "unverified-buildings", "unverified-buildings.geojson",
            "unverified-pois", "unverified-pois.geojson",
            "candidate-entrances", "candidate-entrances.geojson",
            "dormitory-candidates", "dormitory-candidates.geojson"
    );

    private final ObjectMapper objectMapper;
    private final Path reviewDirectory;

    public GisReviewController(ObjectMapper objectMapper,
                               @Value("${app.review.directory}") String reviewDirectory) {
        this.objectMapper = objectMapper;
        this.reviewDirectory = Path.of(reviewDirectory).toAbsolutePath().normalize();
    }

    @GetMapping("/{layer}")
    public JsonNode layer(@PathVariable String layer) throws IOException {
        String filename = REVIEW_LAYERS.get(layer);
        if (filename == null) {
            throw new IllegalArgumentException("不支持的 GIS review layer: " + layer);
        }
        return objectMapper.readTree(reviewDirectory.resolve(filename).toFile());
    }
}

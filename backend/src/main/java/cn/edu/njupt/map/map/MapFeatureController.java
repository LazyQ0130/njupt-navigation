package cn.edu.njupt.map.map;

import com.fasterxml.jackson.databind.node.ObjectNode;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/map")
public class MapFeatureController {

    private final MapFeatureService service;

    public MapFeatureController(MapFeatureService service) {
        this.service = service;
    }

    @GetMapping("/features")
    public ObjectNode features(
            @RequestParam(defaultValue = "NJUPT_XIANLIN") String campusCode) {
        return service.load(campusCode);
    }
}

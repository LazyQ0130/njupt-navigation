package cn.edu.njupt.map.bootstrap;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/map")
public class MapBootstrapController {

    private final MapBootstrapService service;

    public MapBootstrapController(MapBootstrapService service) {
        this.service = service;
    }

    @GetMapping("/bootstrap")
    public MapBootstrapResponse bootstrap() {
        return service.load();
    }
}


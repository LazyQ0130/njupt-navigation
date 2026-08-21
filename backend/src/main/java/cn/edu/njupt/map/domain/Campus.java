package cn.edu.njupt.map.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;
import org.locationtech.jts.geom.MultiPolygon;

@Entity
@Table(name = "campus")
public class Campus {

    @Id
    private UUID id;

    @Column(nullable = false, unique = true, length = 64)
    private String code;

    @Column(nullable = false, length = 128)
    private String name;

    @Column(columnDefinition = "geometry(MultiPolygon,4326)")
    private MultiPolygon boundary;

    @Column(name = "default_longitude", nullable = false)
    private double defaultLongitude;

    @Column(name = "default_latitude", nullable = false)
    private double defaultLatitude;

    @Column(name = "default_zoom", nullable = false)
    private double defaultZoom;

    @Column(name = "default_pitch", nullable = false)
    private double defaultPitch;

    @Column(name = "default_bearing", nullable = false)
    private double defaultBearing;

    @Column(nullable = false)
    private boolean enabled;

    @Column(name = "created_at", nullable = false, insertable = false, updatable = false)
    private Instant createdAt;

    @Column(name = "updated_at", nullable = false, insertable = false)
    private Instant updatedAt;

    protected Campus() {
    }

    public UUID getId() {
        return id;
    }

    public String getCode() {
        return code;
    }

    public String getName() {
        return name;
    }

    public double getDefaultLongitude() {
        return defaultLongitude;
    }

    public double getDefaultLatitude() {
        return defaultLatitude;
    }

    public double getDefaultZoom() {
        return defaultZoom;
    }

    public double getDefaultPitch() {
        return defaultPitch;
    }

    public double getDefaultBearing() {
        return defaultBearing;
    }
}


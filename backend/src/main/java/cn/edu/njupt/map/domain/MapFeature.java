package cn.edu.njupt.map.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;
import org.locationtech.jts.geom.Geometry;

@Entity
@Table(name = "map_feature")
public class MapFeature {

    @Id
    @GeneratedValue
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "campus_id", nullable = false)
    private Campus campus;

    @Column(name = "external_id", nullable = false, unique = true, length = 128)
    private String externalId;

    @Column(nullable = false, length = 160)
    private String name;

    @Column(name = "feature_type", nullable = false, length = 40)
    private String featureType;

    @Column(nullable = false, columnDefinition = "geometry(Geometry,4326)")
    private Geometry geometry;

    @Column(length = 16)
    private String color;

    @Column(nullable = false)
    private int priority;

    @Column(nullable = false)
    private boolean enabled;

    @Column(name = "created_at", nullable = false, insertable = false, updatable = false)
    private Instant createdAt;

    @Column(name = "updated_at", nullable = false, insertable = false)
    private Instant updatedAt;

    public MapFeature() {
    }

    public void updateFromImport(Campus campus, String externalId, String name, String featureType,
                                 Geometry geometry, String color, int priority, boolean enabled) {
        this.campus = campus;
        this.externalId = externalId;
        this.name = name;
        this.featureType = featureType;
        this.geometry = geometry;
        this.color = color;
        this.priority = priority;
        this.enabled = enabled;
        this.updatedAt = Instant.now();
    }

    public UUID getId() {
        return id;
    }

    public String getExternalId() {
        return externalId;
    }

    public String getName() {
        return name;
    }

    public String getFeatureType() {
        return featureType;
    }

    public Geometry getGeometry() {
        return geometry;
    }

    public String getColor() {
        return color;
    }

    public int getPriority() {
        return priority;
    }
}

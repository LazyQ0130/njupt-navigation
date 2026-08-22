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
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;
import org.locationtech.jts.geom.MultiPolygon;

@Entity
@Table(name = "building")
public class Building {

    @Id
    @GeneratedValue
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "campus_id", nullable = false)
    private Campus campus;

    @Column(name = "external_id", unique = true, length = 128)
    private String externalId;

    @Column(nullable = false, length = 160)
    private String name;

    @Column(name = "official_name", length = 200)
    private String officialName;

    @Column(name = "display_name", length = 160)
    private String displayName;

    @Column(name = "label_visible", nullable = false)
    private boolean labelVisible;

    @Column(name = "dormitory_zone", length = 40)
    private String dormitoryZone;

    @Column(name = "building_number", length = 16)
    private String buildingNumber;

    @JdbcTypeCode(SqlTypes.ARRAY)
    @Column(nullable = false, columnDefinition = "text[]")
    private List<String> aliases = new ArrayList<>();

    @Column(nullable = false, length = 40)
    private String category;

    @Column(nullable = false, columnDefinition = "geometry(MultiPolygon,4326)")
    private MultiPolygon geometry;

    @Column(nullable = false)
    private Double height;

    @Column(name = "min_height", nullable = false)
    private double minHeight;

    @Column(nullable = false, length = 16)
    private String color;

    @Column(name = "height_source", nullable = false, length = 40)
    private String heightSource;

    @Column(name = "data_source", nullable = false, length = 40)
    private String dataSource;

    @Column(name = "verification_status", nullable = false, length = 40)
    private String verificationStatus;

    @Column(name = "source_id", length = 128)
    private String sourceId;

    @Column(name = "source_updated_at")
    private Instant sourceUpdatedAt;

    @Column(nullable = false)
    private boolean enabled;

    @Column(name = "created_at", nullable = false, insertable = false, updatable = false)
    private Instant createdAt;

    @Column(name = "updated_at", nullable = false, insertable = false)
    private Instant updatedAt;

    public Building() {
    }

    public void updateFromImport(Campus campus, String externalId, String name, String officialName,
                                 String displayName, boolean labelVisible, List<String> aliases,
                                 String dormitoryZone, String buildingNumber,
                                 String category, MultiPolygon geometry, Double height, double minHeight,
                                 String color, String heightSource, String dataSource,
                                 String verificationStatus, String sourceId, Instant sourceUpdatedAt,
                                 boolean enabled) {
        this.campus = campus;
        this.externalId = externalId;
        this.name = name;
        this.officialName = officialName;
        this.displayName = displayName;
        this.labelVisible = labelVisible;
        this.aliases = new ArrayList<>(aliases);
        this.dormitoryZone = dormitoryZone;
        this.buildingNumber = buildingNumber;
        this.category = category;
        this.geometry = geometry;
        this.height = height;
        this.minHeight = minHeight;
        this.color = color;
        this.heightSource = heightSource;
        this.dataSource = dataSource;
        this.verificationStatus = verificationStatus;
        this.sourceId = sourceId;
        this.sourceUpdatedAt = sourceUpdatedAt;
        this.enabled = enabled;
        this.updatedAt = Instant.now();
    }

    public UUID getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getOfficialName() {
        return officialName;
    }

    public String getDisplayName() {
        return displayName;
    }

    public boolean isLabelVisible() {
        return labelVisible;
    }

    public List<String> getAliases() {
        return List.copyOf(aliases);
    }

    public String getDormitoryZone() {
        return dormitoryZone;
    }

    public String getBuildingNumber() {
        return buildingNumber;
    }

    public String getExternalId() {
        return externalId;
    }

    public String getCategory() {
        return category;
    }

    public MultiPolygon getGeometry() {
        return geometry;
    }

    public Double getHeight() {
        return height;
    }

    public double getMinHeight() {
        return minHeight;
    }

    public String getColor() {
        return color;
    }

    public String getHeightSource() {
        return heightSource;
    }

    public String getDataSource() {
        return dataSource;
    }

    public String getVerificationStatus() {
        return verificationStatus;
    }

    public String getSourceId() {
        return sourceId;
    }

    public Instant getSourceUpdatedAt() {
        return sourceUpdatedAt;
    }
}

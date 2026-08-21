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
import org.locationtech.jts.geom.Point;

@Entity
@Table(name = "poi")
public class Poi {

    @Id
    @GeneratedValue
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "campus_id", nullable = false)
    private Campus campus;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "building_id")
    private Building building;

    @Column(name = "external_id", unique = true, length = 128)
    private String externalId;

    @Column(nullable = false, length = 160)
    private String name;

    @JdbcTypeCode(SqlTypes.ARRAY)
    @Column(nullable = false, columnDefinition = "text[]")
    private List<String> aliases = new ArrayList<>();

    @JdbcTypeCode(SqlTypes.ARRAY)
    @Column(nullable = false, columnDefinition = "text[]")
    private List<String> keywords = new ArrayList<>();

    @Column(nullable = false, length = 40)
    private String category;

    @Column(name = "data_source", nullable = false, length = 40)
    private String dataSource;

    @Column(name = "verification_status", nullable = false, length = 40)
    private String verificationStatus;

    @Column(name = "source_id", length = 128)
    private String sourceId;

    @Column(name = "source_updated_at")
    private Instant sourceUpdatedAt;

    @Column(nullable = false, columnDefinition = "geometry(Point,4326)")
    private Point location;

    @Column(nullable = false)
    private boolean enabled;

    @Column(name = "created_at", nullable = false, insertable = false, updatable = false)
    private Instant createdAt;

    @Column(name = "updated_at", nullable = false, insertable = false)
    private Instant updatedAt;

    public Poi() {
    }

    public void updateFromImport(Campus campus, Building building, String externalId, String name,
                                 List<String> aliases, List<String> keywords, String category,
                                 Point location, String dataSource, String verificationStatus,
                                 String sourceId, Instant sourceUpdatedAt, boolean enabled) {
        this.campus = campus;
        this.building = building;
        this.externalId = externalId;
        this.name = name;
        this.aliases = new ArrayList<>(aliases);
        this.keywords = new ArrayList<>(keywords);
        this.category = category;
        this.location = location;
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

    public String getExternalId() {
        return externalId;
    }

    public String getCategory() {
        return category;
    }

    public Point getLocation() {
        return location;
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

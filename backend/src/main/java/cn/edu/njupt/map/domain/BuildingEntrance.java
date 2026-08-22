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
import org.locationtech.jts.geom.Point;

@Entity
@Table(name = "building_entrance")
public class BuildingEntrance {
    @Id @GeneratedValue private UUID id;
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "building_id", nullable = false)
    private Building building;
    @Column(name = "external_id", unique = true, length = 128) private String externalId;
    @Column(nullable = false, length = 128) private String name;
    @Column(nullable = false, columnDefinition = "geometry(Point,4326)") private Point location;
    @Column(name = "walking_access") private Boolean walkingAccess;
    @Column(name = "cycling_access") private Boolean cyclingAccess;
    @Column private Boolean accessible;
    @Column(name = "vehicle_access") private Boolean vehicleAccess;
    @Column(name = "opening_hours", length = 160) private String openingHours;
    @Column(name = "data_source", nullable = false, length = 40) private String dataSource;
    @Column(name = "verification_status", nullable = false, length = 40) private String verificationStatus;
    @Column(name = "source_id", length = 128) private String sourceId;
    @Column(name = "source_updated_at") private Instant sourceUpdatedAt;
    @Column(nullable = false) private boolean enabled;
    @Column(name = "created_at", nullable = false, insertable = false, updatable = false) private Instant createdAt;
    @Column(name = "updated_at", nullable = false, insertable = false) private Instant updatedAt;

    public void updateFromImport(Building building, String externalId, String name, Point location,
                                 Boolean walkingAccess, Boolean cyclingAccess, Boolean accessible,
                                 Boolean vehicleAccess, String openingHours,
                                 String dataSource, String verificationStatus, String sourceId,
                                 Instant sourceUpdatedAt, boolean enabled) {
        this.building = building;
        this.externalId = externalId;
        this.name = name;
        this.location = location;
        this.walkingAccess = walkingAccess;
        this.cyclingAccess = cyclingAccess;
        this.accessible = accessible;
        this.vehicleAccess = vehicleAccess;
        this.openingHours = openingHours;
        this.dataSource = dataSource;
        this.verificationStatus = verificationStatus;
        this.sourceId = sourceId;
        this.sourceUpdatedAt = sourceUpdatedAt;
        this.enabled = enabled;
        this.updatedAt = Instant.now();
    }
}

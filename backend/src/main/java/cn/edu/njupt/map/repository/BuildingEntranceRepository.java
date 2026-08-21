package cn.edu.njupt.map.repository;

import cn.edu.njupt.map.domain.BuildingEntrance;
import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;

public interface BuildingEntranceRepository extends JpaRepository<BuildingEntrance, UUID> {
    Optional<BuildingEntrance> findByExternalId(String externalId);

    long countByBuildingCampusIdAndEnabledTrue(UUID campusId);

    @Modifying
    @Query("update BuildingEntrance item set item.enabled = :enabled where item.dataSource = :dataSource")
    int setEnabledByDataSource(String dataSource, boolean enabled);
}

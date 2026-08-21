package cn.edu.njupt.map.repository;

import cn.edu.njupt.map.domain.Building;
import java.util.Optional;
import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface BuildingRepository extends JpaRepository<Building, UUID> {

    Optional<Building> findByExternalId(String externalId);

    long countByCampusIdAndEnabledTrue(UUID campusId);

    List<Building> findAllByCampusCodeAndEnabledTrueOrderByNameAsc(String campusCode);
}

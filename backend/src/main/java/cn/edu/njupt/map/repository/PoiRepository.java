package cn.edu.njupt.map.repository;

import cn.edu.njupt.map.domain.Poi;
import java.util.Optional;
import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;

public interface PoiRepository extends JpaRepository<Poi, UUID> {

    Optional<Poi> findByExternalId(String externalId);

    long countByCampusIdAndEnabledTrue(UUID campusId);

    List<Poi> findAllByCampusCodeAndEnabledTrueOrderByNameAsc(String campusCode);

    @Modifying
    @Query("update Poi item set item.enabled = :enabled where item.dataSource = :dataSource")
    int setEnabledByDataSource(String dataSource, boolean enabled);
}

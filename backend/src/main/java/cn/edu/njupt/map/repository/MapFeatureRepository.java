package cn.edu.njupt.map.repository;

import cn.edu.njupt.map.domain.MapFeature;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;

public interface MapFeatureRepository extends JpaRepository<MapFeature, UUID> {

    Optional<MapFeature> findByExternalId(String externalId);

    List<MapFeature> findAllByCampusCodeAndEnabledTrueOrderByPriorityDescNameAsc(String campusCode);

    long countByCampusIdAndEnabledTrue(UUID campusId);

    boolean existsByCampusIdAndFeatureTypeInAndEnabledTrue(UUID campusId, List<String> featureTypes);

    @Modifying
    @Query("update MapFeature item set item.enabled = :enabled where item.dataSource = :dataSource")
    int setEnabledByDataSource(String dataSource, boolean enabled);
}

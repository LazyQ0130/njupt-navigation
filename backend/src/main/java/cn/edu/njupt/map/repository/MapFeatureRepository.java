package cn.edu.njupt.map.repository;

import cn.edu.njupt.map.domain.MapFeature;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface MapFeatureRepository extends JpaRepository<MapFeature, UUID> {

    Optional<MapFeature> findByExternalId(String externalId);

    List<MapFeature> findAllByCampusCodeAndEnabledTrueOrderByPriorityDescNameAsc(String campusCode);

    long countByCampusIdAndEnabledTrue(UUID campusId);

    boolean existsByCampusIdAndFeatureTypeInAndEnabledTrue(UUID campusId, List<String> featureTypes);
}

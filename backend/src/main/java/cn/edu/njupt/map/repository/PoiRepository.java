package cn.edu.njupt.map.repository;

import cn.edu.njupt.map.domain.Poi;
import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PoiRepository extends JpaRepository<Poi, UUID> {

    Optional<Poi> findByExternalId(String externalId);

    long countByCampusIdAndEnabledTrue(UUID campusId);
}


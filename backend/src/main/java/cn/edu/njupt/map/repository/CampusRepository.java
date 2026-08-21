package cn.edu.njupt.map.repository;

import cn.edu.njupt.map.domain.Campus;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CampusRepository extends JpaRepository<Campus, UUID> {

    Optional<Campus> findByCodeAndEnabledTrue(String code);

    List<Campus> findAllByEnabledTrueOrderByNameAsc();
}


package fr.gouv.cnsp.monitorfish.infrastructure.database.repositories.interfaces

import fr.gouv.cnsp.monitorfish.infrastructure.database.entities.GearGroupEntity
import org.springframework.data.repository.CrudRepository
import java.time.Instant

interface DBGearRepository : CrudRepository<GearGroupEntity, Long> {
    fun findByCodeEquals(code: Int): GearGroupEntity
}

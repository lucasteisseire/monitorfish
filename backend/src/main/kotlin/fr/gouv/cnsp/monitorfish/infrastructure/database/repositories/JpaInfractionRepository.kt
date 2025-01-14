package fr.gouv.cnsp.monitorfish.infrastructure.database.repositories

import fr.gouv.cnsp.monitorfish.domain.entities.controls.Infraction
import fr.gouv.cnsp.monitorfish.domain.repositories.InfractionRepository
import fr.gouv.cnsp.monitorfish.infrastructure.database.repositories.interfaces.DBInfractionRepository
import org.springframework.cache.annotation.Cacheable
import org.springframework.stereotype.Repository

@Repository
class JpaInfractionRepository(private val dbInfractionRepository: DBInfractionRepository) : InfractionRepository {
    @Cacheable(value = ["infractions"])
    override fun findInfractions(ids: List<Int>): List<Infraction> {
        return dbInfractionRepository.findAllByIdIn(ids).map { it.toInfraction() }
    }
}

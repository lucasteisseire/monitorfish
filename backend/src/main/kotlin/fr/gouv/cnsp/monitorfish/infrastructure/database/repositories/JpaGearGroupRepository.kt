package fr.gouv.cnsp.monitorfish.infrastructure.database.repositories

import fr.gouv.cnsp.monitorfish.domain.entities.GearGroup
import fr.gouv.cnsp.monitorfish.domain.exceptions.CodeNotFoundException
import fr.gouv.cnsp.monitorfish.domain.repositories.GearGroupRepository
import fr.gouv.cnsp.monitorfish.infrastructure.database.repositories.interfaces.DBGearRepository
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.cache.annotation.Cacheable
import org.springframework.dao.EmptyResultDataAccessException
import org.springframework.stereotype.Repository

@Repository
class JpaGearGroupRepository(private val dbGearGroupRepository: DBGearGroupRepository) : GearGroupRepository {

    @Cacheable(value = ["gears"])
    override fun findAll(): List<GearGroup> {
        return dbGearRepository.findAll().map {
            it.toGearGroup()
        }
    }

    @Cacheable(value = ["gear"])
    override fun find(code: String): GearGroup {
        return try {
            dbGearGroupRepository.findByCodeEquals(code).toGearGroup()
        } catch (e: EmptyResultDataAccessException) {
            throw CodeNotFoundException("Gear: code $code not found")
        }
    }
}

package fr.gouv.cnsp.monitorfish.domain.use_cases

import fr.gouv.cnsp.monitorfish.config.UseCase
import fr.gouv.cnsp.monitorfish.domain.entities.Gear
import fr.gouv.cnsp.monitorfish.domain.repositories.GearRepository
import fr.gouv.cnsp.monitorfish.domain.repositories.GearGroupRepository

@UseCase
class GetAllGears(private val gearRepository: GearRepository, private val GearGroupRepository) {
    fun execute(): List<Gear> {
        val allGears = gearRepository.findAll()
        val allGearGroup = GearGroupRepository.findAll()

        return null
    }
}
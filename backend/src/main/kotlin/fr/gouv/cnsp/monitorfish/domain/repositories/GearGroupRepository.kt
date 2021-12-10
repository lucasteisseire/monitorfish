package fr.gouv.cnsp.monitorfish.domain.repositories

import fr.gouv.cnsp.monitorfish.domain.entities.GearGroup
import fr.gouv.cnsp.monitorfish.domain.exceptions.CodeNotFoundException
import kotlin.jvm.Throws

interface GearRepository {
    fun findAll() : List<GearGroup>
    @Throws(CodeNotFoundException::class)
    fun find(code: String): GearGroup
}

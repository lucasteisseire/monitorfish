package fr.gouv.cnsp.monitorfish.domain.repositories

import fr.gouv.cnsp.monitorfish.domain.entities.Vessel

interface VesselRepository {
    fun findVessel(internalReferenceNumber: String): Vessel
}
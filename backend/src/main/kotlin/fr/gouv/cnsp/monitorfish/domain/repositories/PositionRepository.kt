package fr.gouv.cnsp.monitorfish.domain.repositories

import fr.gouv.cnsp.monitorfish.domain.entities.Position

interface PositionRepository {
    fun findAll(): List<Position>
    fun findAllByMMSI(MMSI: String): List<Position>
    fun findAllLastDistinctPositions(): List<Position>
    fun findVesselLastPositions(internalReferenceNumber: String): List<Position>
    fun save(position: Position)
}
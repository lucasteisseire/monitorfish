package fr.gouv.cnsp.monitorfish.domain.repositories

import fr.gouv.cnsp.monitorfish.domain.entities.wrappers.LastDepartureDateAndTripNumber
import fr.gouv.cnsp.monitorfish.domain.entities.ers.ERSMessage
import fr.gouv.cnsp.monitorfish.domain.exceptions.NoERSLastDepartureDateFound
import java.time.ZonedDateTime
import kotlin.jvm.Throws

interface ERSRepository {
    @Throws(NoERSLastDepartureDateFound::class)
    fun findLastDepartureDateAndTripNumber(internalReferenceNumber: String,
                                           externalReferenceNumber: String,
                                           ircs: String): LastDepartureDateAndTripNumber
    fun findAllMessagesAfterDepartureDate(dateTime: ZonedDateTime,
                                          internalReferenceNumber: String,
                                          externalReferenceNumber: String,
                                          ircs: String): List<ERSMessage>
    fun findLANAndPNOMessagesNotAnalyzedBy(ruleType: String): List<Pair<ERSMessage, ERSMessage?>>
    fun updateERSMessagesAsProcessedByRule(ids: List<Long>, ruleType: String)
    fun findById(id: Long): ERSMessage
    // For test purpose
    fun deleteAll()
}
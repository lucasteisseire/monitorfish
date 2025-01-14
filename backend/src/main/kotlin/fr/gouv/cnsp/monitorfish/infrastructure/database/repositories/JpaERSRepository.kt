package fr.gouv.cnsp.monitorfish.infrastructure.database.repositories

import com.fasterxml.jackson.databind.ObjectMapper
import fr.gouv.cnsp.monitorfish.domain.entities.VoyageDatesAndTripNumber
import fr.gouv.cnsp.monitorfish.domain.entities.ers.ERSMessage
import fr.gouv.cnsp.monitorfish.domain.entities.ers.ERSMessageTypeMapping
import fr.gouv.cnsp.monitorfish.domain.entities.ers.ERSOperationType
import fr.gouv.cnsp.monitorfish.domain.exceptions.NoLogbookFishingTripFound
import fr.gouv.cnsp.monitorfish.domain.exceptions.NoERSMessagesFound
import fr.gouv.cnsp.monitorfish.domain.repositories.ERSRepository
import fr.gouv.cnsp.monitorfish.infrastructure.database.entities.ERSEntity
import fr.gouv.cnsp.monitorfish.infrastructure.database.repositories.interfaces.DBERSRepository
import org.springframework.cache.annotation.Cacheable
import org.springframework.dao.EmptyResultDataAccessException
import org.springframework.data.domain.PageRequest
import org.springframework.data.jpa.repository.Modifying
import org.springframework.stereotype.Repository
import java.time.ZoneOffset.UTC
import java.time.ZonedDateTime
import javax.transaction.Transactional

@Repository
class JpaERSRepository(private val dbERSRepository: DBERSRepository,
                       private val mapper: ObjectMapper) : ERSRepository {

    private val postgresChunkSize = 5000

    override fun findLastTripBeforeDateTime(internalReferenceNumber: String, beforeDateTime: ZonedDateTime): VoyageDatesAndTripNumber {
        try {
            if(internalReferenceNumber.isNotEmpty()) {
                val lastTrip = dbERSRepository.findTripsBeforeDatetime(
                        internalReferenceNumber, beforeDateTime.toInstant(), PageRequest.of(0, 1)).first()

                return VoyageDatesAndTripNumber(lastTrip.tripNumber, lastTrip.startDate.atZone(UTC), lastTrip.endDate.atZone(UTC))
            }

            throw IllegalArgumentException("No CFR given to find the vessel.")
        } catch (e: NoSuchElementException) {
            throw NoLogbookFishingTripFound(getTripNotFoundExceptionMessage(internalReferenceNumber), e)
        } catch (e: IllegalArgumentException) {
            throw NoLogbookFishingTripFound(getTripNotFoundExceptionMessage(internalReferenceNumber), e)
        }
    }

    @Cacheable(value = ["previous_ers"])
    override fun findTripBeforeTripNumber(internalReferenceNumber: String, tripNumber: Int): VoyageDatesAndTripNumber {
        try {
            if(internalReferenceNumber.isNotEmpty()) {
                val previousTripNumber = dbERSRepository.findPreviousTripNumber(
                        internalReferenceNumber, tripNumber, PageRequest.of(0, 1)).first().tripNumber
                val previousTrip = dbERSRepository.findFirstAndLastOperationsDatesOfTrip(internalReferenceNumber, previousTripNumber)

                return VoyageDatesAndTripNumber(
                        previousTripNumber,
                        previousTrip.startDate.atZone(UTC),
                        previousTrip.endDate.atZone(UTC))
            }

            throw IllegalArgumentException("No CFR given to find the vessel.")
        } catch (e: NoSuchElementException) {
            throw NoLogbookFishingTripFound(getTripNotFoundExceptionMessage(internalReferenceNumber), e)
        } catch (e: IllegalArgumentException) {
            throw NoLogbookFishingTripFound(getTripNotFoundExceptionMessage(internalReferenceNumber), e)
        } catch (e: EmptyResultDataAccessException) {
            throw NoLogbookFishingTripFound(getTripNotFoundExceptionMessage(internalReferenceNumber), e)
        }
    }

    @Cacheable(value = ["next_ers"])
    override fun findTripAfterTripNumber(internalReferenceNumber: String, tripNumber: Int): VoyageDatesAndTripNumber {
        try {
            if(internalReferenceNumber.isNotEmpty()) {
                val nextTripNumber = dbERSRepository.findNextTripNumber(
                        internalReferenceNumber, tripNumber, PageRequest.of(0, 1)).first().tripNumber
                val nextTrip = dbERSRepository.findFirstAndLastOperationsDatesOfTrip(internalReferenceNumber, nextTripNumber)

                return VoyageDatesAndTripNumber(
                        nextTripNumber,
                        nextTrip.startDate.atZone(UTC),
                        nextTrip.endDate.atZone(UTC))
            }

            throw IllegalArgumentException("No CFR given to find the vessel.")
        } catch (e: NoSuchElementException) {
            throw NoLogbookFishingTripFound(getTripNotFoundExceptionMessage(internalReferenceNumber), e)
        } catch (e: IllegalArgumentException) {
            throw NoLogbookFishingTripFound(getTripNotFoundExceptionMessage(internalReferenceNumber), e)
        } catch (e: EmptyResultDataAccessException) {
            throw NoLogbookFishingTripFound(getTripNotFoundExceptionMessage(internalReferenceNumber), e)
        }
    }

    private fun getTripNotFoundExceptionMessage(internalReferenceNumber: String) =
            "No trip found found for the vessel. (internalReferenceNumber: \"$internalReferenceNumber\")"

    @Cacheable(value = ["ers_messages"])
    override fun findAllMessagesByTripNumberBetweenDates(
        internalReferenceNumber: String,
        afterDate: ZonedDateTime,
        beforeDate: ZonedDateTime,
        tripNumber: Int): List<ERSMessage> {
        try {
            if(internalReferenceNumber.isNotEmpty()) {
                return dbERSRepository.findAllMessagesByTripNumberBetweenDates(
                    internalReferenceNumber,
                    afterDate.toInstant(),
                    beforeDate.toInstant(),
                    tripNumber
                ).map {
                    it.toERSMessage(mapper)
                }
            }

            throw IllegalArgumentException("No CFR given to find the vessel.")
        } catch (e: EmptyResultDataAccessException) {
            throw NoERSMessagesFound(getAllMessagesExceptionMessage(internalReferenceNumber), e)
        } catch (e: IllegalArgumentException) {
            throw NoERSMessagesFound(getAllMessagesExceptionMessage(internalReferenceNumber), e)
        }
    }

    override fun findLANAndPNOMessagesNotAnalyzedBy(ruleType: String): List<Pair<ERSMessage, ERSMessage?>> {
        val lanAndPnoMessages = dbERSRepository.findAllLANAndPNONotProcessedByRule(ruleType)

        val lanAndPnoMessagesWithoutCorrectedMessages = lanAndPnoMessages.filter { lanMessage ->
            getCorrectedMessageIfAvailable(lanMessage, lanAndPnoMessages)
        }

        return lanAndPnoMessagesWithoutCorrectedMessages.filter {
            it.internalReferenceNumber != null &&
                    it.tripNumber != null &&
                    it.messageType == ERSMessageTypeMapping.LAN.name
        }.map { lanMessage ->
            val pnoMessage = lanAndPnoMessagesWithoutCorrectedMessages.singleOrNull { message ->
                message.internalReferenceNumber == lanMessage.internalReferenceNumber &&
                        message.tripNumber == lanMessage.tripNumber &&
                        message.messageType == ERSMessageTypeMapping.PNO.name
            }

            Pair(lanMessage.toERSMessage(mapper), pnoMessage?.toERSMessage(mapper))
        }
    }

    override fun updateERSMessagesAsProcessedByRule(ids: List<Long>, ruleType: String) {
        ids.chunked(postgresChunkSize).forEach {
            dbERSRepository.updateERSMessagesAsProcessedByRule(it, ruleType)
        }
    }

    override fun findById(id: Long): ERSMessage {
        return dbERSRepository.findById(id)
                .get().toERSMessage(mapper)
    }

    @Modifying
    @Transactional
    override fun deleteAll() {
        dbERSRepository.deleteAll()
    }

    override fun findLastMessageDate(): ZonedDateTime {
        return dbERSRepository.findLastOperationDateTime().atZone(UTC)
    }

    private fun getCorrectedMessageIfAvailable(pnoMessage: ERSEntity, messages: List<ERSEntity>): Boolean {
        return if (pnoMessage.operationType == ERSOperationType.DAT) {
            !messages.any { it.operationType == ERSOperationType.COR && it.referencedErsId == pnoMessage.ersId }
        } else {
            true
        }
    }

    private fun getAllMessagesExceptionMessage(internalReferenceNumber: String) =
            "No messages found for the vessel. (internalReferenceNumber: \"$internalReferenceNumber\")"
}

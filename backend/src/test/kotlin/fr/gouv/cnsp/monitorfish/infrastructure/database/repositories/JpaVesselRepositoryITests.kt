package fr.gouv.cnsp.monitorfish.infrastructure.database.repositories

import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.runner.RunWith
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.cache.CacheManager
import org.springframework.test.context.junit4.SpringRunner
import org.springframework.transaction.annotation.Transactional

@RunWith(SpringRunner::class)
class JpaVesselRepositoryITests : AbstractDBTests() {

    @Autowired
    private lateinit var jpaVesselRepository: JpaVesselRepository

    @Autowired
    lateinit var cacheManager: CacheManager

    @BeforeEach
    fun setup() {
        cacheManager.getCache("vessel")?.clear()
    }

    @Test
    @Transactional
    fun `findVessel Should return an empty Vessel object When no vessel is found`() {
        // When
        val vessel = jpaVesselRepository.findVessel("DUMMY")

        assertThat(vessel.internalReferenceNumber).isNull()
        assertThat(vessel.externalReferenceNumber).isNull()
        assertThat(vessel.MMSI).isNull()
        assertThat(vessel.IRCS).isNull()
    }

    @Test
    @Transactional
    fun `findVessel Should return a vessel`() {
        // When
        val vessel = jpaVesselRepository.findVessel("FR209143000")

        assertThat(vessel.internalReferenceNumber).isEqualTo("FR209143000")
    }
}
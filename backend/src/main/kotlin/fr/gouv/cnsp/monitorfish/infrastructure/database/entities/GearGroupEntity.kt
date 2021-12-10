package fr.gouv.cnsp.monitorfish.infrastructure.database.entities

import fr.gouv.cnsp.monitorfish.domain.entities.Gear
import javax.persistence.*

@Entity
@Table(name = "fishing_gear_codes")
data class GearEntity(
        @Id
        @Column(name = "id")
        val group: String,
        @Column(name = "fishing_gear_group") {

        fun toGearGroup() = Gear(
            Id = code,
            group = group,
    )
}

package fr.gouv.cnsp.monitorfish.infrastructure.database.entities

import fr.gouv.cnsp.monitorfish.domain.entities.SpeciesGroup
import javax.persistence.Column
import javax.persistence.Entity
import javax.persistence.Id
import javax.persistence.Table

@Entity
@Table(name = "species_groups")
data class SpeciesGroupEntity(
        @Id
        @Column(name = "id")
        val id: Int? = null,
        @Column(name = "species_group")
        val group: String,
        @Column(name = "comment")
        val comment: String) {

        fun toSpeciesGroup() = SpeciesGroup(
            group = group,
            comment = comment
    )
}

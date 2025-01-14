import React, { useEffect } from 'react'
import { COLORS } from '../../../../constants/constants'
import styled from 'styled-components'
import { ReactComponent as ShowFishingActivitiesSVG } from '../../../icons/Bouton_afficher_messages_JPE_sur_piste.svg'
import { MapButtonStyle } from '../../../commonStyles/MapButton.style'
import { useDispatch, useSelector } from 'react-redux'
import { hideFishingActivitiesOnMap, showFishingActivitiesOnMap } from '../../../../domain/shared_slices/FishingActivities'

const ShowFishingActivitiesOnMap = ({ openBox, rightMenuIsOpen }) => {
  const dispatch = useDispatch()
  const { healthcheckTextWarning } = useSelector(state => state.global)
  const {
    /** @type {FishingActivityShowedOnMap[]} fishingActivitiesShowedOnMap */
    fishingActivitiesShowedOnMap,
    fishingActivitiesAreShowedOnMap
  } = useSelector(state => state.fishingActivities)

  useEffect(() => {
    if (!openBox) {
      dispatch(hideFishingActivitiesOnMap())
    }
  }, [openBox])

  return (
    <ShowFishingActivitiesOnMapButton
      title={`${fishingActivitiesAreShowedOnMap || fishingActivitiesShowedOnMap?.length ? 'Cacher' : 'Afficher'} les messages du JPE sur la piste`}
      data-cy={'show-all-fishing-activities-on-map'}
      healthcheckTextWarning={healthcheckTextWarning}
      fishingActivitiesShowedOnMap={fishingActivitiesAreShowedOnMap || fishingActivitiesShowedOnMap?.length}
      openBox={openBox}
      rightMenuIsOpen={rightMenuIsOpen}
      onClick={() => fishingActivitiesAreShowedOnMap || fishingActivitiesShowedOnMap?.length
        ? dispatch(hideFishingActivitiesOnMap())
        : dispatch(showFishingActivitiesOnMap())
      }
    >
      <ShowFishingActivities />
    </ShowFishingActivitiesOnMapButton>
  )
}

const ShowFishingActivitiesOnMapButton = styled(MapButtonStyle)`
  top: 223px;
  height: 30px;
  width: 30px;
  background: ${props => props.fishingActivitiesShowedOnMap ? COLORS.shadowBlue : COLORS.charcoal};
  position: absolute;
  right: 10px;
  margin-right: ${props => props.openBox ? 505 : -45}px;
  opacity: ${props => props.openBox ? 1 : 0};
  ${props => props.isClickable ? 'cursor: pointer;' : null}
  border-radius: 1px;
  z-index: 999;
  transition: 0.5s all;
  
  animation: ${props => props.rightMenuIsOpen && props.openBox
  ? 'vessel-box-opening-with-right-menu-hover'
  : 'vessel-box-closing-with-right-menu-hover'} 0.3s ease forwards;

  :hover, :focus {
      background: ${props => props.fishingActivitiesShowedOnMap ? COLORS.shadowBlue : COLORS.charcoal};
  }
`

const ShowFishingActivities = styled(ShowFishingActivitiesSVG)`
  width: 30px;
`

export default ShowFishingActivitiesOnMap

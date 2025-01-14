import { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'
import VectorSource from 'ol/source/Vector'
import Layers from '../domain/entities/layers'
import { EstimatedPosition } from '../domain/entities/estimatedPosition'
import { getVesselLastPositionVisibilityDates, Vessel } from '../domain/entities/vessel'
import { Vector } from 'ol/layer'
import { getEstimatedPositionStyle } from './styles/vesselEstimatedPosition.style'
import { VESSELS_UPDATE_EVENT } from './VesselsLayer'
import { unByKey } from 'ol/Observable'

const NOT_FOUND = -1
export const OPACITY = 'opacity'

const VesselEstimatedPositionLayer = ({ map }) => {
  const {
    vesselsLayerSource,
    filteredVesselsFeaturesUids,
    previewFilteredVesselsFeaturesUids,
    hideOtherVessels
  } = useSelector(state => state.vessel)

  const {
    nonFilteredVesselsAreHidden,
    filters
  } = useSelector(state => state.filter)

  const {
    selectedBaseLayer,
    showingVesselsEstimatedPositions,
    vesselsLastPositionVisibility,
    hideVesselsAtPort
  } = useSelector(state => state.map)

  const [vectorSource] = useState(new VectorSource({
    features: []
  }))

  const [layer] = useState(new Vector({
    renderBuffer: 4,
    source: vectorSource,
    zIndex: Layers.VESSEL_ESTIMATED_POSITION.zIndex,
    updateWhileAnimating: true,
    updateWhileInteracting: true,
    style: feature => getEstimatedPositionStyle(feature)
  }))

  useEffect(() => {
    addLayerToMap()
  }, [map])

  useEffect(() => {
    let eventKey
    if (vesselsLayerSource && !showingVesselsEstimatedPositions) {
      vectorSource.clear(true)
    }

    if (vesselsLayerSource && showingVesselsEstimatedPositions) {
      showVesselEstimatedTrack()
    }

    if (vesselsLayerSource) {
      eventKey = vesselsLayerSource.once(VESSELS_UPDATE_EVENT, ({ showingVesselsEstimatedPositions }) => {
        if (showingVesselsEstimatedPositions) {
          showVesselEstimatedTrack()
        }
      })
    }

    return () => {
      if (eventKey) {
        unByKey(eventKey)
      }
    }
  }, [
    vesselsLayerSource,
    selectedBaseLayer,
    showingVesselsEstimatedPositions,
    filteredVesselsFeaturesUids,
    previewFilteredVesselsFeaturesUids,
    nonFilteredVesselsAreHidden,
    hideOtherVessels,
    hideVesselsAtPort
  ])

  useEffect(() => {
    const { vesselIsHidden, vesselIsOpacityReduced } = getVesselLastPositionVisibilityDates(vesselsLastPositionVisibility)

    vectorSource.forEachFeature(feature => {
      const opacity = Vessel.getVesselOpacity(feature.estimatedPosition.dateTime, vesselIsHidden, vesselIsOpacityReduced)
      feature.set(EstimatedPosition.opacityProperty, opacity)
    })
  }, [vesselsLastPositionVisibility])

  useEffect(() => {
    vectorSource.forEachFeature(feature => {
      feature.set(EstimatedPosition.isHiddenProperty, hideOtherVessels)
    })
  }, [hideOtherVessels])

  function addLayerToMap () {
    if (map) {
      layer.name = Layers.VESSEL_ESTIMATED_POSITION.code
      map.getLayers().push(layer)
    }

    return () => {
      if (map) {
        map.removeLayer(layer)
      }
    }
  }

  function showVesselEstimatedTrack () {
    vectorSource.clear(true)
    const isLight = Vessel.iconIsLight(selectedBaseLayer)
    const { vesselIsHidden, vesselIsOpacityReduced } = getVesselLastPositionVisibilityDates(vesselsLastPositionVisibility)
    const showedFilter = filters?.find(filter => filter.showed)

    if (showedFilter && nonFilteredVesselsAreHidden && !filteredVesselsFeaturesUids?.length) {
      return
    }

    const estimatedCurrentPositionsFeatures = []
    vesselsLayerSource.forEachFeature(vesselFeature => {
      const {
        estimatedCurrentLatitude,
        estimatedCurrentLongitude,
        latitude,
        longitude,
        dateTime,
        isAtPort
      } = vesselFeature.vessel

      if (nonFilteredVesselsAreHidden &&
        filteredVesselsFeaturesUids?.length > 0) {
        const featureIndex = filteredVesselsFeaturesUids.indexOf(vesselFeature.ol_uid)

        if (featureIndex === NOT_FOUND) {
          return
        }
      }

      if (previewFilteredVesselsFeaturesUids?.length) {
        const featureIndex = previewFilteredVesselsFeaturesUids.indexOf(vesselFeature.ol_uid)

        if (featureIndex === NOT_FOUND) {
          return
        }
      }

      if (hideVesselsAtPort && isAtPort) {
        return
      }

      if (estimatedCurrentLatitude && estimatedCurrentLongitude && latitude && longitude) {
        estimatedCurrentPositionsFeatures.push(EstimatedPosition.getFeatures(
          [longitude, latitude],
          [estimatedCurrentLongitude, estimatedCurrentLatitude],
          {
            id: vesselFeature.getId().replace(`${Layers.VESSELS.code}:`, ''),
            isLight,
            dateTime,
            vesselIsHidden,
            vesselIsOpacityReduced,
            hideOtherVessels
          }))
      }
    })

    vectorSource.addFeatures(estimatedCurrentPositionsFeatures.flat())
  }

  return null
}

export default VesselEstimatedPositionLayer

import React, { useEffect, useRef, useState } from 'react'
import { useSelector } from 'react-redux'
import VectorSource from 'ol/source/Vector'
import Layers from '../domain/entities/layers'
import { getVesselFeatureIdFromVessel, getVesselLastPositionVisibilityDates, Vessel } from '../domain/entities/vessel'
import { Vector } from 'ol/layer'
import VesselLabelOverlay from '../features/map/overlays/VesselLabelOverlay'
import LineString from 'ol/geom/LineString'
import { usePrevious } from '../hooks/usePrevious'
import { VesselLabelLine } from '../domain/entities/vesselLabelLine'
import { getLabelLineStyle } from './styles/vesselLabelLine.style'

const MAX_LABELS_DISPLAYED = 200
const MAX_LABELS_DISPLAYED_IN_PREVIEW = 400
const NOT_FOUND = -1

const VesselsLabelsLayer = ({ map, mapMovingAndZoomEvent }) => {
  const throttleDuration = 500 // ms

  const {
    filteredVesselsFeaturesUids,
    previewFilteredVesselsFeaturesUids,
    vesselsLayerSource,
    hideOtherVessels,
    selectedVessel,
    vesselsTracksShowed
  } = useSelector(state => state.vessel)

  const {
    previewFilteredVesselsMode
  } = useSelector(state => state.global)

  const {
    vesselLabelsShowedOnMap,
    riskFactorShowedOnMap,
    vesselsLastPositionVisibility,
    vesselLabel,
    hideVesselsAtPort
  } = useSelector(state => state.map)

  const {
    /** @type {VesselFilter[]} filters */
    filters,
    nonFilteredVesselsAreHidden
  } = useSelector(state => state.filter)

  const [featuresAndLabels, setFeaturesAndLabels] = useState([])
  const previousMapZoom = useRef('')
  const previousFeaturesAndLabels = usePrevious(featuresAndLabels)
  const [vesselToCoordinates, setVesselToCoordinates] = useState(new Map())
  const [vesselToRiskFactorDetailsShowed, setVesselToRiskFactorDetailsShowed] = useState(new Map())
  const isThrottled = useRef(false)

  const [vectorSource] = useState(new VectorSource({
    features: []
  }))
  const [layer] = useState(new Vector({
    renderBuffer: 7,
    source: vectorSource,
    zIndex: Layers.VESSELS_LABEL.zIndex,
    updateWhileAnimating: true,
    updateWhileInteracting: true,
    style: feature => getLabelLineStyle(feature)
  }))

  useEffect(() => {
    addLayerToMap()
  }, [map])

  useEffect(() => {
    if (previousFeaturesAndLabels && featuresAndLabels) {
      const previousFeatureIdsList = previousFeaturesAndLabels.map(({ identity }) => VesselLabelLine.getFeatureId(identity))
      const featureIdsList = featuresAndLabels.map(({ identity }) => VesselLabelLine.getFeatureId(identity))

      previousFeatureIdsList.forEach(id => {
        if (featureIdsList.indexOf(id) === NOT_FOUND) {
          const feature = vectorSource.getFeatureById(id)
          if (feature) {
            vectorSource.removeFeature(feature)
          }
        }
      })
    }
  }, [featuresAndLabels])

  function addLayerToMap () {
    if (map) {
      layer.name = Layers.VESSELS_LABEL.code
      map.getLayers().push(layer)
    }

    return () => {
      if (map) {
        map.removeLayer(layer)
      }
    }
  }

  useEffect(() => {
    if (!riskFactorShowedOnMap) {
      setVesselToRiskFactorDetailsShowed(new Map())
    }
  }, [riskFactorShowedOnMap])

  useEffect(() => {
    if (isThrottled.current || !vesselsLayerSource) {
      return
    }

    isThrottled.current = true
    setTimeout(() => {
      addVesselLabelToAllFeaturesInExtent()
      isThrottled.current = false
    }, throttleDuration)
  }, [
    vesselsLayerSource,
    mapMovingAndZoomEvent,
    filters,
    nonFilteredVesselsAreHidden,
    vesselLabelsShowedOnMap,
    riskFactorShowedOnMap,
    vesselLabel,
    filteredVesselsFeaturesUids,
    previewFilteredVesselsFeaturesUids,
    vesselsLastPositionVisibility,
    hideOtherVessels,
    vesselsTracksShowed,
    hideVesselsAtPort
  ])

  useEffect(() => {
    if (vesselsLayerSource) {
      const { vesselIsHidden, vesselIsOpacityReduced } = getVesselLastPositionVisibilityDates(vesselsLastPositionVisibility)

      vesselsLayerSource.forEachFeatureInExtent(map.getView().calculateExtent(), vesselFeature => {
        const opacity = Vessel.getVesselOpacity(vesselFeature.vessel.dateTime, vesselIsHidden, vesselIsOpacityReduced)
        const labelLineFeatureId = VesselLabelLine.getFeatureId(vesselFeature.vessel)

        const feature = vectorSource.getFeatureById(labelLineFeatureId)
        if (feature) {
          feature.set(VesselLabelLine.opacityProperty, opacity)
        }
      })
    }
  }, [vesselsLayerSource, vesselsLastPositionVisibility])

  useEffect(() => {
    const currentZoom = map.getView().getZoom().toFixed(2)
    if (currentZoom !== previousMapZoom.current) {
      previousMapZoom.current = currentZoom
    }
  }, [mapMovingAndZoomEvent])

  function moveVesselLabelLine (featureId, coordinates, nextCoordinates, offset) {
    if (vesselToCoordinates.has(featureId)) {
      const existingLabelLineFeature = vectorSource.getFeatureById(featureId)
      if (existingLabelLineFeature) {
        existingLabelLineFeature.setGeometry(new LineString([coordinates, nextCoordinates]))
      }
    } else {
      const labelLineFeature = VesselLabelLine.getFeature(
        coordinates,
        nextCoordinates,
        featureId)

      vectorSource.addFeature(labelLineFeature)
    }

    const nextVesselToCoordinates = vesselToCoordinates
    nextVesselToCoordinates.set(featureId, { coordinates: nextCoordinates, offset })
    setVesselToCoordinates(nextVesselToCoordinates)
  }

  function showOnlySelectedVesselsLabel () {
    const extent = vesselsLayerSource.getFeaturesInExtent(map.getView().calculateExtent())

    const selectedVesselFeature = extent
      .find(feature => selectedVessel && feature.getId() === Vessel.getVesselId(selectedVessel))

    const showedFeaturesIdentities = Object.keys(vesselsTracksShowed)
    const showedTracksFeatures = extent
      .filter(feature => showedFeaturesIdentities.find(identity => feature?.getId()?.toString()?.includes(identity)))

    const showedFeaturesLabels = showedTracksFeatures.concat(selectedVesselFeature)
    addLabelToFeatures(showedFeaturesLabels.filter(feature => feature))
  }

  function addVesselLabelToAllFeaturesInExtent () {
    if (!vesselLabelsShowedOnMap && !riskFactorShowedOnMap) {
      setFeaturesAndLabels([])
      vectorSource.clear()
      return
    }

    if (hideOtherVessels) {
      showOnlySelectedVesselsLabel()
      return
    }

    const features = vesselsLayerSource.getFeaturesInExtent(map.getView().calculateExtent())
    const filterShowed = filters.find(filter => filter.showed)

    const isFiltered = filterShowed && nonFilteredVesselsAreHidden && filteredVesselsFeaturesUids?.length
    const isPreviewed = previewFilteredVesselsFeaturesUids?.length

    if (isFiltered || isPreviewed) {
      addLabelToFilteredFeatures(features)
    } else if (features.length < MAX_LABELS_DISPLAYED) {
      addLabelToFeatures(features)
    } else {
      setFeaturesAndLabels([])
      vectorSource.clear()
    }
  }

  function addLabelToFilteredFeatures (features) {
    let filteredFeatures
    if (previewFilteredVesselsFeaturesUids?.length) {
      filteredFeatures = features.filter(feature => {
        return isIncludedInFilterList(feature, previewFilteredVesselsFeaturesUids)
      })
    } else {
      filteredFeatures = features.filter(feature => {
        return isIncludedInFilterList(feature, filteredVesselsFeaturesUids)
      })
    }

    const maxLabelsDisplayed = previewFilteredVesselsMode
      ? MAX_LABELS_DISPLAYED_IN_PREVIEW
      : MAX_LABELS_DISPLAYED

    if (filteredFeatures.length < maxLabelsDisplayed) {
      addLabelToFeatures(filteredFeatures)
    } else {
      setFeaturesAndLabels([])
      vectorSource.clear()
    }
  }

  function isIncludedInFilterList (feature, arrayOfUids) {
    return arrayOfUids?.length && arrayOfUids.indexOf(feature.ol_uid) !== NOT_FOUND
  }

  function drawMovedLabelIfFoundAndReturnOffset (labelLineFeatureId, feature) {
    let offset = null

    if (vesselToCoordinates.has(labelLineFeatureId)) {
      const coordinatesAndOffset = vesselToCoordinates.get(labelLineFeatureId)
      offset = coordinatesAndOffset.offset

      const existingLabelLineFeature = vectorSource.getFeatureById(labelLineFeatureId)
      if (existingLabelLineFeature) {
        existingLabelLineFeature.getGeometry().setCoordinates([feature.getGeometry().getCoordinates(), coordinatesAndOffset.coordinates])
      } else {
        const labelLineFeature = VesselLabelLine.getFeature(
          feature.getGeometry().getCoordinates(),
          coordinatesAndOffset.coordinates,
          labelLineFeatureId)

        vectorSource.addFeature(labelLineFeature)
      }
    }

    return offset
  }

  function addLabelToFeatures (features) {
    const { vesselIsHidden, vesselIsOpacityReduced } = getVesselLastPositionVisibilityDates(vesselsLastPositionVisibility)
    const showedTracksVesselsIdentities = Object.keys(vesselsTracksShowed)

    const nextFeaturesAndLabels = features
      .filter(feature => feature.vessel)
      .map(feature => {
        const label = Vessel.getVesselFeatureLabel(feature, {
          vesselLabel,
          vesselsLastPositionVisibility,
          riskFactorShowedOnMap,
          vesselLabelsShowedOnMap,
          hideVesselsAtPort
        })
        const identity = feature.vessel
        const labelLineFeatureId = VesselLabelLine.getFeatureId(identity)
        const offset = drawMovedLabelIfFoundAndReturnOffset(labelLineFeatureId, feature)
        const trackIsShown = showedTracksVesselsIdentities.includes(getVesselFeatureIdFromVessel(identity))

        return {
          identity: {
            key: feature.ol_uid,
            flagState: feature.vessel.flagState,
            coordinates: feature.getGeometry().getCoordinates(),
            internalReferenceNumber: feature.vessel.internalReferenceNumber,
            ircs: feature.vessel.ircs,
            externalReferenceNumber: feature.vessel.externalReferenceNumber
          },
          trackIsShown: trackIsShown,
          opacity: Vessel.getVesselOpacity(feature.vessel.dateTime, vesselIsHidden, vesselIsOpacityReduced),
          label,
          offset,
          featureId: labelLineFeatureId
        }
      }).filter(object => object)

    setFeaturesAndLabels(nextFeaturesAndLabels)
  }

  function triggerShowRiskDetails (featureId) {
    const previousValue = vesselToRiskFactorDetailsShowed.get(featureId)

    const nextVesselToRiskFactorDetailsShowed = vesselToRiskFactorDetailsShowed
    nextVesselToRiskFactorDetailsShowed.set(featureId, !previousValue)

    setVesselToRiskFactorDetailsShowed(nextVesselToRiskFactorDetailsShowed)
  }

  return (<>
    {
      featuresAndLabels.map(({ identity, label, offset, featureId, opacity, trackIsShown }) => {
        return <VesselLabelOverlay
          map={map}
          key={identity.key}
          featureId={featureId}
          triggerShowRiskDetails={triggerShowRiskDetails}
          moveLine={moveVesselLabelLine}
          text={label?.labelText}
          riskFactor={label?.riskFactor}
          riskFactorDetailsShowed={vesselToRiskFactorDetailsShowed.get(featureId)}
          underCharter={label?.underCharter}
          flagState={identity.flagState}
          offset={offset}
          coordinates={identity.coordinates}
          zoomHasChanged={previousMapZoom.current}
          opacity={opacity}
          trackIsShown={trackIsShown}
          previewFilteredVesselsMode={previewFilteredVesselsMode}
        />
      })
    }
    <div />
  </>)
}

export default VesselsLabelsLayer

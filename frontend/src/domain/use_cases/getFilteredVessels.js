import * as Comlink from 'comlink'
/* eslint-disable import/no-webpack-loader-syntax */
import Worker from 'worker-loader!../../workers/MapperWorker'
import VectorSource from 'ol/source/Vector'
import GeoJSON from 'ol/format/GeoJSON'
import { OPENLAYERS_PROJECTION, WSG84_PROJECTION } from '../entities/map'
import { all } from 'ol/loadingstrategy'

const worker = new Worker()
const MapperWorker = Comlink.wrap(worker)

const vectorSource = new VectorSource({
  format: new GeoJSON({
    dataProjection: WSG84_PROJECTION,
    featureProjection: OPENLAYERS_PROJECTION
  }),
  strategy: all
})

const getFilteredVessels = (vessels, filters) => async () => {
  const worker = await new MapperWorker()

  const workerFilters = getFiltersWithoutZonesSelected(filters)

  return worker.getFilteredVessels(vessels, workerFilters).then(filteredVessels => {
    if (filters.zonesSelected && filters.zonesSelected.length) {
      filteredVessels = filterByZones(filteredVessels, filters.zonesSelected)
    }

    return filteredVessels
  })
}

function getFiltersWithoutZonesSelected (filters) {
  const workerFilters = { ...filters }
  workerFilters.zonesSelected = null
  return workerFilters
}

function filterByZones (filteredVessels, zonesSelected) {
  const featuresGeometries = zonesSelected
    .map(zone => zone.feature)
    .map(feature => vectorSource.getFormat().readFeatures(feature))

  if (featuresGeometries && featuresGeometries.length) {
    const flattenFeaturesGeometries = featuresGeometries
      .flat()
      .map(feature => feature.getGeometry())

    filteredVessels = filteredVessels
      .filter(vessel => {
        return flattenFeaturesGeometries.some(featureGeometry => featureGeometry.intersectsCoordinate(vessel.olCoordinates))
      })
      .filter((zone, index, acc) => {
        return acc.findIndex(existingZone => (existingZone.id === zone.id)) === index
      })
  }

  return filteredVessels
}

export default getFilteredVessels
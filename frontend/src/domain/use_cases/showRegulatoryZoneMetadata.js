import { getRegulatoryFeatureMetadataFromAPI } from '../../api/fetch'
import {
  closeRegulatoryZoneMetadataPanel,
  resetLoadingRegulatoryZoneMetadata,
  setLoadingRegulatoryZoneMetadata,
  setRegulatoryZoneMetadata
} from '../shared_slices/Regulatory'
import { mapToRegulatoryZone } from '../entities/regulatory'
import { setError } from '../shared_slices/Global'
import { batch } from 'react-redux'

const showRegulatoryZoneMetadata = regulatoryZone => (dispatch, getState) => {
  if (regulatoryZone) {
    dispatch(setLoadingRegulatoryZoneMetadata())
    getRegulatoryFeatureMetadataFromAPI(regulatoryZone, getState().global.inBackofficeMode).then(feature => {
      const regulatoryZone = mapToRegulatoryZone(feature)
      dispatch(setRegulatoryZoneMetadata(regulatoryZone))
    }).catch(error => {
      console.error(error)
      batch(() => {
        dispatch(closeRegulatoryZoneMetadataPanel())
        dispatch(setError(error))
        dispatch(resetLoadingRegulatoryZoneMetadata())
      })
    })
  }
}

export default showRegulatoryZoneMetadata

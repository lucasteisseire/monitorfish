import React, { useEffect, useRef, useState } from 'react'
import styled from 'styled-components'

import RegulatoryLayerSearchInput from './RegulatoryLayerSearchInput'
import RegulatoryLayerSearchResultList from './RegulatoryLayerSearchResultList'
import { resetRegulatoryZonesChecked, setRegulatoryLayersSearchResult } from './RegulatoryLayerSearch.slice'
import { COLORS } from '../../../../constants/constants'
import { batch, useDispatch, useSelector } from 'react-redux'
import layer from '../../../../domain/shared_slices/Layer'
import { useEscapeFromKeyboard } from '../../../../hooks/useEscapeFromKeyboard'
import { addRegulatoryZonesToMyLayers } from '../../../../domain/shared_slices/Regulatory'

const RegulatoryLayerSearch = props => {
  const {
    namespace,
    numberOfRegulatoryLayersSaved,
    setNumberOfRegulatoryLayersSaved,
    layersSidebarIsOpen
  } = props

  const dispatch = useDispatch()
  const { setLayersSideBarOpenedZone } = layer[namespace].actions
  const { layersSidebarOpenedLayer } = useSelector(state => state.layer)
  const {
    regulatoryLayersSearchResult,
    regulatoryZonesChecked
  } = useSelector(state => state.regulatoryLayerSearch)

  const [initSearchFields, setInitSearchFields] = useState(false)

  const escape = useEscapeFromKeyboard()

  const wrapperRef = useRef(null)

  useEffect(() => {
    if (layersSidebarOpenedLayer !== '') {
      batch(() => {
        dispatch(setRegulatoryLayersSearchResult(null))
        dispatch(resetRegulatoryZonesChecked())
      })
    }
  }, [layersSidebarOpenedLayer])

  useEffect(() => {
    if (escape) {
      batch(() => {
        dispatch(setRegulatoryLayersSearchResult(null))
        dispatch(resetRegulatoryZonesChecked())
      })
    }
  }, [escape])

  useEffect(() => {
    if (regulatoryLayersSearchResult && Object.keys(regulatoryLayersSearchResult).length > 0) {
      dispatch(setLayersSideBarOpenedZone(''))
    }
  }, [regulatoryLayersSearchResult])

  function saveRegulatoryLayers (regulatoryZonesChecked) {
    setNumberOfRegulatoryLayersSaved(regulatoryZonesChecked.length)
    setTimeout(() => { setNumberOfRegulatoryLayersSaved(0) }, 2000)
    dispatch(addRegulatoryZonesToMyLayers(regulatoryZonesChecked))
    dispatch(resetRegulatoryZonesChecked())
  }

  return (
    <Search ref={wrapperRef}>
      <RegulatoryLayerSearchInput
        initSearchFields={initSearchFields}
        setInitSearchFields={setInitSearchFields}
        layersSidebarIsOpen={layersSidebarIsOpen}
      />
      <RegulatoryLayerSearchResultList/>
      <AddRegulatoryLayer
        data-cy={'regulatory-search-add-zones-button'}
        onClick={() => saveRegulatoryLayers(regulatoryZonesChecked)}
        isShown={regulatoryZonesChecked && regulatoryZonesChecked.length}
      >
        {
          numberOfRegulatoryLayersSaved
            ? `${numberOfRegulatoryLayersSaved} zones ajoutées`
            : `Ajouter ${regulatoryZonesChecked.length} zone${regulatoryZonesChecked.length > 1 ? 's' : ''}`
        }
      </AddRegulatoryLayer>
    </Search>
  )
}

const Search = styled.div`
  width: 350px;
`

const AddRegulatoryLayer = styled.div`
  cursor: pointer;
  border-radius: 0;
  font-size: 13px;
  background: ${COLORS.charcoal};
  color: ${COLORS.gray};
  padding: 0;
  line-height: 2.5em;
  margin: 0;
  height: 0;
  width: 100%;
  overflow: hidden;
  user-select: none;
  height: ${props => props.isShown ? '36' : '0'}px;
  max-height: 600px;
  transition: 0.5s all;
`

export default RegulatoryLayerSearch

import React, { useEffect, useState } from 'react'
import styled from 'styled-components'
import { COLORS } from '../../../../constants/constants'
import SearchIconSVG from '../../../icons/Loupe_dark.svg'
import { REGULATORY_SEARCH_PROPERTIES } from '../../../../domain/entities/regulatory'
import searchRegulatoryLayers from '../../../../domain/use_cases/searchRegulatoryLayers'
import { batch, useDispatch, useSelector } from 'react-redux'
import {
  resetRegulatoryZonesChecked,
  setAdvancedSearchIsOpen,
  setRegulatoryLayersSearchResult
} from './RegulatoryLayerSearch.slice'

const MINIMUM_SEARCH_CHARACTERS_NUMBER = 2

const RegulatoryLayerSearchInput = props => {
  const {
    initSearchFields,
    setInitSearchFields
  } = props
  const dispatch = useDispatch()
  const {
    regulatoryLayers
  } = useSelector(state => state.regulatory)
  const {
    advancedSearchIsOpen
  } = useSelector(state => state.regulatoryLayerSearch)

  const [nameSearchText, setNameSearchText] = useState('')
  const [placeSearchText, setPlaceSearchText] = useState('')
  const [gearSearchText, setGearSearchText] = useState('')
  const [speciesSearchText, setSpeciesSearchText] = useState('')
  const [regulatoryReferencesSearchText, setRegulatoryReferenceSearchText] = useState('')

  useEffect(() => {
    if (initSearchFields) {
      setNameSearchText('')
      setPlaceSearchText('')
      setGearSearchText('')
      setSpeciesSearchText('')
      setRegulatoryReferenceSearchText('')
      setInitSearchFields(false)
    }
  }, [initSearchFields])

  useEffect(() => {
    if (!advancedSearchIsOpen) {
      setPlaceSearchText('')
      setGearSearchText('')
      setSpeciesSearchText('')
      setRegulatoryReferenceSearchText('')
    }
  }, [advancedSearchIsOpen])

  const searchFields = {
    nameSearchText: {
      searchText: nameSearchText,
      properties: [REGULATORY_SEARCH_PROPERTIES.TOPIC, REGULATORY_SEARCH_PROPERTIES.ZONE]
    },
    placeSearchText: {
      searchText: placeSearchText,
      properties: [REGULATORY_SEARCH_PROPERTIES.REGION, REGULATORY_SEARCH_PROPERTIES.SEAFRONT]
    },
    gearSearchText: {
      searchText: gearSearchText,
      properties: [REGULATORY_SEARCH_PROPERTIES.GEARS]
    },
    speciesSearchText: {
      searchText: speciesSearchText,
      properties: [REGULATORY_SEARCH_PROPERTIES.SPECIES]
    },
    regulatoryReferencesSearchText: {
      searchText: regulatoryReferencesSearchText,
      properties: [REGULATORY_SEARCH_PROPERTIES.REGULATORY_REFERENCES]
    }
  }

  useEffect(() => {
    if (nameSearchText.length < MINIMUM_SEARCH_CHARACTERS_NUMBER &&
      placeSearchText.length < MINIMUM_SEARCH_CHARACTERS_NUMBER &&
      gearSearchText.length < MINIMUM_SEARCH_CHARACTERS_NUMBER &&
      regulatoryReferencesSearchText.length < MINIMUM_SEARCH_CHARACTERS_NUMBER &&
      speciesSearchText.length < MINIMUM_SEARCH_CHARACTERS_NUMBER) {
      batch(() => {
        dispatch(setRegulatoryLayersSearchResult({}))
        dispatch(resetRegulatoryZonesChecked())
      })
      return
    }

    batch(() => {
      dispatch(resetRegulatoryZonesChecked())
      dispatch(searchRegulatoryLayers(searchFields, regulatoryLayers)).then(foundRegulatoryLayers => {
        dispatch(setRegulatoryLayersSearchResult(foundRegulatoryLayers))
      })
    })
  }, [nameSearchText, placeSearchText, speciesSearchText, gearSearchText, regulatoryReferencesSearchText])

  return (
    <>
      <PrincipalSearchInput>
        <SearchBoxInput
          data-cy={'regulatory-search-input'}
          placeholder={'Rechercher une zone reg. par son nom'}
          type="text"
          value={nameSearchText}
          onChange={e => setNameSearchText(e.target.value)}/>
        <AdvancedSearch
          data-cy={'regulatory-layers-advanced-search'}
          onClick={() => dispatch(setAdvancedSearchIsOpen(!advancedSearchIsOpen))}
          advancedSearchIsOpen={advancedSearchIsOpen}
        >
          {
            advancedSearchIsOpen
              ? '-'
              : '+'
          }
        </AdvancedSearch>
      </PrincipalSearchInput>
      <AdvancedSearchBox advancedSearchIsOpen={advancedSearchIsOpen}>
        <AdvancedSearchInput
          data-cy={'regulatory-layers-advanced-search-zone'}
          placeholder={'Zone (ex. Med, Bretagne, mer Celtique…)'}
          type="text"
          value={placeSearchText}
          onChange={e => setPlaceSearchText(e.target.value)}
        />
        <AdvancedSearchInput
          data-cy={'regulatory-layers-advanced-search-gears'}
          placeholder={'Engins (ex. chaluts, casiers, FPO, GNS…)'}
          type="text"
          value={gearSearchText}
          onChange={e => setGearSearchText(e.target.value)}
        />
        <AdvancedSearchInput
          data-cy={'regulatory-layers-advanced-search-species'}
          placeholder={'Espèces (ex. merlu, coque, SCE, PIL...)'}
          type="text"
          value={speciesSearchText}
          onChange={e => setSpeciesSearchText(e.target.value)}
        />
        <AdvancedSearchInput
          data-cy={'regulatory-layers-advanced-search-reg'}
          placeholder={'Référence reg. (ex. 58/2007, 171/2020, 1241...)'}
          type="text"
          value={regulatoryReferencesSearchText}
          onChange={e => setRegulatoryReferenceSearchText(e.target.value)}
        />
      </AdvancedSearchBox>
    </>)
}

const AdvancedSearchBox = styled.div`
  background-color: white;
  height: ${props => props.advancedSearchIsOpen ? 160 : 0}px;
  width: 320px;
  transition: 0.5s all;
  padding: ${props => props.advancedSearchIsOpen ? 10 : 0}px 15px;
  overflow: hidden;
  text-align: left;
  border-bottom: ${props => props.advancedSearchIsOpen ? 1 : 0}px ${COLORS.lightGray} solid;
`

const PrincipalSearchInput = styled.div`
  height: 40px;
  width: 100%;
`

const SearchBoxInput = styled.input`
  margin: 0;
  background-color: white;
  border: none;
  border-bottom: 1px ${COLORS.lightGray} solid;
  border-radius: 0;
  color: ${COLORS.gunMetal};
  font-size: 13px;
  height: 40px;
  width: 310px;
  padding: 0 5px 0 10px;
  flex: 3;
  background-image: url(${SearchIconSVG});
  background-size: 30px;
  background-position: bottom 3px right 5px;
  background-repeat: no-repeat;
  
  :hover, :focus {
    border-bottom: 1px ${COLORS.lightGray} solid;
  }
`

const AdvancedSearchInput = styled.input`
  border: none !important;
  border-bottom: 1px ${COLORS.lightGray} solid !important;
  background: ${COLORS.background} !important;
  overflow: none !important;
  width: 265px;
  margin: 5px 0 15px 0 !important;
  font-size: 13px;
  color: ${COLORS.gunMetal};

  :hover, :focus {
    border-bottom: 1px ${COLORS.lightGray} solid;
  }
`

const AdvancedSearch = styled.div`
  width: 40px;
  height: 40px;
  float: right;
  background: ${props => props.advancedSearchIsOpen ? COLORS.shadowBlue : COLORS.charcoal};
  cursor: pointer;
  font-size: 32px;
  line-height: 29px;
  color: ${COLORS.gainsboro};
  font-weight: 300;
  transition: 0.5s all;
`

export default RegulatoryLayerSearchInput
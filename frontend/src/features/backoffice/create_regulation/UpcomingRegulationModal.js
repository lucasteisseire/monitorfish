import React, { useEffect, useState } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import styled from 'styled-components'

import { COLORS } from '../../../constants/constants'
import {
  setIsModalOpen,
  setRegulatoryTextListValidityMap
} from '../Regulation.slice'
import RegulatoryTextSection from './RegulatoryTextSection'
import { ValidateButton, CancelButton } from '../../commonStyles/Buttons.style'
import { FooterButton } from '../../commonStyles/Backoffice.style'
import { ReactComponent as CloseIconSVG } from '../../icons/Croix_grise_clair.svg'

const UpcomingRegulationModal = () => {
  const dispatch = useDispatch()
  const {
    isModalOpen,
    upcomingRegulation,
    regulatoryTextListValidityMap
  } = useSelector(state => state.regulation)

  const [regulatoryTextList, setRegulatoryTextList] = useState(upcomingRegulation?.regulatoryTextList
    ? [...upcomingRegulation.regulatoryTextList]
    : [{}])

  const [saveForm, setSaveForm] = useState(false)

  const onAddUpcomingRegulation = () => {
    setSaveForm(true)
  }

  useEffect(() => {
    if (regulatoryTextListValidityMap) {
      const values = Object.values(regulatoryTextListValidityMap)
      if (saveForm && values.length > 0 && values.length === regulatoryTextList.length) {
        if (!values.includes(false)) {
          dispatch(setIsModalOpen(false))
        }
        dispatch(setRegulatoryTextListValidityMap({}))
        setSaveForm(false)
      }
    }
  }, [saveForm, regulatoryTextListValidityMap, regulatoryTextList])

  return (<RegulationModal isOpen={isModalOpen}>
    <ModalContent>
      <Body>
        <ModalTitle>
          BACKOFFISH - Ajouter une réglementation à venir
          <CloseIcon onClick={() => dispatch(setIsModalOpen(false))}/>
        </ModalTitle>
        <Section>
          <RegulatoryTextSection
            regulatoryTextList={regulatoryTextList}
            setRegulatoryTextList={setRegulatoryTextList}
            source={'upcomingRegulation'}
            saveForm={saveForm}
          />
        </Section>
      </Body>
      <Footer>
      <FooterButton>
        <ValidateButton
          disabled={false}
          isLast={false}
          onClick={() => onAddUpcomingRegulation()}
        >
          Ajouter la réglementation à venir
        </ValidateButton>
        <CancelButton
          disabled={false}
          isLast={false}
          onClick={() => dispatch(setIsModalOpen(false))}
        >
          Annuler
        </CancelButton>
      </FooterButton>
    </Footer>
    </ModalContent>
  </RegulationModal>)
}

const Body = styled.div`
  display: flex;
  flex-direction: column;
  overflow-y: scroll;
  height: calc(100vh - 260px);
`

const Footer = styled.div`
  background-color: ${COLORS.background};
  border-top: 1px solid ${COLORS.lightGray};
`

const CloseIcon = styled(CloseIconSVG)`
  width: 16px;
  vertical-align: text-bottom;
  cursor: pointer;
  float: right;
`

const RegulationModal = styled.div`
  display: ${props => props.isOpen ? 'block' : 'none'};
  width: 100%;
  height: 100vh;
  z-index: 1000;
  background-color: rgba(59, 69, 89, 0.5);
  position: fixed;
  top: 0;
`

const ModalContent = styled.div`
  margin: 100px 160px;
  background-color: ${COLORS.background};
`

const ModalTitle = styled.div`
  background-color: ${COLORS.charcoal};
  text-align: center;
  padding: 9px;
  font-size:13px;
  color: ${COLORS.white};
`

const Section = styled.div`
  padding: 40px 60px;
`

export default UpcomingRegulationModal
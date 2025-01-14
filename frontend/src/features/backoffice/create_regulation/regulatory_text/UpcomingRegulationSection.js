import React from 'react'
import { useDispatch } from 'react-redux'
import styled from 'styled-components'
import { COLORS } from '../../../../constants/constants'
import InfoBox from '../InfoBox'
import { CancelButton } from '../../../commonStyles/Buttons.style'
import { Link } from '../../../commonStyles/Backoffice.style'
import { setIsModalOpen, setUpcomingRegulation } from '../../Regulation.slice'

const UpcomingRegulationSection = ({ upcomingRegulation }) => {
  const dispatch = useDispatch()
  const DATE_STRING_OPTIONS = { year: 'numeric', month: '2-digit', day: '2-digit' }
  return (
      <>
      <Container>
        <YellowRectangle />
        <UpcomingRegulation>
          <Row><InfoBox /> <GrayText >Réglementation à venir</ GrayText></Row>
          {upcomingRegulation?.regulatoryTextList?.length > 0 && upcomingRegulation?.regulatoryTextList?.map((upcomingRegulationText, id) => {
            const {
              reference,
              url,
              startDate,
              endDate
            } = upcomingRegulationText
            return (
              <TextRow key={id}>
                <LinkWithGrayBg
                  href={url}
                  target={'_blank'}
                >{reference}</LinkWithGrayBg>
                {endDate !== 'infinite'
                  ? <TextWithGrayBg color={'#282F3E'}>Du {new Date(startDate).toLocaleString([], DATE_STRING_OPTIONS)} au {new Date(endDate).toLocaleString([], DATE_STRING_OPTIONS)}</TextWithGrayBg>
                  : <TextWithGrayBg color={'#282F3E'}>&Agrave; partir du {new Date(startDate).toLocaleString([], DATE_STRING_OPTIONS)}</TextWithGrayBg>}
              </TextRow>)
          })}
          <Row><CancelButton
            disabled={false}
            isLast={false}
            onClick={() => dispatch(setIsModalOpen(true))}
          >
            Éditer la réglementation
          </CancelButton>
          <CancelButton
            disabled={false}
            isLast={false}
            onClick={() => dispatch(setUpcomingRegulation(undefined))}
          >
            Supprimer la réglementation
          </CancelButton></Row>
        </ UpcomingRegulation>
      </Container>
      </>
  )
}

const LinkWithGrayBg = styled(Link)` 
  background-color: ${COLORS.gainsboro};
  padding: 5px 10px;
  font-size: 13px;
  margin-bottom: 5px;
  width: max-content;
`

const TextRow = styled.div`
  display: flex;
  flex-direction: column;
  padding: 10px 0 10px 0;
`

const Row = styled.span`
  display: flex;
  flex-direction: row;
  align-items: center;
  margin: 5px 0px;
`

const TextWithGrayBg = styled.p`
  background-color: ${COLORS.gainsboro};
  color: ${props => props.color};
  box-sizing: border-box;
  margin: 0 0 5px 0;
  width: max-content;
  padding: 5px 10px;
  font-size: 13px;
`

const GrayText = styled.p`
  margin: 0 0 0 5px;
  color: ${COLORS.slateGray};
`

const Container = styled.div`
  display: flex;
  flex-direction: row;
  box-sizing: border-box;
  border: 1px solid ${COLORS.slateGray};
  margin: 15px 0px;
  width: max-content;
`

const YellowRectangle = styled.div`
  width: 10px;
  background-color: ${COLORS.orange};
`

const UpcomingRegulation = styled.div`
  padding: 10px 15px;
`

export default UpcomingRegulationSection

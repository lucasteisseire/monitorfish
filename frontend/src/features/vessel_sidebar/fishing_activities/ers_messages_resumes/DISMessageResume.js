import React, { useEffect, useRef, useState } from 'react'
import styled from 'styled-components'
import { COLORS } from '../../../../constants/constants'
import ERSMessageResumeHeader from './ERSMessageResumeHeader'
import SpeciesAndWeightChart from './SpeciesAndWeightChart'
import { ERSMessageType as ERSMessageTypeEnum } from '../../../../domain/entities/ERS'

const DISMessageResume = props => {
  const [isOpen, setIsOpen] = useState(false)
  const firstUpdate = useRef(true)
  const [speciesAndWeightArray, setSpeciesAndWeightArray] = useState([])
  const [chartHeight, setChartHeight] = useState(0)

  useEffect(() => {
    if (props.speciesToWeightOfDIS) {
      const array = Object.keys(props.speciesToWeightOfDIS)
        .map(species => props.speciesToWeightOfDIS[species])
        .sort((a, b) => {
          if (a.weight < b.weight) {
            return 1
          } else {
            return -1
          }
        })
      setSpeciesAndWeightArray(array)
    }
  }, [props.speciesToWeightOfDIS])

  useEffect(() => {
    if (isOpen) {
      firstUpdate.current = false
    }
  }, [isOpen])

  const getDISMessageResumeTitleText = () => {
    return `${props.numberOfMessages} message${props.numberOfMessages > 1 ? 's' : ''} - ${props.totalDISWeight} kg rejetés au total`
  }

  const getDISMessageResumeTitle = () => {
    return <>{props.numberOfMessages} message{props.numberOfMessages > 1 ? 's' : ''} - {props.totalDISWeight} kg rejetés
      au total</>
  }

  return <Wrapper>
    <ERSMessageResumeHeader
      onHoverText={props.hasNoMessage ? null : getDISMessageResumeTitleText()}
      title={props.hasNoMessage ? null : getDISMessageResumeTitle()}
      hasNoMessage={props.hasNoMessage}
      noContent={!props.hasNoMessage && !props.totalDISWeight}
      showERSMessages={props.showERSMessages}
      messageType={ERSMessageTypeEnum.DIS.code.toString()}
      setIsOpen={setIsOpen}
      isOpen={isOpen}/>
    {
      props.hasNoMessage
        ? null
        : <ERSMessageContent
          id={props.id}
          chartHeight={chartHeight}
          species={(speciesAndWeightArray && speciesAndWeightArray.length > 0) ? speciesAndWeightArray.length : 1}
          firstUpdate={firstUpdate}
          isOpen={isOpen}
          name={ERSMessageTypeEnum.DIS.code.toString()}>
          <Zone>
            <SpeciesAndWeightChart
              setChartHeight={setChartHeight}
              compareWithTotalWeight={true}
              speciesAndWeightArray={speciesAndWeightArray}
            />
          </Zone>
        </ERSMessageContent>
    }
  </Wrapper>
}

const Zone = styled.div`
  margin: 10px;
  text-align: left;
  display: flex;
  flex-wrap: wrap;
`

const Wrapper = styled.li`
  margin: 0;
  border-radius: 0;
  padding: 0;
  overflow: hidden;
  color: ${COLORS.slateGray};
`

const ERSMessageContent = styled.div`
  background: ${COLORS.background};
  width: inherit;
  overflow: hidden;
  padding-left: 20px;
  border-bottom: 1px solid ${COLORS.gray};
  opacity: ${props => props.isOpen ? 1 : 0};
  height: ${props => props.isOpen
    ? props.chartHeight + 20
    : 0
  }px;
  transition: 0.2s all;
  margin-bottom: ${props => props.isOpen ? 5 : -1}px;
`

export default DISMessageResume

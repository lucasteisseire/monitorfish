import React from 'react'
import styled from 'styled-components'
import { COLORS, INFO_TEXT } from '../../../constants/constants'

const InfoBox = props => {
  const {
    isInfoTextShown,
    setIsInfoTextShown,
    isFormOpened,
    message
  } = props
  return (
    <InfoTextParent
      isInfoTextShown={isInfoTextShown}
      isFormOpened={isFormOpened}
      onMouseLeave={() => setIsInfoTextShown && !isFormOpened && setIsInfoTextShown(false)}
      pointer={message}
    >
      {isInfoTextShown
        ? <InfoTextWrapper
          isFormOpened={isFormOpened}
          onMouseLeave={() => setIsInfoTextShown && !isFormOpened && setIsInfoTextShown(false)}
          >
          <InfoPoint>!</InfoPoint>
          <InfoText>
            {INFO_TEXT[message]}
          </InfoText>
        </InfoTextWrapper>
        : <InfoPoint
          onMouseEnter={() => setIsInfoTextShown && setIsInfoTextShown(true)}
          onMouseOut={() => setIsInfoTextShown && setIsInfoTextShown(false)}
        >!</InfoPoint>}
    </InfoTextParent>)
}

const InfoTextParent = styled.div`
  display: flex;
  min-height: 20px;
  min-width: 20px;
  position: relative;
  cursor: ${props => props.pointer ? 'pointer' : 'default'};
  ${props => props.isFormOpened && props.isInfoTextShown ? 'left: 352px' : ''};
  ${props => props.isFormOpened && props.isInfoTextShown ? 'margin-top: 8px' : ''};
`

const InfoTextWrapper = styled.div`
  display: flex;
  ${props => props.isFormOpened ? '' : 'position: absolute;'};
  border: 1px solid ${COLORS.lightGray};
  background: ${COLORS.gainsboro} 0% 0% no-repeat padding-box;
  border-radius: 2px;
  min-width: 560px;
  max-width: 600px;
  padding: 8px;
  box-sizing: border-box;
  z-index: 30;
  top: '-6px';
  left: '0';
`

const InfoText = styled.span`
  align-self: center;
  display: 'flex';
  font-size: 13px;
  color: ${COLORS.gunMetal};
  padding-left: 8px;
  white-space: pre-line;
`

const InfoPoint = styled.a`
  display: inline-block;
  align-self: start;
  min-height: 20px;
  min-width: 20px;
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: ${COLORS.slateGray} 0% 0% no-repeat padding-box;
  color: ${COLORS.white};
  text-align: center;
  font: normal normal bold 13px Arial;
  text-align: center;
  line-height: 20px;
  &:hover {
    text-decoration: none;
    color: ${COLORS.white};
  }
  &:focus {
    text-decoration: none;
    color: ${COLORS.white};
  }
`

export default InfoBox
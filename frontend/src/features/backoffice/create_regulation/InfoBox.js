import React from 'react'
import styled from 'styled-components'
import { COLORS } from '../../../constants/constants'

const InfoBox = props => {
  const {
    isInfoTextShown,
    setIsInfoTextShown,
    isFormOpened,
    message,
    className,
    children
  } = props
  return (
    <InfoTextParent
      isInfoTextShown={isInfoTextShown}
      isFormOpened={isFormOpened}
      onMouseLeave={() => setIsInfoTextShown && !isFormOpened && setIsInfoTextShown(false)}
      pointer={message}
      className={className}
    >
      {isInfoTextShown
        ? <InfoTextWrapper
          isInfoTextShown={isInfoTextShown}
          isFormOpened={isFormOpened}
          onMouseLeave={() => setIsInfoTextShown && !isFormOpened && setIsInfoTextShown(false)}
          >
          <InfoPoint
            isInfoTextShown={isInfoTextShown}
          >!</InfoPoint>
          <ChildrenWrapper>
            {children}
          </ChildrenWrapper>
        </InfoTextWrapper>
        : <InfoPoint
          onMouseEnter={() => setIsInfoTextShown && setIsInfoTextShown(true)}
          onMouseOut={() => setIsInfoTextShown && setIsInfoTextShown(false)}
        >!</InfoPoint>}
    </InfoTextParent>)
}

const InfoTextParent = styled.div`
  display: flex;
  min-height: 14px;
  min-width: 14px;
  position: relative;
  cursor: ${props => props.pointer ? 'pointer' : 'default'};
  ${props => props.isFormOpened && props.isInfoTextShown ? 'left: 384px' : ''};
  ${props => props.isFormOpened && props.isInfoTextShown ? 'margin-top: 8px' : ''};
`

const ChildrenWrapper = styled.div`
  display: flex;
  flex-direction: column;
  text-align: left;
`

const InfoTextWrapper = styled.div`
  display: flex;
  ${props => props.isFormOpened ? '' : 'position: absolute;'};
  border: 1px solid ${COLORS.lightGray};
  background: ${COLORS.gainsboro} 0% 0% no-repeat padding-box;
  border-radius: 2px;
  min-width: 460px;
  max-width: 500px;
  padding: 8px 20px 20px 8px;
  ${props => props.isInfoTextShown && !props.isFormOpened ? 'margin-top: -10px;' : ''}
  box-sizing: border-box;
  z-index: 30;
`

const InfoPoint = styled.a`
  display: inline-block;
  align-self: start;
  min-height: 14px;
  min-width: 14px;
  height: 14px;
  width: 14px;
  border-radius: 50%;
  background: ${props => props.isInfoTextShown ? COLORS.charcoal : COLORS.slateGray} 0% 0% no-repeat padding-box;
  color: ${COLORS.white};
  text-align: center;
  font-size: 11px;
  font-weight: bold;
  text-align: center;
  line-height: 12px;
  &:hover {
    text-decoration: none;
    color: ${COLORS.white};
  }
  &:focus {
    text-decoration: none;
    background-color: ${COLORS.charcoal};
  }
`

export default InfoBox

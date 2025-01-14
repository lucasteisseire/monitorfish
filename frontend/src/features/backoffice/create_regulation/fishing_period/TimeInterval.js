import React from 'react'
import styled from 'styled-components'
import CustomDatePicker, { CUSTOM_DATEPICKER_TYPES } from '../custom_form/CustomDatePicker'
import { COLORS } from '../../../../constants/constants'

const TimeInterval = props => {
  const {
    disabled,
    id,
    timeInterval,
    onTimeIntervalChange,
    isLast
  } = props

  const setTimeInterval = (key, value) => {
    const newTimeInterval = {
      ...timeInterval,
      [key]: value
    }
    onTimeIntervalChange(id, newTimeInterval)
  }

  return (
    <Wrapper $isLast={isLast}>De<CustomDatePicker
        format={'HH:mm'}
        type={CUSTOM_DATEPICKER_TYPES.TIME}
        placement={'rightEnd'}
        style={{ width: '55px', margin: '0px 5px' }}
        disabled={disabled}
        value={timeInterval?.from}
        saveValue={value => setTimeInterval('from', value)}
      />
      à<CustomDatePicker
        format={'HH:mm'}
        type={CUSTOM_DATEPICKER_TYPES.TIME}
        placement={'rightEnd'}
        style={{ width: '55px', margin: '0px 5px' }}
        disabled={disabled}
        value={timeInterval?.to}
        saveValue={value => setTimeInterval('to', value)}
      />
    </Wrapper>
  )
}

const Wrapper = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  ${props => props.$isLast ? '' : 'margin-bottom: 5px;'}
  color: ${COLORS.slateGray};
  opacity: ${props => props.disabled ? '0.4' : '1'};
`

export default TimeInterval

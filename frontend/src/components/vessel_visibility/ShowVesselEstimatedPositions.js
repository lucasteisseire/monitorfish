import React from 'react'
import { Checkbox } from 'rsuite'
import styled from 'styled-components'
import { COLORS } from '../../constants/constants'
import { useDispatch, useSelector } from 'react-redux'
import { showVesselsEstimatedPositions } from '../../domain/reducers/Map'

const ShowVesselEstimatedPositions = () => {
  const dispatch = useDispatch()
  const { showingVesselsEstimatedPositions } = useSelector(state => state.map)

  return (
    <Wrapper>
      <RadioWrapper>
        <Checkbox
          checked={showingVesselsEstimatedPositions}
          onChange={(value, isChecked) => {
            dispatch(showVesselsEstimatedPositions(isChecked))
          }}

        >{' '} <ShowLabelText>Afficher les positions estimées des navires</ShowLabelText></Checkbox>
      </RadioWrapper>
    </Wrapper>
  )
}

const Wrapper = styled.div`
  background: ${COLORS.grayBackground};
  padding: 0 0 9px 7px;
  border-bottom-left-radius: 2px;
  border-bottom-right-radius: 2px;
  border-top: 1px solid ${COLORS.squareBorder};
`

const ShowLabelText = styled.span`
  margin-left: 0;
  color: #969696;
`

const RadioWrapper = styled.div`
  padding: 0;
  font-size: 13px;
  text-align: left;
`

export default ShowVesselEstimatedPositions
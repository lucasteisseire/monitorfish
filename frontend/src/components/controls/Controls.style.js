import styled from 'styled-components'
import { COLORS } from '../../constants/constants'

export const Zone = styled.div`
  margin: 10px 5px 0 5px;
  text-align: left;
  display: flex;
  flex-wrap: wrap;
  background: ${COLORS.background};
`

export const Title = styled.div`
  color: ${COLORS.textGray};
  background: ${COLORS.grayDarker};
  padding: 8.5px 10px 8px 20px;
  font-size: 0.8rem;
  flex-shrink: 0;
  flex-grow: 2;
  display: flex;
  width: 400px;
  font-size: 13px;
  font-weight: 500;
`

export const NoValue = styled.span`
  color: ${COLORS.grayDarkerTwo};
  font-weight: 300;
  line-height: normal;
`

export const StrongText = styled.span`
  color: ${COLORS.grayDarkerThree};
  margin-left: 5px;
`

export const Red = styled.span`
  height: 8px;
  width: 8px;
  margin-left: 5px;
  background-color: #E1000F;
  border-radius: 50%;
  display: inline-block;
`

export const Green = styled.span`
  height: 8px;
  width: 8px;
  margin-left: 5px;
  background-color: #8CC63F;
  border-radius: 50%;
  display: inline-block;
`
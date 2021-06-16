import React from 'react'
import styled from 'styled-components'
import { ReactComponent as ChevronIconSVG } from '../icons/Chevron_simple_gris.svg'

export const ChevronIconCommon = props => {
  return (
      <ChevronIcon {...props} />
  )
}

const ChevronIcon = styled(ChevronIconSVG)`
  transform: ${props => props.isOpen ? 'rotate(0deg)' : 'rotate(180deg)'};
  transition: 0.5s all;
`

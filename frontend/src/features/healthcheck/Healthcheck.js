import React from 'react'
import styled from 'styled-components'
import { useSelector } from 'react-redux'
import { ReactComponent as WarningSVG } from '../icons/Picto_alerte.svg'

const Healthcheck = () => {
  const {
    healthcheckTextWarning,
    previewFilteredVesselsMode
  } = useSelector(state => state.global)

  return (<>
    {
      healthcheckTextWarning && !previewFilteredVesselsMode
        ? <HealthcheckWarnings>
          <Warning>
            <WarningIcon />
            {healthcheckTextWarning}
          </Warning>
        </HealthcheckWarnings>
        : null
    }
  </>)
}

const WarningIcon = styled(WarningSVG)`
  width: 20px;
  vertical-align: sub;
  margin-right: 8px;
  height: 18px
`

const Warning = styled.div`
  font: normal normal bold 16px/22px Marianne;
`

const HealthcheckWarnings = styled.div`
  background: #F6D012 0% 0% no-repeat padding-box;
  width 100%;
  height: 22px;
  text-align: center;
  padding: 13px;
  border-bottom: 2px solid #E3BE05;
`

export default Healthcheck

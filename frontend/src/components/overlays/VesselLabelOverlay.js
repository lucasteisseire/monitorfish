import React, { createRef, useEffect, useRef, useState } from 'react'
import Overlay from 'ol/Overlay'
import styled from 'styled-components'
import { COLORS } from '../../constants/constants'
import Hammer from 'hammerjs'

const X = 0
const Y = 1
const initialOffsetValue = [5, -30]

const VesselLabelOverlay = ({ map, coordinates, offset, flagState, text, featureId, moveVesselLabelLine, zoomHasChanged }) => {
  const ref = createRef()

  const currentOffset = useRef(initialOffsetValue)
  const currentCoordinates = useRef([])
  const isThrottled = useRef(false)
  const [showed, setShowed] = useState(false)
  const [overlay] = useState(new Overlay({
    element: ref.current,
    position: coordinates,
    offset: currentOffset.current,
    autoPan: false,
    positioning: 'left-center'
  }))

  useEffect(() => {
    if (overlay && offset) {
      currentOffset.current = offset
      overlay.setOffset(offset)
    }
  }, [offset, overlay])

  useEffect(() => {
    if (map) {
      overlay.setPosition(coordinates)
      overlay.setElement(ref.current)

      map.addOverlay(overlay)
      setShowed(true)

      overlay.on('change:offset', ({ target }) => {
        moveVesselLabelWithThrottle(target, 50)
      })

      return () => {
        map.removeOverlay(overlay)
      }
    }
  }, [overlay, coordinates, map])

  useEffect(() => {
    if (currentOffset.current !== initialOffsetValue) {
      moveVesselLabelWithThrottle(overlay, 100)
    }
  }, [zoomHasChanged])

  useEffect(() => {
    if (showed) {
      const hammer = new Hammer(overlay.getElement())
      hammer.on('pan', ({ deltaX, deltaY }) => {
        overlay.setOffset([currentOffset.current[X] + deltaX, currentOffset.current[Y] + deltaY])
      })

      hammer.on('panend', ({ deltaX, deltaY }) => {
        currentOffset.current = [currentOffset.current[X] + deltaX, currentOffset.current[Y] + deltaY]
      })
    }
  }, [showed])

  function moveVesselLabelWithThrottle (target, delay) {
    if (isThrottled.current) {
      return
    }

    isThrottled.current = true
    setTimeout(() => {
      const offset = target.getOffset()
      const pixel = map.getPixelFromCoordinate(coordinates)

      const { width, height } = target.getElement().getBoundingClientRect()
      const nextXPixelCenter = pixel[X] + offset[X] + width / 2
      const nextYPixelCenter = pixel[Y] + offset[Y] + height / 2

      const nextCoordinates = map.getCoordinateFromPixel([nextXPixelCenter, nextYPixelCenter])
      currentCoordinates.current = nextCoordinates
      moveVesselLabelLine(featureId, coordinates, nextCoordinates, offset)

      isThrottled.current = false
    }, delay)
  }

  return (
    <WrapperToBeKeptForDOMManagement>
      <div ref={ref}>
        {
          showed
            ? <VesselLabelOverlayElement>
              {
                flagState
                  ? <Flag rel="preload" src={`flags/${flagState.toLowerCase()}.svg`}/>
                  : null
              }
              <ZoneText>
                {text}
              </ZoneText>
            </VesselLabelOverlayElement>
            : null
        }
      </div>
    </WrapperToBeKeptForDOMManagement>
  )
}

const WrapperToBeKeptForDOMManagement = styled.div`
  z-index: 300;
`

const VesselLabelOverlayElement = styled.div`
  padding: 0 6px 2px 4px;
  box-shadow: 0px 2px 3px #969696BF;
  background: ${COLORS.background};
  line-height: 18px;
  cursor: grabbing;
`

const Flag = styled.img`
  vertical-align: middle;
  height: 12px;
  margin-top: -2px;
  margin-right: 2px;
  user-select: none;
  cursor: grabbing;
`

const ZoneText = styled.span`
  font-size: 13px;
  font-weight: 500;
  display: inline-block;
  user-select: none;
  color: ${COLORS.grayDarkerThree};
  line-height: 18.5px;
  cursor: grabbing;
  margin-left: 2px;
`

export default VesselLabelOverlay
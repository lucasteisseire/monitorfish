import { Icon, Style } from 'ol/style'
import { asArray } from 'ol/color'
import CircleStyle from 'ol/style/Circle'
import Fill from 'ol/style/Fill'
import { VESSEL_ICON_STYLE, VESSEL_SELECTOR_STYLE, Vessel } from '../../domain/entities/vessel'

import { COLORS } from '../../constants/constants'

const iconStyleCache = new Map()
const circleStyleCache = new Map()

export const selectedVesselStyle = new Style({
  image: new Icon({
    opacity: 1,
    src: 'select.png',
    scale: 0.4
  }),
  zIndex: VESSEL_SELECTOR_STYLE
})

export const getIconStyle = object => {
  const key = JSON.stringify(object)

  if (!iconStyleCache.has(key)) {
    iconStyleCache.set(key, new Style({
      image: new Icon({
        src: object.vesselFileName,
        offset: [0, 0],
        imgSize: [8, 16],
        rotation: degreesToRadian(object.course),
        // See https://github.com/openlayers/openlayers/issues/11133#issuecomment-638987210
        color: 'white',
        opacity: object.opacity
      }),
      zIndex: VESSEL_ICON_STYLE
    }))
  }

  return iconStyleCache.get(key)
}

export const getCircleStyle = object => {
  const key = JSON.stringify(object)

  if (!circleStyleCache.has(key)) {
    let color = asArray(object.vesselColor)
    color = color.slice()
    color[3] = object.opacity

    circleStyleCache.set(key, new Style({
      image: new CircleStyle({
        radius: 4,
        fill: new Fill({
          color: color
        })
      }),
      zIndex: VESSEL_ICON_STYLE
    }))
  }

  return circleStyleCache.get(key)
}

export const getVesselStyle = feature => {
  const {
    filterColor,
    opacity,
    isLight,
    course,
    speed,
    nonFilteredVesselsAreHidden,
    isShowedInFilter
  } = feature.getProperties()

  if (nonFilteredVesselsAreHidden && filterColor && !isShowedInFilter) {
    return []
  }

  const vesselFileName = getVesselFilename(filterColor, isShowedInFilter, isLight)
  const vesselColor = getVesselColor(filterColor, isShowedInFilter, isLight)

  const styles = speed > Vessel.vesselIsMovingSpeed
    ? [getIconStyle({ vesselFileName, course, opacity })]
    : [getCircleStyle({ vesselColor, opacity })]

  if (feature.getProperties().isSelected) {
    styles.push(selectedVesselStyle)
  }

  return styles
}

function getVesselFilename (filterColor, isShowedInFilter, isLight) {
  let vesselFileName = 'Couleur_navires_fond_clair_05065f_png24.png'

  if (filterColor && isShowedInFilter) {
    vesselFileName = `Couleurs_filtres_navires_${filterColor.replace('#', '')}_png24.png`
  } else if (isLight) {
    vesselFileName = 'Couleur_navires_fond_sombre_cacce0_png24.png'
  }

  return vesselFileName
}

function getVesselColor (filterColor, isShowedInFilter, isLight) {
  let vesselColor = COLORS.vesselColor

  if (filterColor && isShowedInFilter) {
    vesselColor = filterColor
  } else if (isLight) {
    vesselColor = COLORS.vesselLightColor
  }

  return vesselColor
}

export function degreesToRadian (course) {
  return course * Math.PI / 180
}
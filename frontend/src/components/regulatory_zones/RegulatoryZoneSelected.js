import React, {useEffect, useState} from "react";
import styled from 'styled-components';
import {ReactComponent as ChevronIconSVG} from '../icons/Chevron_simple_gris.svg'
import RegulatoryZoneSelectedLayer from "./RegulatoryZoneSelectedLayer";
import {COLORS} from "../../constants/constants";

const RegulatoryZoneSelected = props => {
    const [showRegulatoryZonesSelected, setShowRegulatoryZonesSelected] = useState(false);
    const [numberOfZonesOpened, setNumberOfZonesOpened] = useState(0)

    function increaseNumberOfZonesOpened(number) {
        setNumberOfZonesOpened(numberOfZonesOpened + number)
    }

    function decreaseNumberOfZonesOpened(number) {
        const value = numberOfZonesOpened - number
        if (value < 0) {
            setNumberOfZonesOpened(0)
        } else {
            setNumberOfZonesOpened(value)
        }
    }

    const callRemoveRegulatoryZoneFromMySelection = (regulatoryZone, numberOfZones) => {
        decreaseNumberOfZonesOpened(numberOfZones)
        props.callRemoveRegulatoryZoneFromMySelection(regulatoryZone)
    }

    useEffect(() => {
        if(props.regulatoryZoneMetadata) {
            setShowRegulatoryZonesSelected(true)
        }
    }, [props.regulatoryZoneMetadata])

    useEffect(() => {
        if(props.hideZonesListWhenSearching) {
            setShowRegulatoryZonesSelected(false)
        } else {
            setShowRegulatoryZonesSelected(true)
        }
    }, [props.hideZonesListWhenSearching])

    return (
        <>
            <RegulatoryZoneSelectedTitle
                onClick={() => setShowRegulatoryZonesSelected(!showRegulatoryZonesSelected)}
                regulatoryZonesAddedToMySelection={props.regulatoryZonesAddedToMySelection}
            >
                Mes zones réglementaires <ChevronIcon isOpen={showRegulatoryZonesSelected}/>
            </RegulatoryZoneSelectedTitle>
            <RegulatoryZoneSelectedList
                layerLength={Object.keys(props.selectedRegulatoryZones).length}
                zoneLength={numberOfZonesOpened}
                showRegulatoryZonesSelected={showRegulatoryZonesSelected}
            >
                {
                    props.selectedRegulatoryZones && Object.keys(props.selectedRegulatoryZones).length > 0 ? Object.keys(props.selectedRegulatoryZones).map((regulatoryZoneName, index) => {
                        return (<ListItem key={regulatoryZoneName}>
                            <RegulatoryZoneSelectedLayer
                                increaseNumberOfZonesOpened={increaseNumberOfZonesOpened}
                                decreaseNumberOfZonesOpened={decreaseNumberOfZonesOpened}
                                isReadyToShowRegulatoryZones={props.isReadyToShowRegulatoryZones}
                                callRemoveRegulatoryZoneFromMySelection={callRemoveRegulatoryZoneFromMySelection}
                                regulatoryZoneName={regulatoryZoneName}
                                regulatorySubZones={props.selectedRegulatoryZones[regulatoryZoneName]}
                                callShowRegulatoryZone={props.callShowRegulatoryZone}
                                callHideRegulatoryZone={props.callHideRegulatoryZone}
                                callShowRegulatorySubZoneMetadata={props.callShowRegulatorySubZoneMetadata}
                                callCloseRegulatoryZoneMetadata={props.callCloseRegulatoryZoneMetadata}
                                regulatoryZoneMetadata={props.regulatoryZoneMetadata}
                                showedLayers={props.showedLayers}
                                gears={props.gears}
                                isLastItem={Object.keys(props.selectedRegulatoryZones).length === index + 1}
                            />
                        </ListItem>)
                    }) : <NoZoneSelected>Aucune zone sélectionnée</NoZoneSelected>
                }
            </RegulatoryZoneSelectedList>
        </>
    )
}

const NoZoneSelected = styled.div`
  color: ${COLORS.grayDarkerTwo};
  margin: 10px;
  font-size: 13px;
`

const RegulatoryZoneSelectedTitle = styled.div`
  height: 27px;
  padding-top: 8px;
  margin-top: 9px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  background: ${COLORS.grayDarker};
  
  animation: ${props => props.regulatoryZonesAddedToMySelection ? 'blink' : ''} 0.3s ease forwards;

  @keyframes blink {
    0%   {
        background: ${COLORS.grayDarker};
    }
    20%   {
        background: ${COLORS.grayDarkerTwo};
    }
    40% {
        background: ${COLORS.grayDarker};
    }
    60%   {
        background: ${COLORS.grayDarker};
    }
    80%   {
        background: ${COLORS.grayDarkerTwo};
    }
    100% {
        background: ${COLORS.grayDarker};
    }
  }
  
  color: ${COLORS.grayDarkerTwo};
  font-size: 0.8em;
  cursor: pointer;
  font-weight: 500;
  text-align: left;
  padding-left: 15px;
  user-select: none;
`

const RegulatoryZoneSelectedList = styled.ul`
  margin: 0;
  background-color: ${COLORS.background};
  border-radius: 0;
  padding: 0;
  height: ${props => {
        if(props.layerLength) {
            if(props.zoneLength > 0) {
                return props.layerLength * 37 + props.zoneLength * 38.5
            } else {
                return props.layerLength * 37
            }
        } else {
            return 40
        }
    }}px;
  max-height: 550px;
  overflow-y: ${props => {
            if(props.layerLength) {
                if(props.zoneLength > 0) {
                    return props.layerLength + props.zoneLength > 13 ? 'auto' : 'hidden' 
                }
                
                return 'hidden'
            } else {
               return 'hidden'
            }
        }};
  overflow-x: hidden;
  color: ${COLORS.grayDarkerThree};
  
  animation: ${props => props.showRegulatoryZonesSelected ? 'regulatory-selected-opening' : 'regulatory-selected-closing'} 0.5s ease forwards;

  @keyframes regulatory-selected-opening {
    0%   {
        height: 0;
        opacity: 0;
    }
    100% {
        opacity: 1;
    }
  }

  @keyframes regulatory-selected-closing {
    0%   {
        opacity: 1;
    }
    100% {
        opacity: 0;
        height: 0;
    }
  }
`

const ListItem = styled.li`
  padding: 0px 5px 0px 0px;
  margin: 0;
  font-size: 0.8em;
  text-align: left;
  list-style-type: none;
  width: 100%;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden !important;
  cursor: pointer;
  margin: 0;
  border-bottom: rgba(255, 255, 255, 0.2) 1px solid;
  line-height: 1.9em;
`

const ChevronIcon = styled(ChevronIconSVG)`
  transform: rotate(180deg);
  width: 17px;
  float: right;
  margin-right: 10px;
  margin-top: 5px;
  
  animation: ${props => props.isOpen ? 'chevron-zones-opening' : 'chevron-zones-closing'} 0.5s ease forwards;

  @keyframes chevron-zones-opening {
    0%   { transform: rotate(180deg); }
    100% { transform: rotate(0deg); }
  }

  @keyframes chevron-zones-closing {
    0%   { transform: rotate(0deg); }
    100% { transform: rotate(180deg);   }
  }
`

export default RegulatoryZoneSelected
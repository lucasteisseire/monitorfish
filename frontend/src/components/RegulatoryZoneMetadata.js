import React, {useEffect, useState} from "react";
import styled from 'styled-components';
import {COLORS} from "../constants/constants";
import {ReactComponent as REGPaperSVG} from './icons/reg_paper.svg'
import {ReactComponent as CloseIconSVG} from './icons/Croix_grise.svg'
import {FingerprintSpinner} from "react-epic-spinners";

const RegulatoryZoneMetadata = props => {
    const [gears, setGears] = useState([])

    useEffect(() => {
        if (props.regulatoryZoneMetadata && props.gears) {
            if(!props.regulatoryZoneMetadata.gears){
                return setGears(null)
            }

            let gearCodesArray = props.regulatoryZoneMetadata.gears.replace(/ /g, '').split(',')
            let gears = gearCodesArray.map(gearCode => {
                let foundGear = props.gears.find(gear => gear.code === gearCode)
                return {
                    name: foundGear ? foundGear.name : null,
                    code: gearCode
                }
            })

            setGears(gears)
        }
    }, [props.gears, props.regulatoryZoneMetadata])

    return (
        <Wrapper
            firstUpdate={props.firstUpdate}
            openBox={props.regulatoryZoneMetadataPanelIsOpen}
        >
            {
                props.regulatoryZoneMetadataPanelIsOpen && props.regulatoryZoneMetadata ?
                    <>
                        <Header>
                            <REGPaperIcon/>
                            <Title>Réglementation "<RegulatoryName><Ellipsis>{props.regulatoryZoneMetadata.zone}</Ellipsis></RegulatoryName>"</Title>
                            <CloseIcon onClick={() => props.callCloseRegulatoryZoneMetadata()}/>
                        </Header>
                        <Content>
                            <Zone>
                                <Fields>
                                    <Body>
                                        <Field>
                                            <Key>Façade</Key>
                                            <Value>{props.regulatoryZoneMetadata.seafront ? props.regulatoryZoneMetadata.seafront : <NoValue>-</NoValue>}</Value>
                                        </Field>
                                        <Field>
                                            <Key>Région</Key>
                                            <Value>{props.regulatoryZoneMetadata.region ? props.regulatoryZoneMetadata.region : <NoValue>-</NoValue>}</Value>
                                        </Field>
                                        <Field>
                                            <Key>Zone</Key>
                                            <Value>{props.regulatoryZoneMetadata.zone ? props.regulatoryZoneMetadata.zone : <NoValue>-</NoValue>}</Value>
                                        </Field>
                                    </Body>
                                </Fields>
                            </Zone>
                            <Zone>
                                <Fields>
                                    <Body>
                                        <Field>
                                            <Key>Période(s)</Key>
                                            <Value>{props.regulatoryZoneMetadata.period ? props.regulatoryZoneMetadata.period : <NoValue>-</NoValue>}</Value>
                                        </Field>
                                        <Field>
                                            <Key>Dates d'ouvertures</Key>
                                            <Value>{props.regulatoryZoneMetadata.openingDate ? props.regulatoryZoneMetadata.openingDate : <NoValue>-</NoValue>}</Value>
                                        </Field>
                                        <Field>
                                            <Key>Dates de fermetures</Key>
                                            <Value>{props.regulatoryZoneMetadata.closingDate ? props.regulatoryZoneMetadata.closingDate : <NoValue>-</NoValue>}</Value>
                                        </Field>
                                        <Field>
                                            <Key>État</Key>
                                            <Value>{props.regulatoryZoneMetadata.state ? props.regulatoryZoneMetadata.state : <NoValue>-</NoValue>}</Value>
                                        </Field>
                                    </Body>
                                </Fields>
                            </Zone>
                            <ZoneWithLineBreak>
                                <KeyWithLineBreak>Engin(s)</KeyWithLineBreak>
                                {
                                    gears ?
                                    gears.map(gear => {
                                        return gear.name ?
                                            <ValueWithLineBreak key={gear.code}>{gear.name} ({gear.code})</ValueWithLineBreak>
                                            : <ValueWithLineBreak key={gear.code}>{gear.code}</ValueWithLineBreak>

                                    }) : <NoValue>-</NoValue>
                                }
                                <KeyWithLineBreak>Mesures techniques</KeyWithLineBreak>
                                <ValueWithLineBreak>{props.regulatoryZoneMetadata.technicalMeasures ? props.regulatoryZoneMetadata.technicalMeasures : <NoValue>-</NoValue>} </ValueWithLineBreak>
                            </ZoneWithLineBreak>
                            <ZoneWithLineBreak>
                                <KeyWithLineBreak>Espèce(s)</KeyWithLineBreak>
                                {
                                    props.regulatoryZoneMetadata.species ?
                                        props.regulatoryZoneMetadata.species.replace(/ /g, '').split(',').map(species => {
                                            return <ValueWithLineBreak key={species}>{species}</ValueWithLineBreak>
                                        }) : <NoValue>-</NoValue>
                                }
                                <KeyWithLineBreak>Tailles</KeyWithLineBreak>
                                <ValueWithLineBreak>{props.regulatoryZoneMetadata.size ? props.regulatoryZoneMetadata.size : <NoValue>-</NoValue>} </ValueWithLineBreak>
                                <KeyWithLineBreak>Quantités</KeyWithLineBreak>
                                <ValueWithLineBreak>{props.regulatoryZoneMetadata.quantity ? props.regulatoryZoneMetadata.quantity : <NoValue>-</NoValue>} </ValueWithLineBreak>
                            </ZoneWithLineBreak>
                            <ZoneWithLineBreak>
                                <KeyWithLineBreak>Documents obligatoires</KeyWithLineBreak>
                                <ValueWithLineBreak>{props.regulatoryZoneMetadata.mandatoryDocuments ? props.regulatoryZoneMetadata.mandatoryDocuments : <NoValue>-</NoValue>} </ValueWithLineBreak>
                                <KeyWithLineBreak>Interdictions</KeyWithLineBreak>
                                <ValueWithLineBreak>{props.regulatoryZoneMetadata.prohibitions ? props.regulatoryZoneMetadata.prohibitions : <NoValue>-</NoValue>} </ValueWithLineBreak>
                                <KeyWithLineBreak>Références réglementaires</KeyWithLineBreak>
                                <ValueWithLineBreak>{props.regulatoryZoneMetadata.regulatoryReferences ? props.regulatoryZoneMetadata.regulatoryReferences : <NoValue>-</NoValue>} </ValueWithLineBreak>
                            </ZoneWithLineBreak>
                        </Content>
                    </> : <FingerprintSpinner color={COLORS.background} className={'radar'} size={100}/>
            }
        </Wrapper>
    )
}

const RegulatoryName = styled.span`
    display: inline-flex;
    padding: unset;
    margin: unset;
    line-height: initial;
`

const Ellipsis = styled.span`
    max-width: 176px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
`

const Header = styled.div`
  color: ${COLORS.grayDarkerThree};
  margin-left: 6px;
  text-align: left;
  height: 1.5em;
`

const Content = styled.div`
  border-radius: 1px;
  color: ${COLORS.grayDarker};
  background: ${COLORS.background};
  margin-top: 6px;
  min-height: 480px;
  overflow-y: auto;
  max-height: 750px;
`

const Title = styled.span`
  margin-top: 2px;
  margin-left: 12px;
  vertical-align: top;
  display: inline-block;
  font-size: 13px;
}
`

const REGPaperIcon = styled(REGPaperSVG)`
  width: 20px;
`

const CloseIcon = styled(CloseIconSVG)`
  width: 10px;
  float: right;
  margin-right: 7px;
  margin-top: 5px;
  cursor: pointer;
`

const Body = styled.tbody``

const Zone = styled.div`
  margin: 0;
  padding: 10px 5px 9px 16px;
  text-align: left;
  display: flex;
  flex-wrap: wrap;
  border-bottom: 1px solid ${COLORS.grayDarker};
`

const ZoneWithLineBreak = styled.div`
  margin: 0;
  padding: 10px 5px 9px 16px;
  text-align: left;
  display: block;
  border-bottom: 1px solid ${COLORS.grayDarker};
`

const Fields = styled.table`
  width: inherit;
  display: table;
  margin: 0;
  min-width: 40%;
  line-height: 0.2em;
  padding: unset;
`

const Field = styled.tr`
  margin: 5px 5px 5px 0;
  border: none;
  background: none;
  line-height: 0.5em;
`

const KeyWithLineBreak = styled.div`
  color: ${COLORS.grayDarkerTwo};
  flex: initial;
  display: inline-block;
  margin: 0;
  border: none;
  padding: 6px 10px 5px 0;
  background: none;
  width: max-content;
  line-height: 0.5em;
  height: 0.5em;
  font-size: 13px;
  font-weight: 400;
`

const ValueWithLineBreak = styled.div`
  color: ${COLORS.grayDarkerThree};
  padding: 2px 5px 5px 0;
  line-height: normal;
  font-size: 13px;
`

const Key = styled.th`
  color: ${COLORS.grayDarkerTwo};
  flex: initial;
  display: inline-block;
  margin: 0;
  border: none;
  padding: 6px 10px 5px 0;
  background: none;
  width: max-content;
  line-height: 0.5em;
  height: 0.5em;
  font-size: 13px;
  font-weight: 400;
`

const Value = styled.td`
  color: ${COLORS.grayDarkerThree};
  margin: 0;
  text-align: left;
  padding: 1px 5px 5px 5px;
  background: none;
  border: none;
  line-height: normal;
  font-size: 13px;
`

const NoValue = styled.span`
  color: ${COLORS.textBueGray};
  font-weight: 300;
  line-height: normal;
  font-size: 13px;
  display: block;
`

const Wrapper = styled.div`
    border-radius: 1px;
    width: 350px;
    position: absolute;
    display: block;
    color: ${COLORS.grayDarkerThree};
    text-decoration: none;
    background-color: ${COLORS.gray};
    padding: 0;
    margin-left: -30px;
    margin-top: 45px;
    top: 0px;
    opacity: 0;
    z-index: -1;
    min-height: 300px;
    max-height: calc(100vh - 50px);
    padding: 10px;
    
    animation: ${props => props.firstUpdate && !props.openBox ? '' : props.openBox ? 'regulatory-metadata-box-opening' : 'regulatory-metadata-box-closing'} 0.5s ease forwards;
    
    @keyframes regulatory-metadata-box-opening {
        0%   { min-height: 200px; opacity: 0; margin-left: -30px;   }
        100% { min-height: 500px; opacity: 1; margin-left: 360px; }
    }
    
    @keyframes regulatory-metadata-box-closing {
        0% { min-height: 500px; opacity: 1; margin-left: 360px; }
        100%   { min-height: 200px; opacity: 0; margin-left: -30px;   }
    }
`

export default RegulatoryZoneMetadata
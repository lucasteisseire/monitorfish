import React, {useEffect, useState} from "react";
import styled from "styled-components";
import {COLORS} from "../../constants/constants";
import {getCoordinates, getDateTime} from "../../utils";
import {WSG84_PROJECTION} from "../../domain/entities/map";
import ERSMessageSpecies from "./ERSMessageSpecies";
import {buildCatchArray} from "../../domain/entities/ERS";

const DISMessage = props => {
    const [catches, setCatches] = useState([])

    useEffect(() => {
        if (props.message && props.message.catches) {
            let catches = buildCatchArray(props.message.catches)

            setCatches(catches)
        } else {
            setCatches([])
        }
    }, [props.message])

    return <>
        { props.message ?
            <>
                <Zone>
                    <Fields>
                        <TableBody>
                            <Field>
                                <Key>Date opération</Key>
                                <Value>{props.message.discardDatetimeUtc ? <>{getDateTime(props.message.discardDatetimeUtc, true)} <Gray>(UTC)</Gray></> : <NoValue>-</NoValue>}</Value>
                            </Field>
                            <Field>
                                <Key>Position opération</Key>
                                <Value>
                                    <FirstInlineKey>Lat.</FirstInlineKey> { props.message.latitude && props.message.longitude ?
                                    getCoordinates([props.message.latitude, props.message.longitude], WSG84_PROJECTION)[0] :
                                    <NoValue>-</NoValue> }
                                    <InlineKey>Lon.</InlineKey> { props.message.latitude && props.message.longitude ?
                                    getCoordinates([props.message.latitude, props.message.longitude], WSG84_PROJECTION)[1] :
                                    <NoValue>-</NoValue>}
                                </Value>
                            </Field>
                        </TableBody>
                    </Fields>
                </Zone>
                <SpeciesList>
                    {
                        catches.map((speciesCatch, index) => {
                            return <ERSMessageSpecies
                                index={index + 1}
                                hasManyProperties={speciesCatch.properties.length > 1}
                                isLast={catches.length === index + 1}
                                species={speciesCatch}
                                key={'FAR' + speciesCatch.species}
                            />
                        })
                    }
                </SpeciesList>
            </> : null }
    </>
}


const FirstInlineKey = styled.div`
  color: ${COLORS.textGray};
  display: inline-block;
  padding: 0px 5px 0px 0;
  font-size: 13px;
`
const Gray = styled.span`
  color: ${COLORS.grayDarkerThree};
  font-weight: 300;
`

const SpeciesList = styled.ul`
  margin: 10px 0 0 0;
  padding: 0;
  width: -moz-available;
`

const TableBody = styled.tbody``

const Zone = styled.div`
  padding: 5px 10px 0px 10px;
  margin-top: 10px;
  text-align: left;
  display: flex;
  flex-wrap: wrap;
  background: ${COLORS.background};
`

const Fields = styled.table`
  padding: 0px 5px 0 5px; 
  width: inherit;
  display: table;
  margin: 0;
  min-width: 40%;
  line-height: 0.2em;
  margin-top: 5px;
  margin-bottom: 5px;
`

const Field = styled.tr`
  margin: 5px 5px 0 0;
  border: none;
  background: none;
  line-height: 0.5em;
`

const InlineKey = styled.div`
  color: ${COLORS.textGray};
  display: inline-block;
  padding: 0px 5px 0px 10px;
  font-size: 13px;
`

const Key = styled.th`
  color: ${COLORS.textGray};
  flex: initial;
  display: inline-block;
  margin: 0;
  border: none;
  padding: 5px 5px 5px 0;
  background: none;
  width: max-content;
  line-height: 0.5em;
  height: 0.5em;
  font-size: 13px;
  font-weight: normal;
`

const Value = styled.td`
  font-size: 13px;
  color: ${COLORS.grayDarkerThree};
  margin: 0;
  text-align: left;
  padding: 1px 5px 5px 5px;
  background: none;
  border: none;
  line-height: normal;
`

const NoValue = styled.span`
  color: ${COLORS.grayDarkerTwo};
  font-weight: 300;
  line-height: normal;
`

export default DISMessage
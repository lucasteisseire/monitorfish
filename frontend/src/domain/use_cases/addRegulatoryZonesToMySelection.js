import {addRegulatoryZonesToSelection} from "../reducers/Regulatory";

const addRegulatoryZonesToMySelection = regulatoryZones => (dispatch, getState) => {
    let regulatoryZonesToAdd = {...getState().regulatory.selectedRegulatoryZones}

    Object.keys(regulatoryZones).forEach(regulatoryZoneName => {
        if(!regulatoryZonesToAdd[regulatoryZoneName] || !regulatoryZonesToAdd[regulatoryZoneName].length) {
            regulatoryZonesToAdd[regulatoryZoneName] = regulatoryZones[regulatoryZoneName]
        } else {
            regulatoryZones[regulatoryZoneName].forEach(regulatorySubZone => {
                if(!regulatoryZonesToAdd[regulatoryZoneName].some(item =>
                    item.layerName === regulatorySubZone.layerName &&
                    item.zone === regulatorySubZone.zone)) {
                    regulatoryZonesToAdd[regulatoryZoneName] = regulatoryZonesToAdd[regulatoryZoneName].concat(regulatorySubZone)
                }
            })
        }
    })

    dispatch(addRegulatoryZonesToSelection(regulatoryZonesToAdd))
}

export default addRegulatoryZonesToMySelection
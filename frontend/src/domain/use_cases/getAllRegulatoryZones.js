import {getAllRegulatoryZonesFromAPI} from "../../api/fetch";
import * as Comlink from 'comlink'
/* eslint-disable import/no-webpack-loader-syntax */
import Worker from 'worker-loader!../../workers/MapperWorker';
import {setError} from "../reducers/Global";

const worker = new Worker();
const MapperWorker = Comlink.wrap(worker);

const getAllRegulatoryZones = (dispatch) => async () => {
    const worker = await new MapperWorker()

    return getAllRegulatoryZonesFromAPI()
        .then(features => {
            return worker.convertGeoJSONFeaturesToObject(features)
        }).catch(error => {
            dispatch(setError(error));
        });
}

export default getAllRegulatoryZones
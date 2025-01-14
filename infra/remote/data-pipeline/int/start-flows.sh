#!/bin/bash

docker run -d -t --network=host --name monitorfish-pipeline-flows \
        -v prefect_flows:/home/monitorfish-pipeline/.prefect \
        -u monitorfish-pipeline:"$(getent group di_etlmf | cut -d: -f3)" \
        -v /opt2/monitorfish-data/ers:/opt2/monitorfish-data/ers \
        --env-file datascience/.env \
        --restart always \
        docker.pkg.github.com/mtes-mct/monitorfish/monitorfish-pipeline:$MONITORFISH_VERSION \
        python main.py

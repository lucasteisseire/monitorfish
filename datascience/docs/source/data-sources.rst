External data sources
=====================

VMS positions
^^^^^^^^^^^^^

VMS positions are received on an API endpoint provided by the Kotlin Springboot backend service.

ERS xml files
^^^^^^^^^^^^^

ERS raw xml files are ingested by the :doc:`ers` flow from the 
`configured location <https://github.com/MTES-MCT/monitorfish/blob/master/datascience/config.py>`__ 
where ERS xml files must be deposited.

Databases
^^^^^^^^^

Data is imported (and constantly updated) from external databases for :doc:`flows/controls`, :doc:`flows/controllers`, :doc:`flows/fishing-gears` and :doc:`flows/vessels`.

These databases are :

* OCAN
* FMC2

Credentials for these data sources must be configured for Monitorfish to connect to them. See :ref:`environment_variables`.

DataSources
^^^^^^^^^^^
+--------------------+----------------+-------------+------------------------------------------------------------------------------------------+-------------+---------------+-------------------------------+-----------------------------------------------------------------------+
| Donnée             | Format/support | Responsable | Source                                                                                   | Destination | Fréquence MAJ | Remarque                      | Lien documentation                                                    |
+--------------------+----------------+-------------+------------------------------------------------------------------------------------------+-------------+---------------+-------------------------------+-----------------------------------------------------------------------+
| Fao Areas          | file           | FAO         | http://www.fao.org/geonetwork/srv/en/main.home?uuid=ac02a460-da52-11dc-9d70-0017f293bd28 |             |               | Périmètres réglementaires?    |                                                                       |
| EEZ                | file           |             | https://www.marineregions.org/downloads.php#eez                                          |             |               |                               |                                                                       |
| control units      | ?              | FMC         | FMC2                                                                                     |             | day           |                               |                                                                       |
| controls           | ?              | FMC         | FMC2                                                                                     |             | 10 min        |                               |                                                                       |
| infractions        | ?              | FMC         | FMC2                                                                                     |             | day           |                               |                                                                       |
| ERS                | XML            | BIA/DAM SI  | ?                                                                                        |             |               | Journal de bord de pêche ERS  |                                                                       |
| Façade_areas       | postgis        | CROSSA      |                                                                                          |             |               |                               |                                                                       |
| Positions          | API            | POSEIDON ?  | POSEIDON                                                                                 |             |               | quelle source de la position? |                                                                       |
| Ports              | file ?         | ?           | data.gouv.fr                                                                             |             | manual        |                               |                                                                       |
| Vessels            |                |             | OCAN                                                                                     |             | day           | quelle source de la position? |                                                                       |
| fishing_gear_codes |                |             |                                                                                          |             |               | ?                             | https://monitorfish.readthedocs.io/en/latest/flows/fishing-gears.html |
| regulations        | postgis        | CROSSA      | postgis CROSSA                                                                           |             |               |                               |                                                                       |
| Legipeche          | web            | CNSP        | legipeche.metier.i2                                                                      |             |               | scrapping                     |                                                                       |
| species            |                |             | data.gouv.fr                                                                             |             | manual        |                               |                                                                       |
+--------------------+----------------+-------------+------------------------------------------------------------------------------------------+-------------+---------------+-------------------------------+-----------------------------------------------------------------------+
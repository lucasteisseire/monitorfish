��    	      d               �   �   �   #  ?     c  m  i     �  +   �  &        8  �  H  �   2  8  �       �       �	  6   �	  -   .
     \
   *Flows* are batch jobs that move and transform data. Collectively, they constitute the :ref:`data pipeline` part of the Monitorfish architecture. Each batch job is written as a `Prefect flow <https://docs.prefect.io/core/concepts/flows.html#overview>`__ which typically extracts data  (from external sources and / or from tables in the Monitorfish database), processes the data and loads it back into a table of the Monitorfish database. Flows Flows are composed of `tasks <https://docs.prefect.io/core/concepts/tasks.html#overview>`__ typically written as python pure functions. `The UI <http://prefect.csam.e2.rie.gouv.fr/>`__ (restricted access) enables administrators to view each flow as a diagram of its constituent tasks, to monitor their execution, see the logs and debug in case any flow run fails... List of flows Overall view of data flows in Monitorfish : Schematic of data flows in Monitorfish What are flows? Project-Id-Version:  Monitorfish
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2021-08-24 17:06+0200
PO-Revision-Date: 2021-08-23 14:48+0000
Last-Translator: Vincent Chéry <vincent.chery@m4x.org>, 2021
Language: fr
Language-Team: French (https://www.transifex.com/ministere-de-la-transition-ecologique-et-solidaire-1/teams/124045/fr/)
Plural-Forms: nplurals=2; plural=(n > 1)
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit
Generated-By: Babel 2.9.0
 Les *flows* sont des traitements qui déplacent et transforment les données. Collectivement, ils constituent la partie :ref:`data pipeline` de l'architecture Monitorfish. Chaque traitement est écrit comme un `Flow Prefect <https://docs.prefect.io/core/concepts/flows.html#overview>`__ qui extrait typiquement des données (de sources externes et/ou de tables de la base de données Monitorfish), traite les données et les recharge dans une table de la base de données Monitorfish. Flows Les flows sont composés de `tâches <https://docs.prefect.io/core/concepts/tasks.html#overview>`__ typiquement écrites comme des fonctions pures en python. `L'interface utilisateur <http://prefect.csam.e2.rie.gouv.fr/>`__ (accès restreint) permet aux administrateurs de visualiser chaque flow sous la forme d'un diagramme des tâches qui le composent, de suivre leur exécution, de voir les logs, de déboguer en cas d'échec de l'exécution d'un flow... Liste des flows Vue d'ensemble des flux de données dans Monitorfish : Schéma des flux de données dans Monitorfish Que sont les flows ? 
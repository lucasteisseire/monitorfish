/**
 * @typedef VesselVoyage
 * @property {boolean} isLastVoyage
 * @property {string | null} previousBeforeDateTime
 * @property {string | null} nextBeforeDateTime
 * @property {FishingActivities} ersMessagesAndAlerts
 */

/**
 * @typedef FishingActivities
 * @property {Alert[]} alerts
 * @property {ERSMessage[]} ersMessages
 */

/**
 * @typedef Alert
 * @property {string} creationDate
 * @property {string} externalReferenceNumber
 * @property {string} id
 * @property {string} internalReferenceNumber
 * @property {string} ircs
 * @property {string} name
 * @property {number} tripNumber
 * @property {{name: string}} value
 */

/**
 * @typedef ERSMessage
 * @property {{
        isSuccess: boolean,
        rejectionCause: string,
        returnStatus: string
      }} acknowledge
 * @property {boolean} deleted
 * @property {string} ersId
 * @property {string} externalReferenceNumber
 * @property {string} flagState
 * @property {string} imo
 * @property {string} internalReferenceNumber
 * @property {string} ircs
 * @property {boolean} isCorrected
 * @property {string} message
 * @property {string} messageType
 * @property {string} operationDateTime
 * @property {string} operationNumber
 * @property {string} operationType
 * @property {string} rawMessage
 * @property {string} referencedErsId
 * @property {number} tripNumber
 * @property {string} vesselName
 */
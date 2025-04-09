/**
 * @description :class:`Mandate <Mandate>` A funding mandate for a given year\n\n:param agency: name of the funding agency\n:param url_policy: url of the policy for this mandate\n:param url_policy_cached: url of the policy cached by Google Scholar\n:param effective_date: date from which the policy is effective\n:param embargo: period within which the article must be publicly available\n:param acknowledgement: text in the paper acknowledging the funding\n:param grant: grant ID that supported this work
 */
export type Mandate = {
  /**
   * @type string | undefined
   */
  agency?: string
  /**
   * @type string | undefined
   */
  urlPolicy?: string
  /**
   * @type string | undefined
   */
  urlPolicyCached?: string
  /**
   * @type string | undefined
   */
  effectiveDate?: string
  /**
   * @type string | undefined
   */
  embargo?: string
  /**
   * @type string | undefined
   */
  acknowledgement?: string
  /**
   * @type string | undefined
   */
  grant?: string
}
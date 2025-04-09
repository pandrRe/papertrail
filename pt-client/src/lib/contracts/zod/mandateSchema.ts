import { z } from 'zod'

/**
 * @description :class:`Mandate <Mandate>` A funding mandate for a given year\n\n:param agency: name of the funding agency\n:param url_policy: url of the policy for this mandate\n:param url_policy_cached: url of the policy cached by Google Scholar\n:param effective_date: date from which the policy is effective\n:param embargo: period within which the article must be publicly available\n:param acknowledgement: text in the paper acknowledging the funding\n:param grant: grant ID that supported this work
 */
export const mandateSchema = z
  .object({
    agency: z.string().optional(),
    urlPolicy: z.string().optional(),
    urlPolicyCached: z.string().optional(),
    effectiveDate: z.string().optional(),
    embargo: z.string().optional(),
    acknowledgement: z.string().optional(),
    grant: z.string().optional(),
  })
  .describe(
    ':class:`Mandate <Mandate>` A funding mandate for a given year\n\n:param agency: name of the funding agency\n:param url_policy: url of the policy for this mandate\n:param url_policy_cached: url of the policy cached by Google Scholar\n:param effective_date: date from which the policy is effective\n:param embargo: period within which the article must be publicly available\n:param acknowledgement: text in the paper acknowledging the funding\n:param grant: grant ID that supported this work',
  )

export type MandateSchema = z.infer<typeof mandateSchema>
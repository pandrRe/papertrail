import { extendedAuthorSchema } from './extendedAuthorSchema.ts'
import { z } from 'zod'

export const streamUpdateAuthorSchema = z.object({
  type: z.literal('update:author').default('update:author'),
  payload: z.lazy(() => extendedAuthorSchema),
})

export type StreamUpdateAuthorSchema = z.infer<typeof streamUpdateAuthorSchema>
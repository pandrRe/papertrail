import { extendedAuthorSchema } from './extendedAuthorSchema.ts'
import { z } from 'zod'

export const streamSetAuthorListSchema = z.object({
  type: z.literal('set:author:list').default('set:author:list'),
  payload: z.array(z.lazy(() => extendedAuthorSchema)),
})

export type StreamSetAuthorListSchema = z.infer<typeof streamSetAuthorListSchema>
import { publicationSchema } from './publicationSchema.ts'
import { z } from 'zod'

export const streamSetPublicationListSchema = z.object({
  type: z.literal('set:publication:list').default('set:publication:list'),
  payload: z.array(z.lazy(() => publicationSchema)),
})

export type StreamSetPublicationListSchema = z.infer<typeof streamSetPublicationListSchema>
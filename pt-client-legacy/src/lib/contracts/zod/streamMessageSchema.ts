import { streamSetAuthorListSchema } from './streamSetAuthorListSchema.ts'
import { streamSetPublicationListSchema } from './streamSetPublicationListSchema.ts'
import { streamUpdateAuthorSchema } from './streamUpdateAuthorSchema.ts'
import { z } from 'zod'

export const streamMessageSchema = z.object({
  event: z.string(),
  data: z.union([z.lazy(() => streamSetAuthorListSchema), z.lazy(() => streamSetPublicationListSchema), z.lazy(() => streamUpdateAuthorSchema), z.null()]),
})

export type StreamMessageSchema = z.infer<typeof streamMessageSchema>
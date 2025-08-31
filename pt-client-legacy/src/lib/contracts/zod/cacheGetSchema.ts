import { HTTPValidationErrorSchema } from './HTTPValidationErrorSchema.ts'
import { streamSetAuthorListSchema } from './streamSetAuthorListSchema.ts'
import { streamSetPublicationListSchema } from './streamSetPublicationListSchema.ts'
import { streamUpdateAuthorSchema } from './streamUpdateAuthorSchema.ts'
import { z } from 'zod'

export const cacheGetPathParamsSchema = z.object({
  scope: z.string(),
  key: z.string(),
})

export type CacheGetPathParamsSchema = z.infer<typeof cacheGetPathParamsSchema>

/**
 * @description Successful Response
 */
export const cacheGet200Schema = z.union([
  z.lazy(() => streamSetAuthorListSchema),
  z.lazy(() => streamSetPublicationListSchema),
  z.lazy(() => streamUpdateAuthorSchema),
  z.null(),
])

export type CacheGet200Schema = z.infer<typeof cacheGet200Schema>

/**
 * @description Validation Error
 */
export const cacheGet422Schema = z.lazy(() => HTTPValidationErrorSchema)

export type CacheGet422Schema = z.infer<typeof cacheGet422Schema>

export const cacheGetQueryResponseSchema = z.lazy(() => cacheGet200Schema)

export type CacheGetQueryResponseSchema = z.infer<typeof cacheGetQueryResponseSchema>
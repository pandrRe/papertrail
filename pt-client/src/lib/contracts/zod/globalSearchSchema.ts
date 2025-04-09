import { HTTPValidationErrorSchema } from './HTTPValidationErrorSchema.ts'
import { z } from 'zod'

export const globalSearchQueryParamsSchema = z.object({
  query: z.string(),
})

export type GlobalSearchQueryParamsSchema = z.infer<typeof globalSearchQueryParamsSchema>

/**
 * @description Successful Response
 */
export const globalSearch200Schema = z.unknown()

export type GlobalSearch200Schema = z.infer<typeof globalSearch200Schema>

/**
 * @description Validation Error
 */
export const globalSearch422Schema = z.lazy(() => HTTPValidationErrorSchema)

export type GlobalSearch422Schema = z.infer<typeof globalSearch422Schema>

export const globalSearchQueryResponseSchema = z.lazy(() => globalSearch200Schema)

export type GlobalSearchQueryResponseSchema = z.infer<typeof globalSearchQueryResponseSchema>
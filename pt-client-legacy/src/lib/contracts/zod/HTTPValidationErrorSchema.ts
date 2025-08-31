import { validationErrorSchema } from './validationErrorSchema.ts'
import { z } from 'zod'

export const HTTPValidationErrorSchema = z.object({
  detail: z.array(z.lazy(() => validationErrorSchema)).optional(),
})

export type HTTPValidationErrorSchema = z.infer<typeof HTTPValidationErrorSchema>
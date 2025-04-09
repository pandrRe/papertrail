import { z } from 'zod'

export const validationErrorSchema = z.object({
  loc: z.array(z.union([z.number().int(), z.string()])),
  msg: z.string(),
  type: z.string(),
})

export type ValidationErrorSchema = z.infer<typeof validationErrorSchema>
import { z } from 'zod'

export const publicAccessSchema = z.object({
  available: z.number().int(),
  notAvailable: z.number().int(),
})

export type PublicAccessSchema = z.infer<typeof publicAccessSchema>
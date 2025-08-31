import { streamMessageSchema } from './streamMessageSchema.ts'
import { z } from 'zod'

/**
 * @description Successful Response
 */
export const exposeStreamMessage200Schema = z.union([z.lazy(() => streamMessageSchema), z.null()])

export type ExposeStreamMessage200Schema = z.infer<typeof exposeStreamMessage200Schema>

export const exposeStreamMessageQueryResponseSchema = z.lazy(() => exposeStreamMessage200Schema)

export type ExposeStreamMessageQueryResponseSchema = z.infer<typeof exposeStreamMessageQueryResponseSchema>
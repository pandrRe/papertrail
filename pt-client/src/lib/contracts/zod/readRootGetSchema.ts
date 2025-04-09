import { z } from 'zod'

/**
 * @description Successful Response
 */
export const readRootGet200Schema = z.unknown()

export type ReadRootGet200Schema = z.infer<typeof readRootGet200Schema>

export const readRootGetQueryResponseSchema = z.lazy(() => readRootGet200Schema)

export type ReadRootGetQueryResponseSchema = z.infer<typeof readRootGetQueryResponseSchema>
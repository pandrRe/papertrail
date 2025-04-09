import type { StreamMessage } from './StreamMessage.ts'

/**
 * @description Successful Response
 */
export type ExposeStreamMessage200 = StreamMessage | null

export type ExposeStreamMessageQueryResponse = ExposeStreamMessage200

export type ExposeStreamMessageQuery = {
  Response: ExposeStreamMessage200
  Errors: any
}
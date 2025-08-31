import type { Publication } from './Publication.ts'

export type StreamSetPublicationList = {
  /**
   * @default "set:publication:list"
   * @type string | undefined
   */
  type?: 'set:publication:list'
  /**
   * @type array
   */
  payload: Publication[]
}
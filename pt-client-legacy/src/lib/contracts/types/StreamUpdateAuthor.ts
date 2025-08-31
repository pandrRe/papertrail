import type { ExtendedAuthor } from './ExtendedAuthor.ts'

export type StreamUpdateAuthor = {
  /**
   * @default "update:author"
   * @type string | undefined
   */
  type?: 'update:author'
  /**
   * @type object
   */
  payload: ExtendedAuthor
}
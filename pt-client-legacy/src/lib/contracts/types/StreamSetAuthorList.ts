import type { ExtendedAuthor } from './ExtendedAuthor.ts'

export type StreamSetAuthorList = {
  /**
   * @default "set:author:list"
   * @type string | undefined
   */
  type?: 'set:author:list'
  /**
   * @type array
   */
  payload: ExtendedAuthor[]
}
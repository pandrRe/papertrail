import type { AuthorSource } from './AuthorSource.ts'
import type { PublicAccess } from './PublicAccess.ts'
import type { Publication } from './Publication.ts'

export type ExtendedAuthor = {
  /**
   * @type string | undefined
   */
  scholarId?: string
  /**
   * @type string | undefined
   */
  name?: string
  /**
   * @type string | undefined
   */
  affiliation?: string
  /**
   * @type integer | undefined
   */
  organization?: number
  /**
   * @type string | undefined
   */
  emailDomain?: string
  /**
   * @type string | undefined
   */
  urlPicture?: string
  /**
   * @type string | undefined
   */
  homepage?: string
  /**
   * @type integer | undefined
   */
  citedby?: number
  /**
   * @type array | undefined
   */
  filled?: string[]
  /**
   * @type array | undefined
   */
  interests?: string[]
  /**
   * @type integer | undefined
   */
  citedby5Y?: number
  /**
   * @type integer | undefined
   */
  hindex?: number
  /**
   * @type integer | undefined
   */
  hindex5Y?: number
  /**
   * @type integer | undefined
   */
  i10Index?: number
  /**
   * @type integer | undefined
   */
  i10Index5Y?: number
  /**
   * @type object | undefined
   */
  citesPerYear?: {
    [key: string]: number
  }
  /**
   * @type object | undefined
   */
  publicAccess?: PublicAccess
  /**
   * @type array | undefined
   */
  publications?: Publication[]
  /**
   * @type array | undefined
   */
  coauthors?: any[]
  /**
   * @type string | undefined
   */
  containerType?: string
  /**
   * @type string | undefined
   */
  source?: AuthorSource
  summary?: string | null
}
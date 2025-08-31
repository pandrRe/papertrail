import type { HTTPValidationError } from './HTTPValidationError.ts'
import type { StreamSetAuthorList } from './StreamSetAuthorList.ts'
import type { StreamSetPublicationList } from './StreamSetPublicationList.ts'
import type { StreamUpdateAuthor } from './StreamUpdateAuthor.ts'

export type CacheGetPathParams = {
  /**
   * @type string
   */
  scope: string
  /**
   * @type string
   */
  key: string
}

/**
 * @description Successful Response
 */
export type CacheGet200 = StreamSetAuthorList | StreamSetPublicationList | StreamUpdateAuthor | null

/**
 * @description Validation Error
 */
export type CacheGet422 = HTTPValidationError

export type CacheGetQueryResponse = CacheGet200

export type CacheGetQuery = {
  Response: CacheGet200
  PathParams: CacheGetPathParams
  Errors: CacheGet422
}
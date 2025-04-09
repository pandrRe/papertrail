import type { HTTPValidationError } from './HTTPValidationError.ts'

export type GlobalSearchQueryParams = {
  /**
   * @type string
   */
  query: string
}

/**
 * @description Successful Response
 */
export type GlobalSearch200 = any

/**
 * @description Validation Error
 */
export type GlobalSearch422 = HTTPValidationError

export type GlobalSearchQueryResponse = GlobalSearch200

export type GlobalSearchQuery = {
  Response: GlobalSearch200
  QueryParams: GlobalSearchQueryParams
  Errors: GlobalSearch422
}
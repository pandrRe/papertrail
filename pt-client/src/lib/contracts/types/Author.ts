import type { AuthorSource } from './AuthorSource.ts'
import type { PublicAccess } from './PublicAccess.ts'
import type { Publication } from './Publication.ts'

/**
 * @description :class:`Author <Author>` object used to represent an author entry on Google Scholar.\n       (When source is not specified, the field is present in all sources)\n\n:param scholar_id: The id of the author on Google Scholar\n:param name: The name of the author\n:param affiliation: The affiliation of the author\n:param organization: A unique ID of the organization (source: AUTHOR_PROFILE_PAGE)\n:param email_domain: The email domain of the author (source: SEARCH_AUTHOR_SNIPPETS, AUTHOR_PROFILE_PAGE)\n:param url_picture: The URL for the picture of the author\n:param homepage: URL of the homepage of the author\n:param citedby: The number of citations to all publications. (source: SEARCH_AUTHOR_SNIPPETS)\n:param filled: The list of sections filled out of the total set of sections that can be filled\n:param interests: Fields of interest of this Author (sources: SEARCH_AUTHOR_SNIPPETS, AUTHOR_PROFILE_PAGE)\n:param citedby5y: The number of new citations in the last 5 years to all publications. (source: SEARCH_AUTHOR_SNIPPETS)\n:param hindex: The h-index is the largest number h such that h publications have at least h citations. (source: SEARCH_AUTHOR_SNIPPETS)\n:param hindex5y: The largest number h such that h publications have at least h new citations in the last 5 years. (source: SEARCH_AUTHOR_SNIPPETS)\n:param i10index: This is the number of publications with at least 10 citations.  (source: SEARCH_AUTHOR_SNIPPETS)\n:param i10index5y: The number of publications that have received at least 10 new citations in the last 5 years. (source: SEARCH_AUTHOR_SNIPPETS)\n:param cites_per_year: Breakdown of the number of citations to all publications over the years (source: SEARCH_AUTHOR_SNIPPETS)\n:param public_access: Number of articles that are available and not available in accordance with public access mandates. (source: SEARCH_AUTHOR_SNIPPETS, AUTHOR_PROFILE_PAGE)\n:param publications: A list of publications objects. (source: SEARCH_AUTHOR_SNIPPETS)\n:param coauthors: A list of coauthors (list of Author objects) (source: SEARCH_AUTHOR_SNIPPETS)\n:param container_type: Used from the source code to identify if this container object\n                       is an Author or a Publication object.\n:param source: The place where the author information are derived
 */
export type Author = {
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
}
import type { BibEntry } from './BibEntry.ts'
import type { Mandate } from './Mandate.ts'
import type { PublicationSource } from './PublicationSource.ts'

/**
 * @description :class:`Publication <Publication>` object used to represent a publication entry on Google Scholar.\n       (When source is not specified, the field is present in all sources)\n\n:param BibEntryCitation: contains additional information about the publication\n:param gsrank: position of the publication in the query (source: PUBLICATION_SEARCH_SNIPPET)\n:param author_id: list of the corresponding author ids of the authors that contributed to the Publication (source: PUBLICATION_SEARCH_SNIPPET)\n:param num_citations: number of citations of this Publication\n:param cites_id: This corresponds to a \"single\" publication on Google Scholar. Used in the web search\n                   request to return all the papers that cite the publication. If cites_id =\n                   16766804411681372720 then:\n                   https://scholar.google.com/scholar?cites=<cites_id>&hl=en\n                   If the publication comes from a \"merged\" list of papers from an authors page,\n                   the \"citedby_id\" will be a comma-separated list of values.\n                   It is also used to return the \"cluster\" of all the different versions of the paper.\n                   https://scholar.google.com/scholar?cluster=16766804411681372720&hl=en\n                   (source: AUTHOR_PUBLICATION_ENTRY)\n:param citedby_url: This corresponds to a \"single\" publication on Google Scholar. Used in the web search\n                   request to return all the papers that cite the publication.\n                   https://scholar.google.com/scholar?cites=16766804411681372720hl=en\n                   If the publication comes from a \"merged\" list of papers from an authors page,\n                   the \"citedby_url\" will be a comma-separated list of values.\n                   It is also used to return the \"cluster\" of all the different versions of the paper.\n                   https://scholar.google.com/scholar?cluster=16766804411681372720&hl=en\n:param cites_per_year: a dictionay containing the number of citations per year for this Publication\n                       (source: AUTHOR_PUBLICATION_ENTRY)\n:param eprint_url: digital version of the Publication. Usually it is a pdf.\n:param pub_url: url of the website providing the publication\n:param author_pub_id: The id of the paper on Google Scholar from an author page. Comes from the\n                      parameter \"citation_for_view=PA9La6oAAAAJ:YsMSGLbcyi4C\". It combines the\n                      author id, together with a publication id. It may corresponds to a merging\n                      of multiple publications, and therefore may have multiple \"citedby_id\"\n                      values.\n                      (source: AUTHOR_PUBLICATION_ENTRY)\n:param public_access: Boolean corresponding to whether the article is available or not in accordance with public access mandates.\n:param mandates: List of mandates with funding information and public access requirements.\n:param url_related_articles: the url containing link for related articles of a publication (needs fill() for AUTHOR_PUBLICATION_ENTRIES)\n:param url_add_sclib: (source: PUBLICATION_SEARCH_SNIPPET)\n:param url_scholarbib: the url containing links for\n                       the BibTeX entry, EndNote, RefMan and RefWorks (source: PUBLICATION_SEARCH_SNIPPET)\n:param filled: whether the publication is fully filled or not\n:param source: The source of the publication entry\n:param container_type: Used from the source code to identify if this container object\n                       is an Author or a Publication object.
 */
export type Publication = {
  /**
   * @type object | undefined
   */
  bib?: BibEntry
  /**
   * @type integer | undefined
   */
  gsrank?: number
  /**
   * @type array | undefined
   */
  authorId?: string[]
  /**
   * @type integer | undefined
   */
  numCitations?: number
  /**
   * @type array | undefined
   */
  citesId?: string[]
  /**
   * @type string | undefined
   */
  citedbyUrl?: string
  /**
   * @type object | undefined
   */
  citesPerYear?: {
    [key: string]: number
  }
  /**
   * @type string | undefined
   */
  authorPubId?: string
  /**
   * @type boolean | undefined
   */
  publicAccess?: boolean
  /**
   * @type array | undefined
   */
  mandates?: Mandate[]
  /**
   * @type string | undefined
   */
  eprintUrl?: string
  /**
   * @type string | undefined
   */
  pubUrl?: string
  /**
   * @type string | undefined
   */
  urlAddSclib?: string
  /**
   * @type string | undefined
   */
  urlRelatedArticles?: string
  /**
   * @type string | undefined
   */
  urlScholarbib?: string
  /**
   * @type boolean | undefined
   */
  filled?: boolean
  /**
   * @type string | undefined
   */
  source?: PublicationSource
  /**
   * @type string | undefined
   */
  containerType?: string
}
/**
 * @description :class:`BibEntry <BibEntry>` The bibliographic entry for a publication\n        (When source is not specified, the field is present in all sources)\n\n:param pub_type: the type of entry for this bib (for example \'article\') (source: PUBLICATION_SEARCH_SNIPPET)\n:param bib_id: bib entry id (source: PUBLICATION_SEARCH_SNIPPET)\n:param abstract: description of the publication\n:param title: title of the publication\n:param author: list of author the author names that contributed to this publication\n:param pub_year: the year the publication was first published\n:param venue: the venue of the publication (source: PUBLICATION_SEARCH_SNIPPET)\n:param journal: Journal Name\n:param volume: number of years a publication has been circulated\n:param number: NA number of a publication\n:param pages: range of pages\n:param publisher: The publisher\'s name\n:param citation: Formatted citation string, usually containing journal name, volume and page numbers (source: AUTHOR_PUBLICATION_ENTRY)\n:param pub_url: url of the website providing the publication
 */
export type BibEntry = {
  /**
   * @type string | undefined
   */
  pubType?: string
  /**
   * @type string | undefined
   */
  bibId?: string
  /**
   * @type string | undefined
   */
  abstract?: string
  /**
   * @type string | undefined
   */
  title?: string
  author?: string | string[]
  /**
   * @type string | undefined
   */
  pubYear?: string
  /**
   * @type string | undefined
   */
  venue?: string
  /**
   * @type string | undefined
   */
  journal?: string
  /**
   * @type string | undefined
   */
  volume?: string
  /**
   * @type string | undefined
   */
  number?: string
  /**
   * @type string | undefined
   */
  pages?: string
  /**
   * @type string | undefined
   */
  publisher?: string
  /**
   * @type string | undefined
   */
  citation?: string
}
export const authorSourceEnum = {
  AUTHOR_PROFILE_PAGE: 'AUTHOR_PROFILE_PAGE',
  SEARCH_AUTHOR_SNIPPETS: 'SEARCH_AUTHOR_SNIPPETS',
  CO_AUTHORS_LIST: 'CO_AUTHORS_LIST',
} as const

export type AuthorSourceEnum = (typeof authorSourceEnum)[keyof typeof authorSourceEnum]

/**
 * @description Defines the source of the HTML that will be parsed.\n\nAuthor page: https://scholar.google.com/citations?hl=en&user=yxUduqMAAAAJ\n\nSearch authors: https://scholar.google.com/citations?view_op=search_authors&hl=en&mauthors=jordan&btnG=\n\nCoauthors: From the list of co-authors from an Author page
 */
export type AuthorSource = AuthorSourceEnum
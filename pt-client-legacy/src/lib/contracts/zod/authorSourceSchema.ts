import { z } from 'zod'

/**
 * @description Defines the source of the HTML that will be parsed.\n\nAuthor page: https://scholar.google.com/citations?hl=en&user=yxUduqMAAAAJ\n\nSearch authors: https://scholar.google.com/citations?view_op=search_authors&hl=en&mauthors=jordan&btnG=\n\nCoauthors: From the list of co-authors from an Author page
 */
export const authorSourceSchema = z
  .enum(['AUTHOR_PROFILE_PAGE', 'SEARCH_AUTHOR_SNIPPETS', 'CO_AUTHORS_LIST'])
  .describe(
    'Defines the source of the HTML that will be parsed.\n\nAuthor page: https://scholar.google.com/citations?hl=en&user=yxUduqMAAAAJ\n\nSearch authors: https://scholar.google.com/citations?view_op=search_authors&hl=en&mauthors=jordan&btnG=\n\nCoauthors: From the list of co-authors from an Author page',
  )

export type AuthorSourceSchema = z.infer<typeof authorSourceSchema>
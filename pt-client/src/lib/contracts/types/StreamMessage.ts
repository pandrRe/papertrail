import type { StreamSetAuthorList } from './StreamSetAuthorList.ts'
import type { StreamSetPublicationList } from './StreamSetPublicationList.ts'
import type { StreamUpdateAuthor } from './StreamUpdateAuthor.ts'

export type StreamMessage = {
  /**
   * @type string
   */
  event: string
  data: StreamSetAuthorList | StreamSetPublicationList | StreamUpdateAuthor | null
}
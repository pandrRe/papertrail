import { createFileRoute } from "@tanstack/react-router";
import {
  queryOptions,
  experimental_streamedQuery as streamedQuery,
  useQuery,
} from "@tanstack/react-query";
import { useState, useMemo, useEffect } from "react";
import { Search, BookOpen, Book, SearchXIcon, LibraryIcon, IdCardIcon, ExternalLink } from "lucide-react";
import clsx from "clsx";
import * as v from "valibot";
import { Input, InputLayout } from "@/components/ui/input";
// import { api } from "@/lib/api"; // Commented out for native EventSource implementation
import type { AuthorRankingResult } from "#/types";
import { countryCodeToFlagEmoji } from "@/lib/countryCodeToEmoji";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { api } from "@/lib/api";
import type { OrcidRecord } from "#/orcid";

const quotes = [
  { text: "Conhecimento é poder.", author: "Francis Bacon" },
  {
    text: "Nada está no intelecto que não tenha estado primeiro nos sentidos.",
    author: "John Locke",
  },
  {
    text: "O entendimento, como o olho, enquanto nos faz ver e perceber todas as outras coisas, não toma nota de si mesmo.",
    author: "John Locke",
  },
  {
    text: "Pensamentos sem conteúdo são vazios, intuições sem conceitos são cegas.",
    author: "Immanuel Kant",
  },
  {
    text: "Ser é ser percebido.",
    author: "George Berkeley",
  },
  {
    text: "O método da dúvida é o início da filosofia.",
    author: "René Descartes",
  },
  {
    text: "Os limites da minha linguagem significam os limites do meu mundo.",
    author: "Ludwig Wittgenstein",
  },
  {
    text: "A ciência é construída com fatos, como uma casa é construída com pedras. Mas uma coleção de fatos não é mais ciência do que um monte de pedras é uma casa.",
    author: "Henri Poincaré",
  },
  {
    text: "Podemos saber apenas que não sabemos nada. E este é o mais alto grau da sabedoria humana.",
    author: "Leo Tolstoy",
  },
  {
    text: "A vida não examinada não vale a pena ser vivida.",
    author: "Sócrates",
  },
];

function PhilosophyQuote() {
  const randomQuote = useMemo(() => {
    return quotes[Math.floor(Math.random() * quotes.length)];
  }, []);

  return (
    <blockquote className="font-mono text-sm text-left max-w-screen">
      <p className="w-2xl max-w-screen">"{randomQuote.text}"</p>
      <footer className="mt-2 text-muted-foreground">
        — {randomQuote.author}
      </footer>
    </blockquote>
  );
}

function Searching() {
  const [lightPosition, setLightPosition] = useState(0);
  const [direction, setDirection] = useState(1); // 1 for right, -1 for left
  const [isBookOpen, setIsBookOpen] = useState(false);
  const text = "Pesquisando autores relevantes...";

  useEffect(() => {
    const interval = setInterval(() => {
      setLightPosition((prev) => {
        const newPosition = prev + direction;

        // Check if we need to bounce
        if (newPosition >= text.length - 3) {
          setDirection(-1);
          return text.length - 3;
        } else if (newPosition <= 0) {
          setDirection(1);
          return 0;
        }

        return newPosition;
      });
    }, 100);

    return () => clearInterval(interval);
  }, [direction, text.length]);

  useEffect(() => {
    const bookInterval = setInterval(() => {
      setIsBookOpen((prev) => !prev);
    }, 800); // Switch every 800ms

    return () => clearInterval(bookInterval);
  }, []);

  const BookIcon = isBookOpen ? BookOpen : Book;

  return (
    <div className="flex items-center gap-2">
      <BookIcon className="h-4 w-4" />
      <p className="font-mono text-sm">
        {text.split("").map((char, index) => {
          const isHighlighted =
            index >= lightPosition && index < lightPosition + 3;

          return (
            <span
              key={index}
              className={`transition-colors duration-75 ${
                isHighlighted ? "text-foreground-accent" : "text-foreground"
              }`}
            >
              {char}
            </span>
          );
        })}
      </p>
    </div>
  );
}

function ErrorMessage() {
  return (
    <div className="flex items-center gap-2">
      <SearchXIcon className="h-4 w-4 text-red-400" />
      <p className="font-mono text-sm">Ocorreu um erro ao buscar os autores.</p>
    </div>
  );
}

type InstitutionDisplayProps = {
  institutions: AuthorRankingResult["latest_institutions"];
};
function InstitutionDisplay({ institutions }: InstitutionDisplayProps) {
  // Display the first institution (most recent)
  const institution = institutions.at(0);
  if (!institution) {
    return <span>Instituição desconhecida</span>;
  }
  
  return (
    <span className="text-sm flex items-center gap-1.5 leading-none">
      <span>{institution.display_name}</span>
      <span className="text-sm">
        {institution.country_code
          ? countryCodeToFlagEmoji(institution.country_code)
          : null}
      </span>
    </span>
  );
}

interface CollapsibleParagraphProps {
  children?: React.ReactNode;
}

function CollapsibleParagraph({ children }: CollapsibleParagraphProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!children) {
    return <p className="text-muted-foreground">...</p>;
  }

  return (
    <div
      role="button"
      onClick={() => {
        if (!isExpanded) { setIsExpanded(true); }
      }}
      className={clsx("cursor-default", isExpanded && "cursor-default")}
    >
      <p className={clsx("text-sm", !isExpanded && "line-clamp-2")}>
        {children}
      </p>
      {!isExpanded && (
        <span
          className="text-muted-foreground hover:text-foreground text-sm font-medium mt-1"
        >
          Ler mais...
        </span>
      )}
      {isExpanded && (
        <button
          type="button"
          onClick={() => setIsExpanded(false)}
          className="text-muted-foreground hover:text-foreground text-sm font-medium mt-1"
        >
          Omitir
        </button>
      )}
    </div>
  );
}

interface AuthorRelevantWorksProps {
  works: AuthorRankingResult["works_list"];
}

function AuthorRelevantWorks({ works }: AuthorRelevantWorksProps) {
  if (!works || works.length === 0) {
    return null;
  }

  // Server already provides top 5 works sorted by cited count
  // Just sort by publication date ascending
  const displayWorks = [...works].sort((a, b) => {
    const dateA = new Date(a.publication_date);
    const dateB = new Date(b.publication_date);
    return dateA.getTime() - dateB.getTime();
  });

  function formatAuthorships(
    authorships: AuthorRankingResult["works_list"][number]["authorships"]
  ) {
    const positionOrder: Record<string, number> = { first: 0, middle: 1, last: 2 };
    const sortedAuthorships = [...authorships].sort((a, b) => {
      const aOrder = positionOrder[a.author_position] ?? 999;
      const bOrder = positionOrder[b.author_position] ?? 999;
      return aOrder - bOrder;
    });
    return sortedAuthorships.map((a) => a.author.display_name).join(", ");
  }

  return (
    <div className="max-w-2xl">
      <div className="mt-2 space-y-1">
        {displayWorks.map((work, index) => (
          <div
            key={index}
            className="text-sm text-foreground pl-4 pb-2 border-l border-border"
          >
            <div>
              {work.oa_url ? (
                <a
                  href={work.oa_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-foreground hover:text-foreground-accent inline-flex items-center gap-2 underline transition-colors"
                >
                  {work.display_name}
                  <ExternalLink className="inline !size-3" />
                </a>
              ) : (
                work.display_name
              )}
            </div>
            <div className="text-xs text-muted-foreground">
              {formatAuthorships(work.authorships)}
            </div>
            <div>
              <span className="text-xs text-muted-foreground">
                {work.publication_date
                  ? new Date(work.publication_date).getFullYear()
                  : "Data desconhecida"}
                {work.fwci !== null ? ` • FWCI: ${work.fwci.toFixed(2)}` : ""}
                {work.cited_by_count !== null
                  ? ` • Citações: ${work.cited_by_count}`
                  : ""}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

interface OrcidProfileProps {
  orcidId: string;
}

function OrcidProfile({ orcidId }: OrcidProfileProps) {
  const encodedId = encodeURIComponent(orcidId);
  
  const { data: orcidRecord, isLoading, isError } = useQuery({
    queryKey: ["orcid", orcidId],
    queryFn: async () => {
      const response = await api.orcid({ id: encodedId }).get();
      if (response.error) {
        throw new Error("Failed to fetch ORCID data");
      }
      return response.data as OrcidRecord;
    },
  });

  if (isLoading) {
    return (
      <div className="max-w-2xl">
        <div className="text-sm text-muted-foreground">Carregando perfil ORCID...</div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="max-w-2xl">
        <div className="text-sm text-red-500">Erro ao carregar perfil ORCID</div>
      </div>
    );
  }

  const emails = orcidRecord?.person?.emails?.email || [];
  const biography = orcidRecord?.person?.biography?.content;

  return (
    <div className="max-w-2xl">
      <div className="mt-2 space-y-4">
        {/* Email Section */}
        <div className="text-sm text-foreground pl-4 pb-2 border-l border-border">
          <div className="font-medium mb-1">Emails</div>
          {emails.length === 0 ? (
            <div className="text-muted-foreground">Nenhum email público disponível</div>
          ) : (
            <div className="space-y-1">
              {emails.map((emailEntry, index) => (
                <div key={index} className="text-sm">
                  {emailEntry.email}
                  {emailEntry.primary && (
                    <span className="ml-2 text-xs text-muted-foreground">(principal)</span>
                  )}
                  {emailEntry.verified && (
                    <span className="ml-1 text-xs text-green-600">✓</span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Biography Section */}
        <div className="text-sm text-foreground pl-4 pb-2 border-l border-border">
          <div className="font-medium mb-1">Biografia</div>
          {!biography ? (
            <div className="text-muted-foreground">Biografia não disponível</div>
          ) : (
            <CollapsibleParagraph>{biography}</CollapsibleParagraph>
          )}
        </div>

        {/* Employment Section */}
        <div className="text-sm text-foreground pl-4 pb-2 border-l border-border">
          <div className="font-medium mb-1">Empregos</div>
          {(() => {
            const employments = orcidRecord?.['activities-summary']?.employments?.['affiliation-group']
              ?.flatMap(group => group.summaries?.flatMap(summary => summary['employment-summary']) || []) || [];
            
            if (employments.length === 0) {
              return <div className="text-muted-foreground">Nenhum emprego público disponível</div>;
            }

            // Sort employments: null end-date first, then by start date
            const sortedEmployments = [...employments].sort((a, b) => {
              // If one has null end-date and the other doesn't, prioritize the one with null end-date
              if (!a?.['end-date'] && b?.['end-date']) return -1;
              if (a?.['end-date'] && !b?.['end-date']) return 1;
              
              // If both have same end-date status, sort by start date
              const aStartYear = a?.['start-date']?.year ? parseInt(a['start-date'].year) : 0;
              const bStartYear = b?.['start-date']?.year ? parseInt(b['start-date'].year) : 0;
              return bStartYear - aStartYear;
            });

            return (
              <div className="space-y-4 mt-4">
                {sortedEmployments.map((employment, index) => {
                  if (!employment) return null;
                  
                  const startYear = employment['start-date']?.year;
                  const endYear = employment['end-date']?.year;
                  const period = startYear ? 
                    `${startYear.value}${endYear?.value ? `-${endYear.value}` : '-presente'}` : 
                    'Período não informado';

                  return (
                    <div key={index} className="text-sm">
                      <div className="font-medium text-accent-foreground">
                        {employment.organization?.name || 'Organização não informada'}
                      </div>
                      {employment['department-name'] && (
                        <div>
                          {employment['department-name']}
                        </div>
                      )}
                      {employment['role-title'] && (
                        <div>
                          {employment['role-title']}
                        </div>
                      )}
                      <div className="text-xs">
                        {period}
                      </div>
                    </div>
                  );
                })}
              </div>
            );
          })()}
        </div>
      </div>
    </div>
  );
}

type AuthorResultDisplayProps = {
  author: AuthorRankingResult;
  summaries: Map<string, string | undefined>;
};
function AuthorResultDisplay({ author, summaries }: AuthorResultDisplayProps) {
  const summary = summaries.get(author.id);

  return (
    <section className="space-y-4">
      <header className="flex gap-x-4 justify-between items-start">
        <div>
          <h2 className="text-base text-accent-foreground">
            {author.display_name}
          </h2>
          <p className="text-sm">
            <InstitutionDisplay institutions={author.latest_institutions} />
          </p>
        </div>
        <div className="flex gap-1">
          {author.ids.orcid ? (
            <a
              href={author.ids.orcid}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs font-semibold bg-[#a9d040] text-white w-6 h-6 rounded-sm flex items-center justify-center"
            >
              ID
            </a>
          ) : null}
          {author.ids.wikipedia ? (
            <a
              href={author.ids.wikipedia}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs font-semibold font-serif bg-neutral-100 text-neutral-800 w-6 h-6 rounded-sm flex items-center justify-center"
            >
              W
            </a>
          ) : null}
        </div>
      </header>
      <div className="max-w-2xl">
        <CollapsibleParagraph>
          {summary}
        </CollapsibleParagraph>
        {/* <AuthorSummary summary={summary} /> */}
      </div>
      <div>
        <Tabs className="max-w-2xl">
          <TabsList variant="ghost" className="flex justify-start gap-x-4">
            <TabsTrigger
              value="relevant-works"
              variant="ghost"
              className={clsx(
                "flex items-center text-xs transition-colors cursor-pointer",
                "text-muted-foreground hover:text-foreground data-[state=active]:text-foreground data-[state=active]:hover:text-foreground-accent",
              )}
            >
              <LibraryIcon className="inline !size-3" />
              Trabalhos relevantes
            </TabsTrigger>
            {
              author.ids.orcid ? (
                <TabsTrigger
                  value="orcid"
                  variant="ghost"
                  className={clsx(
                    "flex items-center text-xs transition-colors cursor-pointer",
                    "text-muted-foreground hover:text-foreground data-[state=active]:text-foreground data-[state=active]:hover:text-foreground-accent",
                  )}
                >
                  <IdCardIcon className="inline !size-3" />
                  ORCiD
                </TabsTrigger>
              ) : null
            }
          </TabsList>
          <TabsContent value="relevant-works">
            <AuthorRelevantWorks works={author.works_list} />
          </TabsContent>
          {author.ids.orcid && (
            <TabsContent value="orcid">
              <OrcidProfile orcidId={author.ids.orcid} />
            </TabsContent>
          )}
        </Tabs>
      </div>
    </section>
  );
}

const querySchema = v.object({
  q: v.optional(v.fallback(v.string(), ""), ""),
});

export const Route = createFileRoute("/")({
  component: App,
  validateSearch: (search) => v.parse(querySchema, search),
});

// Original implementation using Elysia Eden treaty client
// function streamAuthorResults(queryContent: string) {
//   return {
//     async *[Symbol.asyncIterator]() {
//       const { data: authorEventStream, error } = await api.query.get({
//         query: { content: queryContent },
//       });
//       if (error) {
//         throw error;
//       }
//       for await (const event of authorEventStream) {
//         console.log("event", event);
//         yield event;
//       }
//     },
//   };
// }

// Valibot schemas for event validation
const AuthorsEventSchema = v.object({
  event: v.literal("authors"),
  data: v.array(v.object({
    id: v.string(),
    display_name: v.string(),
    ids: v.object({
      openalex: v.optional(v.nullable(v.string())),
      orcid: v.optional(v.nullable(v.string())),
      scopus: v.optional(v.nullable(v.string())),
      twitter: v.optional(v.nullable(v.string())),
      wikipedia: v.optional(v.nullable(v.string())),
    }),
    summary_stats: v.object({
      h_index: v.nullable(v.number()),
      two_year_mean_citedness: v.nullable(v.number()),
      i10_index: v.nullable(v.number()),
    }),
    latest_institutions: v.array(v.object({
      id: v.string(),
      display_name: v.string(),
      country_code: v.nullable(v.string()),
    })),
    works_list: v.array(v.object({
      id: v.string(),
      display_name: v.fallback(v.string(), "Título desconhecido"),
      publication_date: v.string(),
      doi: v.nullable(v.string()),
      oa_url: v.nullable(v.string()),
      fwci: v.nullable(v.number()),
      cited_by_count: v.number(),
      authorships: v.array(v.object({
        author: v.object({
          id: v.string(),
          display_name: v.string(),
          orcid: v.nullable(v.string()),
        }),
        author_position: v.string(),
      })),
    })),
  })),
});

const AuthorSummaryEventSchema = v.object({
  event: v.literal("author_summary"),
  data: v.object({
    authorId: v.string(),
    summary: v.string(),
  }),
});

const EventTypeSchema = v.union([AuthorsEventSchema, AuthorSummaryEventSchema]);

type EventType = v.InferInput<typeof EventTypeSchema>;

// New implementation using native EventSource API
function streamAuthorResults(queryContent: string) {
  return {
    async *[Symbol.asyncIterator]() {
      const baseUrl = import.meta.env.VITE_API_URL;
      const url = new URL('/query', baseUrl);
      url.searchParams.set('content', queryContent);
      
      const eventSource = new EventSource(url.toString());
      const eventQueue: Array<EventType> = [];
      let isFinished = false;
      let pendingResolve: ((value: EventType | null) => void) | null = null;
      
      const handleAuthors = (e: MessageEvent) => {
        try {
          const rawData = JSON.parse(e.data);
          const result = v.safeParse(AuthorsEventSchema, { event: 'authors', data: rawData });
          if (result.success) {
            if (pendingResolve) {
              pendingResolve(result.output);
              pendingResolve = null;
            } else {
              eventQueue.push(result.output);
            }
          }
          else {
            console.error('Invalid authors event data:', result.issues);
          }
        } catch (error) {
          console.error('Failed to parse or validate authors data:', error);
        }
      };

      const handleAuthorSummary = (e: MessageEvent) => {
        try {
          const rawData = JSON.parse(e.data);
          const event = v.parse(AuthorSummaryEventSchema, { event: 'author_summary', data: rawData });
          if (pendingResolve) {
            pendingResolve(event);
            pendingResolve = null;
          } else {
            eventQueue.push(event);
          }
        } catch (error) {
          console.error('Failed to parse or validate author_summary data:', error);
        }
      };

      const handleError = () => {
        isFinished = true;
        if (pendingResolve) {
          pendingResolve(null);
          pendingResolve = null;
        }
      };

      const cleanup = () => {
        eventSource.removeEventListener('authors', handleAuthors);
        eventSource.removeEventListener('author_summary', handleAuthorSummary);
        eventSource.removeEventListener('error', handleError);
        eventSource.close();
      };

      eventSource.addEventListener('authors', handleAuthors);
      eventSource.addEventListener('author_summary', handleAuthorSummary);
      eventSource.addEventListener('error', handleError);

      try {
        while (!isFinished) {
          if (eventQueue.length > 0) {
            const event = eventQueue.shift();
            if (!event) {
              throw new Error("Unexpected null event");
            }
            yield event;
          } else {
            const event = await new Promise<EventType | null>((resolve) => {
              pendingResolve = resolve;
            });
            if (event) {
              yield event;
            } else {
              break;
            }
          }
        }
      } finally {
        cleanup();
      }
    },
  };
}

const authorStreamQuery = (queryContent: string) =>
  queryOptions({
    queryKey: ["authors", queryContent],
    queryFn: streamedQuery({
      queryFn: () => streamAuthorResults(queryContent),
    }),
    staleTime: Infinity,
    enabled: !!queryContent,
    refetchOnWindowFocus: false,
  });

function SearchResults() {
  const { q } = Route.useSearch();

  const streamQuery = useQuery(authorStreamQuery(q));

  const authors = streamQuery.data?.flatMap((event) =>
    event.event === "authors" ? event.data : []
  );
  const summaries = useMemo(() => {
    const map = new Map<string, string | undefined>();
    streamQuery.data?.forEach((event) => {
      if (event.event === "author_summary") {
        map.set(event.data.authorId, event.data.summary);
      }
    });
    return map;
  }, [streamQuery.data]);

  if (!streamQuery.isEnabled) {
    return <PhilosophyQuote />;
  }

  if (streamQuery.isError) {
    return <ErrorMessage />;
  }

  if (streamQuery.isLoading) {
    return <Searching />;
  }

  if (!authors) {
    return "...";
  }

  return (
    <div role="list" className="space-y-8 pb-8">
      {authors.map((author) => {
        return (
          <div key={author.id} role="listitem" className="py-1">
            <AuthorResultDisplay author={author} summaries={summaries} />
          </div>
        );
      })}
    </div>
  );
}

function App() {
  const { q } = Route.useSearch();
  const [inputText, setInputText] = useState(q);
  const navigate = Route.useNavigate();

  function submitSearch(e: React.FormEvent) {
    e.preventDefault();
    navigate({
      search: { q: inputText },
    });
  }

  return (
    <main className="flex flex-col px-8 items-center [&>*]:w-2xl [&>*]:max-w-full [&>*]:min-w-fit space-y-8">
      <header className="pt-24 text-center">
        <h1 className="text-3xl tracking-wide font-semibold text-foreground-accent">
          papertrail
        </h1>
      </header>
      <form onSubmit={submitSearch} className="w-full">
        <InputLayout className="flex items-center px-3 gap-2">
          <Input
            variant="ghost"
            className="font-mono px-0 flex-1"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Pesquise por um tema"
          />
          <button
            type="submit"
            aria-label="Pesquisar"
            disabled={!inputText}
            className="text-foreground-accent disabled:text-muted-foreground"
          >
            <Search className="h-4 w-4 transition-colors" />
          </button>
        </InputLayout>
      </form>
      <SearchResults />
    </main>
  );
}

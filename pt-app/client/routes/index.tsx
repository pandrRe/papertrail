import { createFileRoute } from "@tanstack/react-router";
import {
  queryOptions,
  experimental_streamedQuery as streamedQuery,
  useQuery,
} from "@tanstack/react-query";
import { useState, useMemo, useEffect } from "react";
import { Search, BookOpen, Book, SearchXIcon, LibraryIcon } from "lucide-react";
import clsx from "clsx";
import * as v from "valibot";
import { Input, InputLayout } from "@/components/ui/input";
import { api } from "@/lib/api";
import type { AuthorRankingResult } from "#/types";
import { countryCodeToFlagEmoji } from "@/lib/countryCodeToEmoji";

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
  institution: AuthorRankingResult["latest_institution"];
};
function InstitutionDisplay({ institution }: InstitutionDisplayProps) {
  if (!institution) {
    return <span>Instituição desconhecida</span>;
  }
  return (
    <a
      href={institution?.homepage_url || undefined}
      target="_blank"
      rel="noopener noreferrer"
      className="text-sm group flex items-center gap-1.5 leading-none"
    >
      <span className="group-hover:underline">{institution.display_name}</span>
      <span className="text-sm">
        {institution.country_code
          ? countryCodeToFlagEmoji(institution.country_code)
          : null}
      </span>
    </a>
  );
}

interface AuthorSummaryProps {
  summary: string | undefined;
}

function AuthorSummary({ summary }: AuthorSummaryProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (summary === undefined) {
    return <span className="text-muted-foreground">...</span>;
  }

  return (
    <div>
      <p className={clsx("text-sm", !isExpanded && "line-clamp-2")}>
        {summary}
      </p>
      {!isExpanded && (
        <button
          onClick={() => setIsExpanded(true)}
          className="text-muted-foreground hover:text-foreground text-sm font-medium mt-1"
        >
          Ler mais...
        </button>
      )}
      {isExpanded && (
        <button
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
  const [isExpanded, setIsExpanded] = useState(false);

  if (!works || works.length === 0) {
    return null;
  }

  const displayWorks = [...works]
    .sort((a, b) => {
      return b.cited_by_count - a.cited_by_count;
    })
    .slice(0, 5);

  function formatAuthorships(
    authorships: AuthorRankingResult["works_list"][number]["authorships"]
  ) {
    const positionOrder = { first: 0, middle: 1, last: 2 };
    const sortedAuthorships = [...authorships].sort((a, b) => {
      return (
        positionOrder[a.author_position] - positionOrder[b.author_position]
      );
    });
    return sortedAuthorships.map((a) => a.display_name).join(", ");
  }

  return (
    <div className="max-w-2xl">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className={clsx(
          "flex items-center text-xs transition-colors",
          isExpanded
            ? "text-foreground hover:text-foreground-accent"
            : "text-muted-foreground hover:text-foreground"
        )}
      >
        <LibraryIcon className="inline h-3 w-3 mr-1" />
        Trabalhos relevantes
      </button>
      {isExpanded && (
        <div className="mt-2 space-y-1">
          {displayWorks.map((work, index) => (
            <div
              key={index}
              className="text-sm text-foreground pl-4 pb-2 border-l border-border"
            >
              <div>{work.display_name}</div>
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
      )}
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
            <InstitutionDisplay institution={author.latest_institution} />
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
        <AuthorSummary summary={summary} />
      </div>
      <div>
        <AuthorRelevantWorks works={author.works_list} />
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

function streamAuthorResults(queryContent: string) {
  return {
    async *[Symbol.asyncIterator]() {
      const { data: authorEventStream, error } = await api.query.get({
        query: { content: queryContent },
      });
      if (error) {
        throw error;
      }
      for await (const event of authorEventStream) {
        console.log("event", event);
        yield event;
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

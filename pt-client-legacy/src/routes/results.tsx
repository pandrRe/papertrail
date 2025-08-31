import Header from "@/components/Header";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { SkeletonLoader } from "@/components/ui/skeleton-loader";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import type { ExtendedAuthorSchema, PublicationSchema } from "@/lib/contracts";
import { createSearchStream } from "@/lib/searchStream";
import { cn } from "@/lib/utils";
import { createFileRoute, redirect } from "@tanstack/react-router";
import {
  BookTextIcon,
  QuoteIcon,
  SquareArrowOutUpRightIcon,
  UserPlusIcon,
  UsersIcon,
} from "lucide-react";
import { useEffect, useState } from "react";
import * as v from "valibot";

const resultsSearchSchema = v.object({
  query: v.pipe(v.string(), v.nonEmpty()),
});

export const Route = createFileRoute("/results")({
  component: RouteComponent,
  validateSearch: resultsSearchSchema,
  onCatch() {
    return redirect({
      to: "/",
    });
  },
});

export function AuthorListingSkeletonLoader() {
  return (
    <div className="space-y-6">
      <header className="flex gap-4 items-start">
        <div>
          <img
            className="rounded-full size-12 object-cover aspect-square grow min-w-12"
            src={"/avatar_scholar.png"}
          />
        </div>
        <div className="flex grow gap-4 items-center flex-wrap justify-between">
          <div className="grow space-y-1">
            <h2 className="text-2xl font-semibold leading-none">
              <SkeletonLoader className="h-8 w-5/12 bg-primary/30" />
            </h2>
            <p className="text-stone-600 text-sm whitespace-normal">
              <SkeletonLoader className="h-4 w-7/12 bg-stone-300" />
            </p>
          </div>
          <div>
            <Button className="rounded-2xl !px-4" variant="outline" disabled>
              <UserPlusIcon />
              Seguir
            </Button>
          </div>
        </div>
      </header>
      <div className="md:flex space-y-2 md:space-y-0 gap-2">
        <div className="basis-1/3 space-y-2 bg-foreground/3 p-6 rounded-lg">
          <header className="font-semibold">Sobre</header>
          <div className="leading-6 space-y-2">
            <SkeletonLoader className="h-4 w-full bg-stone-300" />
            <div className="flex gap-2">
              <SkeletonLoader className="h-4 w-1/4 bg-stone-300" />
              <SkeletonLoader className="h-4 w-3/4 bg-stone-300" />
            </div>
          </div>
        </div>
        <div className="basis-2/3 space-y-2 bg-foreground/3 p-6 rounded-lg">
          <header className="font-semibold">Trabalhos relacionados</header>
          <ul>
            <li className="py-4">
              <header className="font-medium underline flex mb-1">
                <SkeletonLoader className="h-4 w-7/12 bg-primary/30" />
                <SquareArrowOutUpRightIcon className="ml-1 inline-block size-3.5" />
              </header>
              <div className="text-xs text-stone-600">
                <SkeletonLoader className="h-4 w-5/12 bg-stone-300" />
              </div>
            </li>
            <li className="py-4">
              <header className="font-medium underline flex mb-1">
                <SkeletonLoader className="h-4 w-6/12 bg-primary/30" />
                <SquareArrowOutUpRightIcon className="ml-1 inline-block size-3.5" />
              </header>
              <div className="text-xs text-stone-600">
                <SkeletonLoader className="h-4 w-10/12 bg-stone-300" />
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export function PublicationListingSkeletonLoader() {
  return (
    <Card className="w-lg p-0 overflow-clip gap-0">
      <CardHeader className="p-0 m-0 bg-neutral-800 h-64"></CardHeader>
      <CardContent className="py-5 px-7 m-0 bg-stone-50 space-y-3 grow">
        <div>
          <SkeletonLoader className="h-6 w-8/12 bg-stone-400" />
        </div>
        <div className="flex gap-2">
          <SkeletonLoader className="h-4 w-1/4 bg-stone-300" />
          <SkeletonLoader className="h-4 w-3/4 bg-stone-300" />
        </div>
        <div className="pt-2 flex gap-4 w-full">
          <div className="flex gap-0.5">
            <UsersIcon className="h-4" />
            <SkeletonLoader className="h-4 w-5 bg-stone-400" />
          </div>
          <div className="flex gap-0.5">
            <QuoteIcon className="h-4" />
            <SkeletonLoader className="h-4 w-5 bg-stone-400" />
          </div>
          <div className="flex gap-0.5 grow">
            <BookTextIcon className="h-4" />
            <SkeletonLoader className="h-4 w-6/12 bg-stone-400" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

type PublicationListingProps = {
  publication: PublicationSchema;
  requestState: "idle" | "loading" | "error" | "success";
};
export function PublicationListing({ publication }: PublicationListingProps) {
  console.log(publication);
  return (
    <Card className="w-lg p-0 overflow-clip gap-0 grow">
      <CardHeader className="p-0 m-0 bg-neutral-800 h-64 overflow-clip">
        <div className="font-serif text-stone-50 text-center px-6 pt-12">
          <div className="text-base text-balance">{publication.bib?.title}</div>
          <div className="text-xs mt-2">
            {Array.isArray(publication.bib?.author)
              ? publication.bib?.author.join(", ")
              : publication.bib?.author}
          </div>
          <div className="text-xs mt-4 text-justify px-6">
            {publication.bib?.abstract}
          </div>
        </div>
      </CardHeader>
      <CardContent className="py-5 px-7 m-0 bg-stone-50 space-y-3 flex flex-col grow">
        <div className="space-y-1.5 grow">
          <div className="text-lg font-medium leading-6">
            {publication.bib?.title}
          </div>
          <div className="flex gap-2">
            {publication.bib?.abstract?.slice(0, 150)}
            ...
          </div>
        </div>
        <div className="pt-2 flex gap-4 w-full">
          <div className="flex gap-0.5 items-center">
            <UsersIcon className="h-4" />
            {publication.bib?.author?.length}
          </div>
          <div className="flex gap-0.5 items-center">
            <QuoteIcon className="h-4" />
            {publication.numCitations}
          </div>
          <div className="flex gap-0.5 grow items-center">
            <BookTextIcon className="h-4" />
            {publication.bib?.citation}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

type AuthorSummaryProps = {
  author: ExtendedAuthorSchema;
  requestState: "idle" | "loading" | "error" | "success";
};
export function AuthorSummary({ author, requestState }: AuthorSummaryProps) {
  if (author.summary) {
    return author.summary;
  }

  if (
    requestState == "loading" ||
    requestState == "success" ||
    requestState == "idle"
  ) {
    return (
      <>
        <SkeletonLoader className="h-4 w-full bg-stone-300" />
        <div className="flex gap-2">
          <SkeletonLoader className="h-4 w-1/4 bg-stone-300" />
          <SkeletonLoader className="h-4 w-3/4 bg-stone-300" />
        </div>
      </>
    );
  }

  return (
    <div className="italic">Erro ao obter lista de trabalhos relacionados.</div>
  );
}

function getPublicationCitationUrl(
  publication: PublicationSchema,
  author: ExtendedAuthorSchema
) {
  if (!publication.authorPubId || !author.scholarId) {
    return "#";
  }
  return `https://scholar.google.com/citations?view_op=view_citation&hl=pt&user=${author.scholarId}&citation_for_view=${publication.authorPubId}`;
}

type AuthorPublicationsPreviewProps = {
  author: ExtendedAuthorSchema;
  requestState: "idle" | "loading" | "error" | "success";
};
export function AuthorPublicationsPreview({
  author,
  requestState,
}: AuthorPublicationsPreviewProps) {
  if ((author.publications?.length ?? 0) > 0) {
    return (
      <ul>
        {author.publications?.slice(0, 3).map((publication) => (
          <li
            className={cn("py-4", publication.citedbyUrl && "cursor-pointer")}
            key={publication.authorPubId}
          >
            <header className="font-medium underline">
              <a href={getPublicationCitationUrl(publication, author)}>
                {publication.bib?.title}
                <SquareArrowOutUpRightIcon className="ml-1 inline-block size-3.5" />
              </a>
            </header>
            <div className="text-xs text-stone-600">
              {publication.bib?.citation}
            </div>
          </li>
        ))}
      </ul>
    );
  }

  if (
    requestState == "loading" ||
    requestState == "success" ||
    requestState == "idle"
  ) {
    return (
      <ul>
        <li className="py-4">
          <header className="font-medium underline flex mb-1">
            <SkeletonLoader className="h-4 w-7/12 bg-primary/30" />
            <SquareArrowOutUpRightIcon className="ml-1 inline-block size-3.5" />
          </header>
          <div className="text-xs text-stone-600">
            <SkeletonLoader className="h-4 w-5/12 bg-stone-300" />
          </div>
        </li>
        <li className="py-4">
          <header className="font-medium underline flex mb-1">
            <SkeletonLoader className="h-4 w-6/12 bg-primary/30" />
            <SquareArrowOutUpRightIcon className="ml-1 inline-block size-3.5" />
          </header>
          <div className="text-xs text-stone-600">
            <SkeletonLoader className="h-4 w-10/12 bg-stone-300" />
          </div>
        </li>
      </ul>
    );
  }
}

type AuthorListingProps = {
  author: ExtendedAuthorSchema;
  requestState: "idle" | "loading" | "error" | "success";
};
function AuthorListing({ author, requestState }: AuthorListingProps) {
  return (
    <div className="space-y-6">
      <header className="flex gap-4 items-start">
        <div>
          <img
            className="rounded-full size-12 object-cover aspect-square grow min-w-12"
            src={author.urlPicture}
          />
        </div>
        <div className="flex grow gap-4 items-center flex-wrap justify-between">
          <div className="grow space-y-1">
            <h2 className="text-2xl font-semibold leading-none">
              {author.name}
            </h2>
            <p className="text-stone-600 text-sm whitespace-normal">
              {author.affiliation}
            </p>
          </div>
          <div>
            <Button className="rounded-2xl !px-4" variant="outline">
              <UserPlusIcon />
              Seguir
            </Button>
          </div>
        </div>
      </header>
      <div className="md:flex space-y-2 md:space-y-0 gap-2">
        <div className="basis-1/3 space-y-2 bg-foreground/3 p-6 rounded-lg">
          <header className="font-semibold">Sobre</header>
          <div className="leading-6 space-y-2">
            <AuthorSummary author={author} requestState={requestState} />
          </div>
        </div>
        <div className="basis-2/3 space-y-2 bg-foreground/3 p-6 rounded-lg">
          <header className="font-semibold">Trabalhos relacionados</header>
          <AuthorPublicationsPreview
            author={author}
            requestState={requestState}
          />
        </div>
      </div>
    </div>
  );
}

type AuthorResultsProps = {
  authors: ExtendedAuthorSchema[];
  requestState: "idle" | "loading" | "error" | "success";
};
function AuthorResults({ authors, requestState }: AuthorResultsProps) {
  if (requestState == "error") {
    return <div>Erro ao buscar por autores.</div>;
  }

  if (
    (requestState == "idle" || requestState == "loading") &&
    authors.length === 0
  ) {
    return (
      <div role="list" className="space-y-16">
        {Array.from([1, 2, 3]).map((i) => (
          <AuthorListingSkeletonLoader key={i} />
        ))}
      </div>
    );
  }

  if (
    (requestState == "loading" || requestState == "success") &&
    authors.length > 0
  ) {
    return (
      <div role="list" className="space-y-16">
        {authors.map((author) => (
          <AuthorListing
            key={author.scholarId}
            author={author}
            requestState={requestState}
          />
        ))}
      </div>
    );
  }

  if (requestState == "success" && authors.length === 0) {
    return <div>Nenhum autor encontrado.</div>;
  }

  throw Error("Invalid state");
}

type PublicationResultsProps = {
  publications: PublicationSchema[];
  requestState: "idle" | "loading" | "error" | "success";
};
function PublicationResults({
  publications,
  requestState,
}: PublicationResultsProps) {
  if (requestState == "error") {
    return <div>Erro ao buscar por publicações.</div>;
  }

  if (
    (requestState == "idle" || requestState == "loading") &&
    publications.length === 0
  ) {
    return (
      <div role="list" className="flex flex-wrap gap-x-4 gap-y-8">
        {Array.from([1, 2, 3, 4]).map((i) => (
          <PublicationListingSkeletonLoader key={i} />
        ))}
      </div>
    );
  }
  if (
    (requestState == "loading" || requestState == "success") &&
    publications.length > 0
  ) {
    return (
      <div
        role="list"
        className="flex flex-wrap gap-x-4 gap-y-8 justify-center"
      >
        {publications.map((publication) => (
          <PublicationListing
            key={publication.authorPubId}
            publication={publication}
            requestState={requestState}
          />
        ))}
      </div>
    );
  }

  if (requestState == "success" && publications.length === 0) {
    return <div>Nenhuma publicação encontrado.</div>;
  }

  throw Error("Invalid state");
}

function RouteComponent() {
  const { query } = Route.useSearch();
  const [requestState, setRequestState] = useState<
    "idle" | "loading" | "error" | "success"
  >("idle");
  const [requestData, setRequestData] = useState<{
    authors: ExtendedAuthorSchema[];
    publications: PublicationSchema[];
  }>({
    authors: [],
    publications: [],
  });

  useEffect(() => {
    setRequestState("loading");
    const source = createSearchStream(query, {
      onMessage: (data) => {
        if (!data) {
          return;
        }
        switch (data.type) {
          case "set:author:list":
            setRequestData((prev) => ({
              ...prev,
              authors: data.payload,
            }));
            break;
          case "set:publication:list":
            setRequestData((prev) => ({
              ...prev,
              publications: data.payload,
            }));
            break;
          case "update:author":
            setRequestData((prev) => ({
              ...prev,
              authors: prev.authors.map((author) => {
                if (author.scholarId === data.payload.scholarId) {
                  return data.payload;
                }
                return author;
              }),
            }));
            break;
          default:
            console.warn("Unknown stream message type", data);
        }
      },
      onError: () => {
        setRequestState("error");
      },
      onFinish: () => {
        setRequestState("success");
      },
    });
    return () => {
      source.close();
    };
  }, [query, setRequestState]);

  return (
    <section className="w-full">
      <Header />
      <div className="w-6xl max-w-dvw px-4 pt-[clamp(2em,_10vw,_10vh)] mx-auto space-y-8 pb-12">
        <header className="text-xl font-medium">
          <h1>Exibindo resultados para "{query}":</h1>
        </header>
        <div>
          <Tabs defaultValue="authors">
            <TabsList className="mb-8">
              <TabsTrigger value="authors" className="px-4 py-1.5">
                {/* <div className="text-2xl font-semibold">254</div> */}
                <div>Autores encontrados</div>
              </TabsTrigger>
              <TabsTrigger value="papers" className="px-4 py-1.5">
                <div>Artigos encontrados</div>
              </TabsTrigger>
            </TabsList>
            <TabsContent value="authors" className="w-full">
              <AuthorResults
                authors={requestData.authors}
                requestState={requestState}
              />
            </TabsContent>
            <TabsContent value="papers" className="w-full">
              <PublicationResults
                publications={requestData.publications}
                requestState={requestState}
              />
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </section>
  );
}

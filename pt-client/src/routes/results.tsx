import Header from "@/components/Header";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import type { ExtendedAuthorSchema, PublicationSchema } from "@/lib/contracts";
import { createSearchStream } from "@/lib/searchStream";
import { createFileRoute, redirect } from "@tanstack/react-router";
import { SquareArrowOutUpRightIcon, UserPlusIcon } from "lucide-react";
import { useEffect, useRef, useState } from "react";
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

type AuthorListingProps = {
  author: ExtendedAuthorSchema;
};
function AuthorListing({ author }: AuthorListingProps) {
  return (
    <div className="space-y-6">
      <header className="flex gap-4 items-center">
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
          <p className="leading-6">{author.summary}</p>
        </div>
        <div className="basis-2/3 space-y-2 bg-foreground/3 p-6 rounded-lg">
          <header className="font-semibold">Trabalhos relacionados</header>
          <ul>
            {author.publications?.slice(0, 3).map((publication) => (
              <li className="py-4">
                <header className="font-medium underline">
                  {publication.bib?.title}
                  <SquareArrowOutUpRightIcon className="ml-1 inline-block size-3.5" />
                </header>
                <div className="text-xs text-stone-600">
                  {publication.bib?.citation}
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
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
      <div className="w-5xl max-w-dvw px-4 pt-[clamp(2em,_10vw,_10vh)] mx-auto space-y-8 pb-12">
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
              <div role="list" className="space-y-16">
                {requestData.authors.map((author) => (
                  <AuthorListing key={author.scholarId} author={author} />
                ))}
              </div>
            </TabsContent>
            <TabsContent value="papers">Listagem de artigos</TabsContent>
          </Tabs>
        </div>
      </div>
    </section>
  );
}

import Header from "@/components/Header";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { createFileRoute, redirect } from "@tanstack/react-router";
import { SquareArrowOutUpRightIcon, UserPlusIcon } from "lucide-react";
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
  name: string;
  email: string;
  avatar: string;
};
function AuthorListing() {
  return (
    <div className="space-y-6">
      <header className="flex gap-4 items-center">
        <div>
          <img
            className="rounded-full size-12 object-cover"
            src="https://gravatar.com/avatar/27205e5c51cb03f862138b22bcb5dc20f94a342e744ff6df1b8dc8af3c865109"
          />
        </div>
        <div className="grow">
          <h2 className="text-2xl font-semibold leading-none">
            Autor S. da Silva
          </h2>
          <p className="text-stone-600 text-sm">Universidade Federal do Pará</p>
        </div>
        <div>
          <Button className="rounded-2xl !px-4">
            <UserPlusIcon />
            Seguir
          </Button>
        </div>
      </header>
      <div className="md:flex space-y-2 md:space-y-0 gap-2">
        <div className="basis-1/3 space-y-2 bg-foreground/3 p-6 rounded-lg">
          <header className="font-semibold">Sobre</header>
          <p>Um parágrafo curto sobre o autor.</p>
          <p>
            Um parágrafo um pouco maior sobre o seu trabalho com o tema
            pesquisado.
          </p>
        </div>
        <div className="basis-2/3 space-y-2 bg-foreground/3 p-6 rounded-lg">
          <header className="font-semibold">Trabalhos relacionados</header>
          <ul>
            <li className="py-4">
              <header className="font-medium underline">
                Efficient Prompt Optimization for Large Language Models in
                Resource-Constrained Environments
                <SquareArrowOutUpRightIcon className="ml-1 inline-block size-3.5" />
              </header>
              <div className="text-xs text-stone-600">
                A Silva, B Costa, R Mendes, L Oliveira, P Santos, M Ferreira
                IEEE Transactions on Neural Networks and Learning Systems 35
                (2), 1124-1138
              </div>
            </li>
            <li className="py-4">
              <header className="font-medium underline">
                Efficient Prompt Optimization for Large Language Models in
                Resource-Constrained Environments
                <SquareArrowOutUpRightIcon className="ml-1 inline-block size-3.5" />
              </header>
              <div className="text-xs text-stone-600">
                A Silva, B Costa, R Mendes, L Oliveira, P Santos, M Ferreira
                IEEE Transactions on Neural Networks and Learning Systems 35
                (2), 1124-1138
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

function RouteComponent() {
  const { query } = Route.useSearch();
  return (
    <section className="w-full">
      <Header />
      <div className="w-5xl max-w-dvw px-4 pt-[clamp(2em,_10vw,_10vh)] mx-auto space-y-8">
        <header className="text-xl font-medium">
          <h1>Exibindo resultados para "{query}":</h1>
        </header>
        <div>
          <Tabs defaultValue="authors">
            <TabsList className="bg-background space-x-2 h-fit mb-6">
              <TabsTrigger
                value="authors"
                className="h-fit flex-col px-4 py-2 gap-0 items-start border border-foreground whitespace-break-spaces text-left"
              >
                <div className="text-2xl font-semibold">254</div>
                <div>autores encontrados</div>
              </TabsTrigger>
              <TabsTrigger
                value="papers"
                className="self-stretch flex-col px-4 py-2 gap-0 items-start border border-foreground whitespace-break-spaces text-left"
              >
                <div className="text-2xl font-semibold">1.543</div>
                <div>artigos encontrados</div>
              </TabsTrigger>
            </TabsList>
            <TabsContent value="authors" className="w-full">
              <AuthorListing />
            </TabsContent>
            <TabsContent value="papers">Change your password here.</TabsContent>
          </Tabs>
        </div>
      </div>
    </section>
  );
}

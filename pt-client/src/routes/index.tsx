import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { Input, InputWrapper } from "@/components/ui/input";
import { useState } from "react";
import { SearchIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/")({
  component: App,
});

function App() {
  const [search, setSearch] = useState("");
  const hasSearch = search.length > 0;
  const navigate = useNavigate();

  return (
    <section className="w-full flex justify-center pt-[20vh] pb-12 px-4">
      <div className="space-y-12 flex flex-col items-center">
        <h1 className="text-6xl font-semibold">papertrail</h1>
        <div role="searchbox" className="min-w-[min(50vw,640px)]">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              navigate({
                to: "/results",
                search: { query: search },
              });
            }}
          >
            <InputWrapper className="w-full p-0 rounded-2xl items-center">
              <Input
                placeholder="Procure por um tema..."
                className="p-0 md:text-lg px-6 h-fit py-3"
                variant="ghost"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                autoFocus
              />
              <Button
                type="submit"
                disabled={!hasSearch}
                className={cn(
                  "size-12 m-1 rounded-xl transition-all !opacity-0 transform scale-80",
                  hasSearch && "!opacity-100 scale-100"
                )}
              >
                <SearchIcon className="size-5" />
              </Button>
            </InputWrapper>
          </form>
          <div className="mt-24 space-y-2">
            <h2>Recentemente pesquisados:</h2>
            <ul className="flex gap-2 text-sm text-center">
              <li className="bg-primary text-background px-3 py-1 rounded-full flex items-center justify-center">
                LLMs
              </li>
              <li className="bg-primary text-background px-3 py-1 rounded-full flex items-center justify-center">
                Inteligência artificial
              </li>
              <li className="bg-primary text-background px-3 py-1 rounded-full flex items-center justify-center">
                Engenharia de software
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}

import { createFileRoute } from "@tanstack/react-router";
import React, { useState, useMemo, useEffect } from "react";
import { Input, InputLayout } from "@/components/ui/input";
import { Search, BookOpen, Book } from "lucide-react";

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

export const Route = createFileRoute("/")({
  component: App,
});

function App() {
  const [inputText, setInputText] = useState("");

  return (
    <main className="flex flex-col px-8 items-center [&>*]:w-2xl [&>*]:max-w-full [&>*]:min-w-fit space-y-8">
      <header className="pt-24 text-center">
        <h1 className="text-3xl tracking-wide font-semibold text-foreground-accent">
          papertrail
        </h1>
      </header>
      <div>
        <InputLayout className="flex items-center px-3 gap-2">
          <Input
            variant="ghost"
            className="font-mono px-0 flex-1"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Pesquise por um tema"
          />
          <Search
            className={`h-4 w-4 transition-colors ${inputText ? "text-foreground-accent" : "text-muted-foreground"}`}
          />
        </InputLayout>
      </div>
      {inputText ? <Searching /> : <PhilosophyQuote />}
    </main>
  );
}

import { Link } from "@tanstack/react-router";

export default function Header() {
  return (
    <header className="p-2 flex gap-2 bg-background text-foreground justify-between border-b border-border">
      <nav className="flex flex-row">
        <div className="px-2 font-semibold">
          <Link to="/">papertrail</Link>
        </div>
      </nav>
    </header>
  );
}

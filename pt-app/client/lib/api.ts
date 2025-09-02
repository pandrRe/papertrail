import { treaty } from "@elysiajs/eden";
import type { App } from "#/index";

if (!import.meta.env.VITE_API_URL) {
  throw new Error("Missing VITE_API_URL environment variable");
}

const api = treaty<App>(import.meta.env.VITE_API_URL);

export { api };

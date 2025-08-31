import { defineConfig } from "@kubb/core";
import { pluginOas } from "@kubb/plugin-oas";
import { pluginTs } from "@kubb/plugin-ts";
import { pluginReactQuery } from "@kubb/plugin-react-query";
import { pluginZod } from "@kubb/plugin-zod";

export default defineConfig(() => ({
  root: "./",
  input: {
    path: "./openapi.json",
  },
  output: {
    path: "./src/lib/contracts",
  },
  plugins: [
    pluginOas(),
    pluginTs(),
    pluginReactQuery({
      client: {
        importPath: "@kubb/plugin-client/clients/fetch",
      },
      parser: "zod",
    }),
    pluginZod({
      unknownType: "unknown",
      inferred: true,
    }),
  ],
}));

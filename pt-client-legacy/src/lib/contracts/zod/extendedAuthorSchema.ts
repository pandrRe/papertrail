import { authorSourceSchema } from "./authorSourceSchema.ts";
import { publicAccessSchema } from "./publicAccessSchema.ts";
import { publicationSchema } from "./publicationSchema.ts";
import { z } from "zod";

export const extendedAuthorSchema = z.object({
  scholarId: z.string().optional(),
  name: z.string().optional(),
  affiliation: z.string().optional(),
  organization: z.number().int().optional(),
  emailDomain: z.string().optional(),
  urlPicture: z.string().optional(),
  homepage: z.string().optional(),
  citedby: z.number().int().optional(),
  filled: z.array(z.string()).optional(),
  interests: z.array(z.string()).optional(),
  citedby5Y: z.number().int().optional(),
  hindex: z.number().int().optional(),
  hindex5Y: z.number().int().optional(),
  i10Index: z.number().int().optional(),
  i10Index5Y: z.number().int().optional(),
  citesPerYear: z.object({}).catchall(z.number().int()).optional(),
  publicAccess: z.lazy(() => publicAccessSchema).optional(),
  publications: z.array(z.lazy(() => publicationSchema)).optional(),
  coauthors: z.array(z.unknown()).optional(),
  containerType: z.string().optional(),
  source: z.lazy(() => authorSourceSchema).optional(),
  summary: z.union([z.string(), z.null()]).optional(),
});

export type ExtendedAuthorSchema = z.infer<typeof extendedAuthorSchema>;

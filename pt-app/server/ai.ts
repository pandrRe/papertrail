import { GoogleGenAI } from "@google/genai";
import { AuthorRankingResult } from "./types";

if (!process.env.GEMINI_API_KEY) {
  throw new Error("Missing GEMINI_API_KEY environment variable");
}

const client = new GoogleGenAI({
  apiKey: process.env.GEMINI_API_KEY,
});

export async function generateEmbedding(text: string): Promise<number[]> {
  const response = await client.models.embedContent({
    model: "gemini-embedding-001",
    contents: text,
    config: {
      taskType: "SEMANTIC_SIMILARITY",
      outputDimensionality: 768,
    },
  });

  const embeddings = response.embeddings?.at(0);

  if (!embeddings) {
    const error = new Error("Embeddings missing from response.");
    return Promise.reject(error);
  }

  const vector = embeddings.values;
  if (!vector) {
    const error = new Error("Vector missing from embeddings.");
    return Promise.reject(error);
  }

  const magnitude = Math.sqrt(vector.reduce((sum, val) => sum + val * val, 0));
  const normalizedVector = vector.map((val) => val / magnitude);

  return normalizedVector;
}

const promptGenerator = (author: AuthorRankingResult, query: string) => `\
Generate a concise summary (2-3 sentences) of the research contributions and expertise of the following author based on their recent publications.
Highlight key topics, notable works, and any significant impact in their field.
Follow the timeline of the publications to illustrate the author's research journey.

The query used to get the author and publications was: "${query}". Relate the summary to the query where possible.

Write it in portuguese.
Do not include any extranous text like confirmations or disclaimers. Just answer with the summary.

Author Name: ${author.display_name}
Works: ${JSON.stringify(author.works_list)}
`;

export async function generateAuthorSummary(
  author: AuthorRankingResult,
  query: string
) {
  const prompt = promptGenerator(author, query);

  const response = await client.models.generateContent({
    model: "gemini-2.5-flash-lite",
    contents: [prompt],
    config: {
      temperature: 0.2,
      maxOutputTokens: 256,
      responseMimeType: "text/plain",
    },
  });

  return response.text;
}

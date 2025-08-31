import { streamMessageSchema, type StreamMessageSchema } from "./contracts";

const searchUrl = `${import.meta.env.PUBLIC_PAPERTRAIL_API_URL}/search`;

type StreamMessageData = StreamMessageSchema["data"];
type Listeners = {
  onMessage?: (data: StreamMessageData) => void;
  onError?: () => void;
  onFinish?: () => void;
};

export function createSearchStream(query: string, listeners: Listeners) {
  const url = new URL(searchUrl);
  url.searchParams.set("query", query);

  const source = new EventSource(url.toString());

  source.addEventListener("message", (event) => {
    if (listeners.onMessage) {
      const jsonParsed = JSON.parse(event.data);
      const parsed = streamMessageSchema.shape.data.safeParse(jsonParsed);
      if (parsed.success) {
        listeners.onMessage(parsed.data);
      } else {
        console.error("Invalid stream message", parsed.error);
      }
    }
  });

  source.addEventListener("finish", () => {
    if (listeners.onFinish) {
      listeners.onFinish();
    }
    source.close();
  });

  source.addEventListener("error", () => {
    if (listeners.onError) {
      listeners.onError();
    }
    source.close();
  });

  return source;
}

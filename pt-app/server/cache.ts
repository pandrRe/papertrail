import { RootDatabase, open } from "lmdb";

const lmdb = open({
  path: process.env.LMDB_PATH || "./.data/lmdb",
  compression: true,
});

export type CacheEntry<T> = {
  timestamp: number;
  ttl: number;
  content: T;
};
export const DEFAULT_CACHE_TTL = 1000 * 60 * 24; // 24 hours

export function getCachedValue<T>(key: string): T | undefined {
  const entry = lmdb.get(key) as CacheEntry<T> | undefined;
  if (entry) {
    const isExpired = Date.now() - entry.timestamp > DEFAULT_CACHE_TTL;
    if (!isExpired) {
      return entry.content;
    }
  }
  return undefined;
}

export async function putCachedValue<T>(key: string, content: T, ttl = DEFAULT_CACHE_TTL) {
  const entry: CacheEntry<T> = {
    timestamp: Date.now(),
    ttl,
    content,
  };
  await lmdb.put(key, entry);
}

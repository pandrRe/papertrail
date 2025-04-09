import client from '@kubb/plugin-client/clients/fetch'
import type { CacheGetQueryResponse, CacheGetPathParams, CacheGet422 } from '../types/CacheGet.ts'
import type { RequestConfig, ResponseErrorConfig } from '@kubb/plugin-client/clients/fetch'
import type { QueryKey, UseSuspenseQueryOptions, UseSuspenseQueryResult } from '@tanstack/react-query'
import { cacheGetQueryResponseSchema } from '../zod/cacheGetSchema.ts'
import { queryOptions, useSuspenseQuery } from '@tanstack/react-query'

export const cacheGetSuspenseQueryKey = (scope: CacheGetPathParams['scope'], key: CacheGetPathParams['key']) =>
  [{ url: '/cache/:scope/:key', params: { scope: scope, key: key } }] as const

export type CacheGetSuspenseQueryKey = ReturnType<typeof cacheGetSuspenseQueryKey>

/**
 * @summary Cache Get
 * {@link /cache/:scope/:key}
 */
export async function cacheGetSuspense(
  scope: CacheGetPathParams['scope'],
  key: CacheGetPathParams['key'],
  config: Partial<RequestConfig> & { client?: typeof client } = {},
) {
  const { client: request = client, ...requestConfig } = config

  const res = await request<CacheGetQueryResponse, ResponseErrorConfig<CacheGet422>, unknown>({
    method: 'GET',
    url: `/cache/${scope}/${key}`,
    ...requestConfig,
  })
  return cacheGetQueryResponseSchema.parse(res.data)
}

export function cacheGetSuspenseQueryOptions(
  scope: CacheGetPathParams['scope'],
  key: CacheGetPathParams['key'],
  config: Partial<RequestConfig> & { client?: typeof client } = {},
) {
  const queryKey = cacheGetSuspenseQueryKey(scope, key)
  return queryOptions<CacheGetQueryResponse, ResponseErrorConfig<CacheGet422>, CacheGetQueryResponse, typeof queryKey>({
    enabled: !!(scope && key),
    queryKey,
    queryFn: async ({ signal }) => {
      config.signal = signal
      return cacheGetSuspense(scope, key, config)
    },
  })
}

/**
 * @summary Cache Get
 * {@link /cache/:scope/:key}
 */
export function useCacheGetSuspense<TData = CacheGetQueryResponse, TQueryData = CacheGetQueryResponse, TQueryKey extends QueryKey = CacheGetSuspenseQueryKey>(
  scope: CacheGetPathParams['scope'],
  key: CacheGetPathParams['key'],
  options: {
    query?: Partial<UseSuspenseQueryOptions<CacheGetQueryResponse, ResponseErrorConfig<CacheGet422>, TData, TQueryKey>>
    client?: Partial<RequestConfig> & { client?: typeof client }
  } = {},
) {
  const { query: queryOptions, client: config = {} } = options ?? {}
  const queryKey = queryOptions?.queryKey ?? cacheGetSuspenseQueryKey(scope, key)

  const query = useSuspenseQuery({
    ...(cacheGetSuspenseQueryOptions(scope, key, config) as unknown as UseSuspenseQueryOptions),
    queryKey,
    ...(queryOptions as unknown as Omit<UseSuspenseQueryOptions, 'queryKey'>),
  }) as UseSuspenseQueryResult<TData, ResponseErrorConfig<CacheGet422>> & { queryKey: TQueryKey }

  query.queryKey = queryKey as TQueryKey

  return query
}
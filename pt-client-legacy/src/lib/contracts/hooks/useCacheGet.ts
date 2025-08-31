import client from '@kubb/plugin-client/clients/fetch'
import type { CacheGetQueryResponse, CacheGetPathParams, CacheGet422 } from '../types/CacheGet.ts'
import type { RequestConfig, ResponseErrorConfig } from '@kubb/plugin-client/clients/fetch'
import type { QueryKey, QueryObserverOptions, UseQueryResult } from '@tanstack/react-query'
import { cacheGetQueryResponseSchema } from '../zod/cacheGetSchema.ts'
import { queryOptions, useQuery } from '@tanstack/react-query'

export const cacheGetQueryKey = (scope: CacheGetPathParams['scope'], key: CacheGetPathParams['key']) =>
  [{ url: '/cache/:scope/:key', params: { scope: scope, key: key } }] as const

export type CacheGetQueryKey = ReturnType<typeof cacheGetQueryKey>

/**
 * @summary Cache Get
 * {@link /cache/:scope/:key}
 */
export async function cacheGet(
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

export function cacheGetQueryOptions(
  scope: CacheGetPathParams['scope'],
  key: CacheGetPathParams['key'],
  config: Partial<RequestConfig> & { client?: typeof client } = {},
) {
  const queryKey = cacheGetQueryKey(scope, key)
  return queryOptions<CacheGetQueryResponse, ResponseErrorConfig<CacheGet422>, CacheGetQueryResponse, typeof queryKey>({
    enabled: !!(scope && key),
    queryKey,
    queryFn: async ({ signal }) => {
      config.signal = signal
      return cacheGet(scope, key, config)
    },
  })
}

/**
 * @summary Cache Get
 * {@link /cache/:scope/:key}
 */
export function useCacheGet<TData = CacheGetQueryResponse, TQueryData = CacheGetQueryResponse, TQueryKey extends QueryKey = CacheGetQueryKey>(
  scope: CacheGetPathParams['scope'],
  key: CacheGetPathParams['key'],
  options: {
    query?: Partial<QueryObserverOptions<CacheGetQueryResponse, ResponseErrorConfig<CacheGet422>, TData, TQueryData, TQueryKey>>
    client?: Partial<RequestConfig> & { client?: typeof client }
  } = {},
) {
  const { query: queryOptions, client: config = {} } = options ?? {}
  const queryKey = queryOptions?.queryKey ?? cacheGetQueryKey(scope, key)

  const query = useQuery({
    ...(cacheGetQueryOptions(scope, key, config) as unknown as QueryObserverOptions),
    queryKey,
    ...(queryOptions as unknown as Omit<QueryObserverOptions, 'queryKey'>),
  }) as UseQueryResult<TData, ResponseErrorConfig<CacheGet422>> & { queryKey: TQueryKey }

  query.queryKey = queryKey as TQueryKey

  return query
}
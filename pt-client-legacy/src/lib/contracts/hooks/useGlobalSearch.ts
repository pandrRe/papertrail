import client from '@kubb/plugin-client/clients/fetch'
import type { GlobalSearchQueryResponse, GlobalSearchQueryParams, GlobalSearch422 } from '../types/GlobalSearch.ts'
import type { RequestConfig, ResponseErrorConfig } from '@kubb/plugin-client/clients/fetch'
import type { QueryKey, QueryObserverOptions, UseQueryResult } from '@tanstack/react-query'
import { globalSearchQueryResponseSchema } from '../zod/globalSearchSchema.ts'
import { queryOptions, useQuery } from '@tanstack/react-query'

export const globalSearchQueryKey = (params: GlobalSearchQueryParams) => [{ url: '/search' }, ...(params ? [params] : [])] as const

export type GlobalSearchQueryKey = ReturnType<typeof globalSearchQueryKey>

/**
 * @summary Search
 * {@link /search}
 */
export async function globalSearch(params: GlobalSearchQueryParams, config: Partial<RequestConfig> & { client?: typeof client } = {}) {
  const { client: request = client, ...requestConfig } = config

  const res = await request<GlobalSearchQueryResponse, ResponseErrorConfig<GlobalSearch422>, unknown>({
    method: 'GET',
    url: `/search`,
    params,
    ...requestConfig,
  })
  return globalSearchQueryResponseSchema.parse(res.data)
}

export function globalSearchQueryOptions(params: GlobalSearchQueryParams, config: Partial<RequestConfig> & { client?: typeof client } = {}) {
  const queryKey = globalSearchQueryKey(params)
  return queryOptions<GlobalSearchQueryResponse, ResponseErrorConfig<GlobalSearch422>, GlobalSearchQueryResponse, typeof queryKey>({
    enabled: !!params,
    queryKey,
    queryFn: async ({ signal }) => {
      config.signal = signal
      return globalSearch(params, config)
    },
  })
}

/**
 * @summary Search
 * {@link /search}
 */
export function useGlobalSearch<TData = GlobalSearchQueryResponse, TQueryData = GlobalSearchQueryResponse, TQueryKey extends QueryKey = GlobalSearchQueryKey>(
  params: GlobalSearchQueryParams,
  options: {
    query?: Partial<QueryObserverOptions<GlobalSearchQueryResponse, ResponseErrorConfig<GlobalSearch422>, TData, TQueryData, TQueryKey>>
    client?: Partial<RequestConfig> & { client?: typeof client }
  } = {},
) {
  const { query: queryOptions, client: config = {} } = options ?? {}
  const queryKey = queryOptions?.queryKey ?? globalSearchQueryKey(params)

  const query = useQuery({
    ...(globalSearchQueryOptions(params, config) as unknown as QueryObserverOptions),
    queryKey,
    ...(queryOptions as unknown as Omit<QueryObserverOptions, 'queryKey'>),
  }) as UseQueryResult<TData, ResponseErrorConfig<GlobalSearch422>> & { queryKey: TQueryKey }

  query.queryKey = queryKey as TQueryKey

  return query
}
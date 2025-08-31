import client from '@kubb/plugin-client/clients/fetch'
import type { GlobalSearchQueryResponse, GlobalSearchQueryParams, GlobalSearch422 } from '../types/GlobalSearch.ts'
import type { RequestConfig, ResponseErrorConfig } from '@kubb/plugin-client/clients/fetch'
import type { QueryKey, UseSuspenseQueryOptions, UseSuspenseQueryResult } from '@tanstack/react-query'
import { globalSearchQueryResponseSchema } from '../zod/globalSearchSchema.ts'
import { queryOptions, useSuspenseQuery } from '@tanstack/react-query'

export const globalSearchSuspenseQueryKey = (params: GlobalSearchQueryParams) => [{ url: '/search' }, ...(params ? [params] : [])] as const

export type GlobalSearchSuspenseQueryKey = ReturnType<typeof globalSearchSuspenseQueryKey>

/**
 * @summary Search
 * {@link /search}
 */
export async function globalSearchSuspense(params: GlobalSearchQueryParams, config: Partial<RequestConfig> & { client?: typeof client } = {}) {
  const { client: request = client, ...requestConfig } = config

  const res = await request<GlobalSearchQueryResponse, ResponseErrorConfig<GlobalSearch422>, unknown>({
    method: 'GET',
    url: `/search`,
    params,
    ...requestConfig,
  })
  return globalSearchQueryResponseSchema.parse(res.data)
}

export function globalSearchSuspenseQueryOptions(params: GlobalSearchQueryParams, config: Partial<RequestConfig> & { client?: typeof client } = {}) {
  const queryKey = globalSearchSuspenseQueryKey(params)
  return queryOptions<GlobalSearchQueryResponse, ResponseErrorConfig<GlobalSearch422>, GlobalSearchQueryResponse, typeof queryKey>({
    enabled: !!params,
    queryKey,
    queryFn: async ({ signal }) => {
      config.signal = signal
      return globalSearchSuspense(params, config)
    },
  })
}

/**
 * @summary Search
 * {@link /search}
 */
export function useGlobalSearchSuspense<
  TData = GlobalSearchQueryResponse,
  TQueryData = GlobalSearchQueryResponse,
  TQueryKey extends QueryKey = GlobalSearchSuspenseQueryKey,
>(
  params: GlobalSearchQueryParams,
  options: {
    query?: Partial<UseSuspenseQueryOptions<GlobalSearchQueryResponse, ResponseErrorConfig<GlobalSearch422>, TData, TQueryKey>>
    client?: Partial<RequestConfig> & { client?: typeof client }
  } = {},
) {
  const { query: queryOptions, client: config = {} } = options ?? {}
  const queryKey = queryOptions?.queryKey ?? globalSearchSuspenseQueryKey(params)

  const query = useSuspenseQuery({
    ...(globalSearchSuspenseQueryOptions(params, config) as unknown as UseSuspenseQueryOptions),
    queryKey,
    ...(queryOptions as unknown as Omit<UseSuspenseQueryOptions, 'queryKey'>),
  }) as UseSuspenseQueryResult<TData, ResponseErrorConfig<GlobalSearch422>> & { queryKey: TQueryKey }

  query.queryKey = queryKey as TQueryKey

  return query
}
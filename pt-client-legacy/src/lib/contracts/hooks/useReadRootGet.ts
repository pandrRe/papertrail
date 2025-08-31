import client from '@kubb/plugin-client/clients/fetch'
import type { ReadRootGetQueryResponse } from '../types/ReadRootGet.ts'
import type { RequestConfig, ResponseErrorConfig } from '@kubb/plugin-client/clients/fetch'
import type { QueryKey, QueryObserverOptions, UseQueryResult } from '@tanstack/react-query'
import { readRootGetQueryResponseSchema } from '../zod/readRootGetSchema.ts'
import { queryOptions, useQuery } from '@tanstack/react-query'

export const readRootGetQueryKey = () => [{ url: '/' }] as const

export type ReadRootGetQueryKey = ReturnType<typeof readRootGetQueryKey>

/**
 * @summary Read Root
 * {@link /}
 */
export async function readRootGet(config: Partial<RequestConfig> & { client?: typeof client } = {}) {
  const { client: request = client, ...requestConfig } = config

  const res = await request<ReadRootGetQueryResponse, ResponseErrorConfig<Error>, unknown>({ method: 'GET', url: `/`, ...requestConfig })
  return readRootGetQueryResponseSchema.parse(res.data)
}

export function readRootGetQueryOptions(config: Partial<RequestConfig> & { client?: typeof client } = {}) {
  const queryKey = readRootGetQueryKey()
  return queryOptions<ReadRootGetQueryResponse, ResponseErrorConfig<Error>, ReadRootGetQueryResponse, typeof queryKey>({
    queryKey,
    queryFn: async ({ signal }) => {
      config.signal = signal
      return readRootGet(config)
    },
  })
}

/**
 * @summary Read Root
 * {@link /}
 */
export function useReadRootGet<TData = ReadRootGetQueryResponse, TQueryData = ReadRootGetQueryResponse, TQueryKey extends QueryKey = ReadRootGetQueryKey>(
  options: {
    query?: Partial<QueryObserverOptions<ReadRootGetQueryResponse, ResponseErrorConfig<Error>, TData, TQueryData, TQueryKey>>
    client?: Partial<RequestConfig> & { client?: typeof client }
  } = {},
) {
  const { query: queryOptions, client: config = {} } = options ?? {}
  const queryKey = queryOptions?.queryKey ?? readRootGetQueryKey()

  const query = useQuery({
    ...(readRootGetQueryOptions(config) as unknown as QueryObserverOptions),
    queryKey,
    ...(queryOptions as unknown as Omit<QueryObserverOptions, 'queryKey'>),
  }) as UseQueryResult<TData, ResponseErrorConfig<Error>> & { queryKey: TQueryKey }

  query.queryKey = queryKey as TQueryKey

  return query
}
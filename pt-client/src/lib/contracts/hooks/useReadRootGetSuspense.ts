import client from '@kubb/plugin-client/clients/fetch'
import type { ReadRootGetQueryResponse } from '../types/ReadRootGet.ts'
import type { RequestConfig, ResponseErrorConfig } from '@kubb/plugin-client/clients/fetch'
import type { QueryKey, UseSuspenseQueryOptions, UseSuspenseQueryResult } from '@tanstack/react-query'
import { readRootGetQueryResponseSchema } from '../zod/readRootGetSchema.ts'
import { queryOptions, useSuspenseQuery } from '@tanstack/react-query'

export const readRootGetSuspenseQueryKey = () => [{ url: '/' }] as const

export type ReadRootGetSuspenseQueryKey = ReturnType<typeof readRootGetSuspenseQueryKey>

/**
 * @summary Read Root
 * {@link /}
 */
export async function readRootGetSuspense(config: Partial<RequestConfig> & { client?: typeof client } = {}) {
  const { client: request = client, ...requestConfig } = config

  const res = await request<ReadRootGetQueryResponse, ResponseErrorConfig<Error>, unknown>({ method: 'GET', url: `/`, ...requestConfig })
  return readRootGetQueryResponseSchema.parse(res.data)
}

export function readRootGetSuspenseQueryOptions(config: Partial<RequestConfig> & { client?: typeof client } = {}) {
  const queryKey = readRootGetSuspenseQueryKey()
  return queryOptions<ReadRootGetQueryResponse, ResponseErrorConfig<Error>, ReadRootGetQueryResponse, typeof queryKey>({
    queryKey,
    queryFn: async ({ signal }) => {
      config.signal = signal
      return readRootGetSuspense(config)
    },
  })
}

/**
 * @summary Read Root
 * {@link /}
 */
export function useReadRootGetSuspense<
  TData = ReadRootGetQueryResponse,
  TQueryData = ReadRootGetQueryResponse,
  TQueryKey extends QueryKey = ReadRootGetSuspenseQueryKey,
>(
  options: {
    query?: Partial<UseSuspenseQueryOptions<ReadRootGetQueryResponse, ResponseErrorConfig<Error>, TData, TQueryKey>>
    client?: Partial<RequestConfig> & { client?: typeof client }
  } = {},
) {
  const { query: queryOptions, client: config = {} } = options ?? {}
  const queryKey = queryOptions?.queryKey ?? readRootGetSuspenseQueryKey()

  const query = useSuspenseQuery({
    ...(readRootGetSuspenseQueryOptions(config) as unknown as UseSuspenseQueryOptions),
    queryKey,
    ...(queryOptions as unknown as Omit<UseSuspenseQueryOptions, 'queryKey'>),
  }) as UseSuspenseQueryResult<TData, ResponseErrorConfig<Error>> & { queryKey: TQueryKey }

  query.queryKey = queryKey as TQueryKey

  return query
}
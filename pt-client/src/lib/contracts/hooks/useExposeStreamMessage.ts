import client from '@kubb/plugin-client/clients/fetch'
import type { ExposeStreamMessageQueryResponse } from '../types/ExposeStreamMessage.ts'
import type { RequestConfig, ResponseErrorConfig } from '@kubb/plugin-client/clients/fetch'
import type { QueryKey, QueryObserverOptions, UseQueryResult } from '@tanstack/react-query'
import { exposeStreamMessageQueryResponseSchema } from '../zod/exposeStreamMessageSchema.ts'
import { queryOptions, useQuery } from '@tanstack/react-query'

export const exposeStreamMessageQueryKey = () => [{ url: '/expose-stream-message' }] as const

export type ExposeStreamMessageQueryKey = ReturnType<typeof exposeStreamMessageQueryKey>

/**
 * @summary Expose Stream Message
 * {@link /expose-stream-message}
 */
export async function exposeStreamMessage(config: Partial<RequestConfig> & { client?: typeof client } = {}) {
  const { client: request = client, ...requestConfig } = config

  const res = await request<ExposeStreamMessageQueryResponse, ResponseErrorConfig<Error>, unknown>({
    method: 'GET',
    url: `/expose-stream-message`,
    ...requestConfig,
  })
  return exposeStreamMessageQueryResponseSchema.parse(res.data)
}

export function exposeStreamMessageQueryOptions(config: Partial<RequestConfig> & { client?: typeof client } = {}) {
  const queryKey = exposeStreamMessageQueryKey()
  return queryOptions<ExposeStreamMessageQueryResponse, ResponseErrorConfig<Error>, ExposeStreamMessageQueryResponse, typeof queryKey>({
    queryKey,
    queryFn: async ({ signal }) => {
      config.signal = signal
      return exposeStreamMessage(config)
    },
  })
}

/**
 * @summary Expose Stream Message
 * {@link /expose-stream-message}
 */
export function useExposeStreamMessage<
  TData = ExposeStreamMessageQueryResponse,
  TQueryData = ExposeStreamMessageQueryResponse,
  TQueryKey extends QueryKey = ExposeStreamMessageQueryKey,
>(
  options: {
    query?: Partial<QueryObserverOptions<ExposeStreamMessageQueryResponse, ResponseErrorConfig<Error>, TData, TQueryData, TQueryKey>>
    client?: Partial<RequestConfig> & { client?: typeof client }
  } = {},
) {
  const { query: queryOptions, client: config = {} } = options ?? {}
  const queryKey = queryOptions?.queryKey ?? exposeStreamMessageQueryKey()

  const query = useQuery({
    ...(exposeStreamMessageQueryOptions(config) as unknown as QueryObserverOptions),
    queryKey,
    ...(queryOptions as unknown as Omit<QueryObserverOptions, 'queryKey'>),
  }) as UseQueryResult<TData, ResponseErrorConfig<Error>> & { queryKey: TQueryKey }

  query.queryKey = queryKey as TQueryKey

  return query
}
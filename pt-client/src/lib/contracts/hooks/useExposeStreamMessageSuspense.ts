import client from '@kubb/plugin-client/clients/fetch'
import type { ExposeStreamMessageQueryResponse } from '../types/ExposeStreamMessage.ts'
import type { RequestConfig, ResponseErrorConfig } from '@kubb/plugin-client/clients/fetch'
import type { QueryKey, UseSuspenseQueryOptions, UseSuspenseQueryResult } from '@tanstack/react-query'
import { exposeStreamMessageQueryResponseSchema } from '../zod/exposeStreamMessageSchema.ts'
import { queryOptions, useSuspenseQuery } from '@tanstack/react-query'

export const exposeStreamMessageSuspenseQueryKey = () => [{ url: '/expose-stream-message' }] as const

export type ExposeStreamMessageSuspenseQueryKey = ReturnType<typeof exposeStreamMessageSuspenseQueryKey>

/**
 * @summary Expose Stream Message
 * {@link /expose-stream-message}
 */
export async function exposeStreamMessageSuspense(config: Partial<RequestConfig> & { client?: typeof client } = {}) {
  const { client: request = client, ...requestConfig } = config

  const res = await request<ExposeStreamMessageQueryResponse, ResponseErrorConfig<Error>, unknown>({
    method: 'GET',
    url: `/expose-stream-message`,
    ...requestConfig,
  })
  return exposeStreamMessageQueryResponseSchema.parse(res.data)
}

export function exposeStreamMessageSuspenseQueryOptions(config: Partial<RequestConfig> & { client?: typeof client } = {}) {
  const queryKey = exposeStreamMessageSuspenseQueryKey()
  return queryOptions<ExposeStreamMessageQueryResponse, ResponseErrorConfig<Error>, ExposeStreamMessageQueryResponse, typeof queryKey>({
    queryKey,
    queryFn: async ({ signal }) => {
      config.signal = signal
      return exposeStreamMessageSuspense(config)
    },
  })
}

/**
 * @summary Expose Stream Message
 * {@link /expose-stream-message}
 */
export function useExposeStreamMessageSuspense<
  TData = ExposeStreamMessageQueryResponse,
  TQueryData = ExposeStreamMessageQueryResponse,
  TQueryKey extends QueryKey = ExposeStreamMessageSuspenseQueryKey,
>(
  options: {
    query?: Partial<UseSuspenseQueryOptions<ExposeStreamMessageQueryResponse, ResponseErrorConfig<Error>, TData, TQueryKey>>
    client?: Partial<RequestConfig> & { client?: typeof client }
  } = {},
) {
  const { query: queryOptions, client: config = {} } = options ?? {}
  const queryKey = queryOptions?.queryKey ?? exposeStreamMessageSuspenseQueryKey()

  const query = useSuspenseQuery({
    ...(exposeStreamMessageSuspenseQueryOptions(config) as unknown as UseSuspenseQueryOptions),
    queryKey,
    ...(queryOptions as unknown as Omit<UseSuspenseQueryOptions, 'queryKey'>),
  }) as UseSuspenseQueryResult<TData, ResponseErrorConfig<Error>> & { queryKey: TQueryKey }

  query.queryKey = queryKey as TQueryKey

  return query
}
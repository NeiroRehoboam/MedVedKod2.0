import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import {
  aiSessionsList,
  aiSessionsRetrieve,
  aiSessionsStartCreate,
  getAiSessionsListQueryKey,
  getAiSessionsRetrieveQueryKey,
  getAiSessionsInitialQuestionRetrieveQueryKey,
  getAiSessionsResultRetrieveQueryKey,
  useAiSessionsDestroy,
  useAiSessionsInitialQuestionRetrieve,
  useAiSessionsResultRetrieve,
} from "@/api/generated/ai-sessions/ai-sessions"

export function useAiSessions() {
  return useQuery({
    queryKey: getAiSessionsListQueryKey(),
    queryFn: async () => {
      const response = await aiSessionsList()
      return response.data
    },
    staleTime: 60_000,
    retry: 1,
  })
}

export function useStartAiSession() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => aiSessionsStartCreate(),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: getAiSessionsListQueryKey(),
      })
    },
  })
}

export function useAiSession(id?: string) {
  return useQuery({
    queryKey: getAiSessionsRetrieveQueryKey(id ?? ""),
    queryFn: async () => {
      const response = await aiSessionsRetrieve(id!)
      return response.data
    },
    enabled: Boolean(id),
    gcTime: 0,
    retry: 1,
    staleTime: 60_000,
  })
}

export function useDeleteAiSession() {
  const queryClient = useQueryClient()

  return useAiSessionsDestroy({
    mutation: {
      onSuccess: (_response, { id }) => {
        void queryClient.invalidateQueries({
          queryKey: getAiSessionsListQueryKey(),
        })
        for (const queryKey of [
          getAiSessionsRetrieveQueryKey(id),
          getAiSessionsInitialQuestionRetrieveQueryKey(Number(id)),
          getAiSessionsResultRetrieveQueryKey(Number(id)),
        ]) {
          queryClient.removeQueries({ queryKey, exact: true })
        }
      },
    },
  })
}

export function useInitialQuestion(sessionId?: string, enabled = true) {
  const id = Number(sessionId)

  return useAiSessionsInitialQuestionRetrieve(id, {
    query: {
      enabled: enabled && Number.isInteger(id) && id > 0,
    },
  })
}

export function useAiSessionResult(sessionId?: string, enabled = true) {
  const id = Number(sessionId)

  return useAiSessionsResultRetrieve(id, {
    query: {
      enabled: enabled && Number.isInteger(id) && id > 0,
      staleTime: 60_000,
      retry: 1,
    },
  })
}

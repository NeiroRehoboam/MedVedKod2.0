import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import {
  aiSessionsList,
  aiSessionsStartCreate,
  getAiSessionsListQueryKey,
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

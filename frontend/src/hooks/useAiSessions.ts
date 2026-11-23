import { useQuery } from "@tanstack/react-query"

import {
  aiSessionsList,
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

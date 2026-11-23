
import { useQuery } from "@tanstack/react-query"

import { anamnesisAnamnesisRetrieve } from
  "@/api/generated/anamnesis/anamnesis"

import { ApiError } from "@/api/fetcher"

export const currentAnamnesisQueryKey = ["currentAnamnesis"]

export function useCurrentAnamnesis() {
  return useQuery({
    queryKey: currentAnamnesisQueryKey,

    queryFn: async () => {
      try {
        const response = await anamnesisAnamnesisRetrieve()
        return response.data
      } catch (error) {
        // Пациент ещё не заполнял анамнез
        if (error instanceof ApiError && error.status === 404) {
          return null
        }

        throw error
      }
    },

    retry: false,
    staleTime: 60_000,
  })
}

import { useQuery } from "@tanstack/react-query"

import {
  dictionariesChronicDiseasesList,
  dictionariesHereditaryList,
  dictionariesAllergensList,
  dictionariesMedicationsList,
} from "@/api/generated/dictionaries/dictionaries"

export function useChronicDiseases() {
  return useQuery({
    queryKey: ["dictionaries", "chronic-diseases"],
    queryFn: async () => {
      const response = await dictionariesChronicDiseasesList()
      return response.data
    },
    staleTime: 10 * 60 * 1000,
  })
}

export function useHereditaryDiseases() {
  return useQuery({
    queryKey: ["dictionaries", "hereditary-diseases"],
    queryFn: async () => {
      const response = await dictionariesHereditaryList()
      return response.data
    },
    staleTime: 10 * 60 * 1000,
  })
}

export function useAllergies() {
  return useQuery({
    queryKey: ["dictionaries", "allergies"],
    queryFn: async () => {
      const response = await dictionariesAllergensList()
      return response.data
    },
    staleTime: 10 * 60 * 1000,
  })
}

export function useMedications() {
  return useQuery({
    queryKey: ["dictionaries", "medications"],
    queryFn: async () => {
      const response = await dictionariesMedicationsList()
      return response.data
    },
    staleTime: 10 * 60 * 1000,
  })
}

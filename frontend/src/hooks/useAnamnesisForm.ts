import { useEffect, useState, type FormEvent } from "react"
import { useSnackbar } from "@maxhub/max-ui"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { anamnesisAnamnesisCreate } from "@/api/generated/anamnesis/anamnesis"
import {
  emptyAnamnesis,
  createAnamnesisPayload,
  mapAnamnesisToForm,
  type AnamnesisData,
  type SelectFieldKey,
} from "@/lib/anamnesis"
import {
  useAllergies,
  useChronicDiseases,
  useHereditaryDiseases,
  useMedications,
} from "@/hooks/useAnamnesisDictionaries"
import {
  currentAnamnesisQueryKey,
  useCurrentAnamnesis,
} from "@/hooks/useCurrentAnamnesis"

type DictionaryItem = {
  id: number
  name: string
}

const toOptions = (items: DictionaryItem[] = []) =>
  items.map((item) => ({
    label: item.name,
    value: String(item.id),
  }))

export function useAnamnesisForm(
  onSuccess?: (data: AnamnesisData) => void
) {
  const { showSnackbar } = useSnackbar()

  const chronicDiseases = useChronicDiseases()
  const hereditaryDiseases = useHereditaryDiseases()
  const allergies = useAllergies()
  const medications = useMedications()

  const queryClient = useQueryClient()
  const anamnesisQuery = useCurrentAnamnesis()

  const [data, setData] = useState<AnamnesisData>(emptyAnamnesis)
  const [initialized, setInitialized] = useState(false)
  const [error, setError] = useState(false)

  useEffect(() => {
    // Initialize once so cache updates cannot overwrite unsaved edits.
    if (!anamnesisQuery.isSuccess || initialized) return

    if (anamnesisQuery.data) {
      setData(mapAnamnesisToForm(anamnesisQuery.data))
    }

    setInitialized(true)
  }, [anamnesisQuery.isSuccess, anamnesisQuery.data, initialized])

  const saveMutation = useMutation({
    mutationFn: async (formData: AnamnesisData) => {
      const payload = createAnamnesisPayload(formData)

      return anamnesisAnamnesisCreate(payload)
    },

    onSuccess: (response, formData) => {
      queryClient.setQueryData(currentAnamnesisQueryKey, response.data)

      setError(false)

      showSnackbar({
        text: "Анамнез сохранён",
        caption: "Ваши данные успешно сохранены",
        duration: 3000,
        placement: "top-center",
        offset: 16,
      })

      onSuccess?.(formData)
    },

    onError: (error) => {
      console.error("Ошибка сохранения анамнеза:", error)
      setError(true)
    },
  })

  const update = <K extends keyof AnamnesisData>(
    key: K,
    value: AnamnesisData[K]
  ) => {
    setData((prev) => ({ ...prev, [key]: value }))
    setError(false)
  }

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (saveMutation.isPending) return

    setError(false)
    saveMutation.mutate(data)
  }

  const selectedMedicationValues = data.medications.map((item) => item.value)

  const updateMedications = (values: string[]) => {
    setData((prev) => ({
      ...prev,
      medications: values.map((value) => {
        const existing = prev.medications.find((item) => item.value === value)

        return (
          existing ?? {
            value,
            intake_mode: "AS_NEEDED" as const,
          }
        )
      }),
    }))

    setError(false)
  }

  const updateSelect = (key: SelectFieldKey, value: string) => {
    switch (key) {
      case "pregnancy":
      case "lactation":
        if (
          value === "YES" ||
          value === "NO" ||
          value === "UNKNOWN" ||
          value === "NA"
        ) {
          update(key, value)
        }
        break

      case "smoking_status":
        if (value === "never" || value === "former" || value === "current") {
          update(key, value)
        } else if (!value) {
          update(key, null)
        }
        break

      case "alcohol_status":
        if (
          value === "never" ||
          value === "sometimes" ||
          value === "regularly"
        ) {
          update(key, value)
        } else if (!value) {
          update(key, null)
        }
        break
    }
  }

  return {
    data,
    initialized,
    error,
    anamnesisQuery,
    chronicDiseases: {
      options: toOptions(chronicDiseases.data),
      isPending: chronicDiseases.isPending,
    },
    allergies: {
      options: toOptions(allergies.data),
      isPending: allergies.isPending,
    },
    hereditaryDiseases: {
      options: toOptions(hereditaryDiseases.data),
      isPending: hereditaryDiseases.isPending,
    },
    medications: {
      options: toOptions(medications.data),
      isPending: medications.isPending,
    },
    selectedMedicationValues,
    update,
    updateMedications,
    updateSelect,
    handleSubmit,
  }
}

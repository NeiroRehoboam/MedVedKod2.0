import { useEffect, useState, type FormEvent, type ReactNode } from "react"
import { MultiSelectField } from "./MultiSelectField"
import {
  emptyAnamnesis,
  readAnamnesis,
  type AnamnesisData,
} from "@/lib/anamnesis"
import { Button, Select, Spinner, Textarea, useSnackbar } from "@maxhub/max-ui"
import { FormLabel } from "./FormLabel"
import {
  useAllergies,
  useChronicDiseases,
  useHereditaryDiseases,
  useMedications,
} from "@/hooks/useAnamnesisDictionaries"
import {
  alcoholOptions,
  pregnancyOptions,
  smokingOptions,
} from "@/data/anamnesis.options"
import { MedicationDetailsDialog } from "./MedicationDetailsDialog"
import { PageDescription } from "../typography"
import { useMutation, useQueryClient } from "@tanstack/react-query"

import { anamnesisAnamnesisCreate } from "@/api/generated/anamnesis/anamnesis"
import { createAnamnesisPayload } from "@/lib/anamnesisPayload"
import {
  currentAnamnesisQueryKey,
  useCurrentAnamnesis,
} from "@/hooks/useCurrentAnamnesis"
import { mapAnamnesisToForm } from "@/lib/anamnesisMapper"

type AnamnesisFormProps = {
  children?: ReactNode
  onSuccess?: (data: AnamnesisData) => void
  className?: string
}

type SelectFieldKey =
  "pregnancy" | "lactation" | "smoking_status" | "alcohol_status"

const selectFields: {
  key: SelectFieldKey
  label: string
  options: { label: string; value: string }[]
}[] = [
  {
    key: "pregnancy",
    label: "Беременность",
    options: pregnancyOptions,
  },
  {
    key: "lactation",
    label: "Лактация",
    options: pregnancyOptions,
  },
  {
    key: "smoking_status",
    label: "Курение",
    options: smokingOptions,
  },
  {
    key: "alcohol_status",
    label: "Алкоголь",
    options: alcoholOptions,
  },
]

export function AnamnesisForm({
  children,
  onSuccess,
  className,
}: AnamnesisFormProps) {
  const { showSnackbar } = useSnackbar()

  const chronicDiseases = useChronicDiseases()
  const hereditaryDiseases = useHereditaryDiseases()
  const allergies = useAllergies()
  const medications = useMedications()
  const [medicationDialogOpen, setMedicationDialogOpen] = useState(false)

  const queryClient = useQueryClient()
  const anamnesisQuery = useCurrentAnamnesis()

  const [data, setData] = useState<AnamnesisData>(emptyAnamnesis)
  const [initialized, setInitialized] = useState(false)
  const [error, setError] = useState(false)
  useEffect(() => {
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

  type DictionaryItem = {
    id: number
    name: string
  }

  const toOptions = (items: DictionaryItem[] = []) =>
    items.map((item) => ({
      label: item.name,
      value: String(item.id),
    }))

  const medicationOptions = toOptions(medications.data)

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

  if (anamnesisQuery.isPending || !initialized) {
    if (anamnesisQuery.isError) {
      return (
        <div className="py-8 text-center">
          <PageDescription>Не удалось загрузить анамнез</PageDescription>

          <Button
            type="button"
            variant="secondary"
            size="medium"
            onClick={() => anamnesisQuery.refetch()}
            className="mx-auto mt-4"
          >
            Повторить
          </Button>
        </div>
      )
    }

    return (
      <div className="py-8 text-center">
        <Spinner />
      </div>
    )
  }
  return (
    <form className={className ?? "mt-8 space-y-7"} onSubmit={handleSubmit}>
      <MultiSelectField
        label="Хронические заболевания"
        options={toOptions(chronicDiseases.data)}
        value={data.diseases}
        onChange={(value) => update("diseases", value)}
        disabled={chronicDiseases.isPending}
      />

      <MultiSelectField
        label="Аллергии"
        options={toOptions(allergies.data)}
        value={data.allergies}
        onChange={(value) => update("allergies", value)}
        disabled={allergies.isPending}
      />

      <MultiSelectField
        label="Наследственные заболевания"
        options={toOptions(hereditaryDiseases.data)}
        value={data.heredity}
        onChange={(value) => update("heredity", value)}
        disabled={hereditaryDiseases.isPending}
      />

      <div>
        <MultiSelectField
          label="Принимаемые лекарства"
          options={medicationOptions}
          value={selectedMedicationValues}
          onChange={updateMedications}
          disabled={medications.isPending}
          action={
            <Button
              type="button"
              variant="ghost"
              size="xsmall"
              disabled={data.medications.length === 0}
              onClick={() => setMedicationDialogOpen(true)}
            >
              Уточнить приём
            </Button>
          }
        />

        <MedicationDetailsDialog
          open={medicationDialogOpen}
          onOpenChange={setMedicationDialogOpen}
          medications={data.medications}
          options={medicationOptions}
          onChange={(value) => update("medications", value)}
        />
      </div>

      <div>
        <FormLabel htmlFor="recent_events_notes">
          Госпитализации за последний год
        </FormLabel>

        <Textarea
          id="recent_events_notes"
          placeholder="Если были, опишите..."
          value={data.recent_events_notes}
          mode="secondary"
          onChange={(event) =>
            update("recent_events_notes", event.target.value)
          }
        />
      </div>

      {selectFields.map((field) => (
        <div key={field.key}>
          <FormLabel>{field.label}</FormLabel>

          <Select
            aria-label={field.label}
            value={data[field.key] ?? ""}
            onValueChange={(value: string) => updateSelect(field.key, value)}
            options={field.options}
            placeholder="Выберите вариант"
            size="large"
            mode="default"
            multiple={false}
            searchable={false}
            dropdownWidth="trigger"
            withClearButton
          />
        </div>
      ))}
      {error && (
        <p role="alert" className="text-max-text-negative">
          Не удалось сохранить анамнез. Попробуйте ещё раз.
        </p>
      )}

      {children}
    </form>
  )
}

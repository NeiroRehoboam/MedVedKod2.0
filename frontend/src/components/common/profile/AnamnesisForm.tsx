import { useState, type ReactNode } from "react"
import { MultiSelectField } from "./MultiSelectField"
import type { AnamnesisData, SelectFieldKey } from "@/lib/anamnesis"
import { Button, Select, Spinner, Textarea } from "@maxhub/max-ui"
import { FormLabel } from "./FormLabel"
import {
  alcoholOptions,
  pregnancyOptions,
  smokingOptions,
} from "@/data/anamnesis.options"
import { MedicationDetailsDialog } from "./MedicationDetailsDialog"
import { PageDescription } from "../typography"
import { useAnamnesisForm } from "@/hooks/useAnamnesisForm"

type AnamnesisFormProps = {
  children?: ReactNode
  onSuccess?: (data: AnamnesisData) => void
  className?: string
}

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
  const [medicationDialogOpen, setMedicationDialogOpen] = useState(false)
  const {
    data,
    initialized,
    error,
    anamnesisQuery,
    chronicDiseases,
    allergies,
    hereditaryDiseases,
    medications,
    selectedMedicationValues,
    update,
    updateMedications,
    updateSelect,
    handleSubmit,
  } = useAnamnesisForm(onSuccess)

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
        options={chronicDiseases.options}
        value={data.diseases}
        onChange={(value) => update("diseases", value)}
        disabled={chronicDiseases.isPending}
      />

      <MultiSelectField
        label="Аллергии"
        options={allergies.options}
        value={data.allergies}
        onChange={(value) => update("allergies", value)}
        disabled={allergies.isPending}
      />

      <MultiSelectField
        label="Наследственные заболевания"
        options={hereditaryDiseases.options}
        value={data.heredity}
        onChange={(value) => update("heredity", value)}
        disabled={hereditaryDiseases.isPending}
      />

      <div>
        <MultiSelectField
          label="Принимаемые лекарства"
          options={medications.options}
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
          options={medications.options}
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

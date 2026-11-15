import { useState, type FormEvent, type ReactNode } from "react"
import { MultiSelectField } from "./MultiSelectField"
import {
  readAnamnesis,
  saveAnamnesis,
  type AnamnesisData,
} from "@/lib/anamnesis"
import { mockFields, mockSelects } from "@/data/anamnesis.mock"
import { Select, Textarea, useSnackbar } from "@maxhub/max-ui"
import { FormLabel } from "./FormLabel"

type AnamnesisFormProps = {
  children?: ReactNode
  onSuccess?: (data: AnamnesisData) => void
  className?: string
}

export function AnamnesisForm({
  children,
  onSuccess,
  className,
}: AnamnesisFormProps) {
  const { showSnackbar } = useSnackbar()

  const [data, setData] = useState<AnamnesisData>(readAnamnesis)
  const [error, setError] = useState(false)

  const update = <K extends keyof AnamnesisData>(
    key: K,
    value: AnamnesisData[K]
  ) => {
    setData((prev) => ({ ...prev, [key]: value }))
    setError(false)
  }

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    try {
      saveAnamnesis(data)
      setError(false)

      showSnackbar({
        text: "Анамнез сохранён",
        caption: "Ваши данные успешно сохранены",
        duration: 3000,
        placement: "top-center",
        offset: 16,
      })

      onSuccess?.(data)
    } catch {
      setError(true)
    }
  }

  return (
    <form className={className ?? "mt-8 space-y-7"} onSubmit={handleSubmit}>
      {mockFields.map((field) => (
        <MultiSelectField
          key={field.key}
          label={field.label}
          options={[...field.options]}
          value={data[field.key]}
          onChange={(value) => update(field.key, value)}
        />
      ))}

      <div>
        <FormLabel htmlFor="surgeries">Операции за последний год</FormLabel>

        <Textarea
          id="surgeries"
          placeholder="Если были, опишите..."
          value={data.surgeries}
          mode="secondary"
          onChange={(event) => update("surgeries", event.target.value)}
        />
      </div>

      {mockSelects.map((field) => (
        <div key={field.key}>
          <FormLabel>{field.label}</FormLabel>

          <Select
            aria-label={field.label}
            value={data[field.key]}
            onValueChange={(value: string) => update(field.key, value)}
            options={field.options.map((option) => ({
              label: option,
              value: option,
            }))}
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

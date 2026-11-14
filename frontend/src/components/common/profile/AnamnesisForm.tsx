import { useState } from "react"
import { ArrowLeft, ArrowRight } from "lucide-react"
import { MultiSelectField } from "./MultiSelectField"
import { ProfileActions } from "./ProfileActions"
import {
  readAnamnesis,
  saveAnamnesis,
  type AnamnesisData,
} from "@/lib/anamnesis"
import { mockFields, mockSelects } from "@/data/anamnesis.mock"
import { Button, Select, Textarea, Typography } from "@maxhub/max-ui"

type AnamnesisFormProps = {
  onContinue?: () => void
  onBack?: () => void
}

export function AnamnesisForm({ onContinue, onBack }: AnamnesisFormProps) {
  const [data, setData] = useState<AnamnesisData>(readAnamnesis)
  const [status, setStatus] = useState<"idle" | "saved" | "error">("idle")

  const update = <K extends keyof AnamnesisData>(
    key: K,
    value: AnamnesisData[K]
  ) => {
    setData((prev) => ({ ...prev, [key]: value }))
    setStatus("idle")
  }

  return (
    <form
      className="mt-8 space-y-7"
      onSubmit={(e) => {
        e.preventDefault()
        try {
          saveAnamnesis(data)
          setStatus("saved")
          onContinue?.()
        } catch {
          setStatus("error")
        }
      }}
    >
      {mockFields.map((field) => (
        <MultiSelectField
          key={field.key}
          label={field.label}
          options={[...field.options]}
          value={data[field.key]}
          onChange={(value) => update(field.key, value)}
        />
      ))}

      <div className="space-y-3">
        <p>
          <Typography.Text variant="body" color="primary">
            Операции за последний год
          </Typography.Text>
        </p>

        <Textarea
          id="surgeries"
          placeholder="Если были, опишите..."
          value={data.surgeries}
          mode="secondary"
          onChange={(e) => update("surgeries", e.target.value)}
        />
      </div>

      {mockSelects.map((field) => (
        <div key={field.key} className="flex flex-col gap-3">
          <Typography.Text variant="body" color="primary">
            {field.label}
          </Typography.Text>

          <Select
            aria-label={field.label}
            value={data[field.key]}
            onValueChange={(value: string) => {
              update(field.key, value)
            }}
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
            withClearButton={false}
          />
        </div>
      ))}

      {status === "error" && (
        <p role="alert" className="text-max-text-negative">
          Не удалось сохранить анамнез. Проверьте, разрешено ли сохранение
          данных в браузере, и попробуйте ещё раз.
        </p>
      )}
      {status === "saved" && (
        <p role="status" className="text-max-text-themed">
          Изменения сохранены.
        </p>
      )}

      {onContinue ? (
        <div className="grid grid-cols-2 gap-3 pt-2">
          {onBack && (
            <Button
              type="button"
              variant="secondary"
              onClick={onBack}
              iconBefore={<ArrowLeft className="size-4" />}
            >
              Назад
            </Button>
          )}
          <Button type="submit" iconAfter={<ArrowRight className="size-4"/>}>
            Далее
          </Button>
        </div>
      ) : (
        <ProfileActions />
      )}
    </form>
  )
}

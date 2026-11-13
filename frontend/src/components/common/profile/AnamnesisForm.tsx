import { useState } from "react"
import { ArrowLeft, ArrowRight } from "lucide-react"
import { MultiSelectField } from "./MultiSelectField"
import { ProfileActions } from "./ProfileActions"
import { Button } from "@/components/ui/button"
import {
  readAnamnesis,
  saveAnamnesis,
  type AnamnesisData,
} from "@/lib/anamnesis"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { mockFields, mockSelects } from "@/data/anamnesis.mock"

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
        <Label htmlFor="surgeries">
          Операции и госпитализации за последний год
        </Label>
        <Textarea
          id="surgeries"
          placeholder="Если были, опишите..."
          value={data.surgeries}
          onChange={(e) => update("surgeries", e.target.value)}
          className="min-h-24 rounded-xl"
        />
      </div>

      {mockSelects.map((field) => (
        <div key={field.key} className="space-y-3">
          <Label id={`anamnesis-${field.key}-label`}>{field.label}</Label>
          <Select
            value={data[field.key]}
            onValueChange={(value) => {
              if (value !== null) {
                update(field.key, value)
              }
            }}
          >
            <SelectTrigger
              aria-labelledby={`anamnesis-${field.key}-label`}
              className="h-12! w-full rounded-xl"
            >
              <SelectValue placeholder="Выберите вариант" />
            </SelectTrigger>
            <SelectContent>
              {field.options.map((option) => (
                <SelectItem key={option} value={option}>
                  {option}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      ))}

      {status === "error" && (
        <p role="alert" className="text-sm text-destructive">
          Не удалось сохранить анамнез. Проверьте, разрешено ли сохранение
          данных в браузере, и попробуйте ещё раз.
        </p>
      )}
      {status === "saved" && (
        <p role="status" className="text-sm text-primary">
          Изменения сохранены.
        </p>
      )}

      {onContinue ? (
        <div className="flex gap-3 pt-2">
          {onBack && (
            <Button
              type="button"
              variant="outline"
              onClick={onBack}
              className="h-14 px-5"
            >
              <ArrowLeft className="size-4" />
              Назад
            </Button>
          )}
          <Button type="submit" className="h-14 flex-1 justify-between px-6">
            Далее
            <ArrowRight className="size-5" />
          </Button>
        </div>
      ) : (
        <ProfileActions />
      )}
    </form>
  )
}

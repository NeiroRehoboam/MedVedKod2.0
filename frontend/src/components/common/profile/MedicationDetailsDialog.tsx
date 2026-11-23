
import { Button, Select } from "@maxhub/max-ui"

import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
} from "@/components/ui/alert-dialog"

import type { MedicationEntry } from "@/lib/anamnesis"
import { intakeModeOptions } from "@/data/anamnesis.options"
import { FormLabel } from "./FormLabel"

type Option = {
  label: string
  value: string
}

type Props = {
  open: boolean
  onOpenChange: (open: boolean) => void
  medications: MedicationEntry[]
  options: Option[]
  onChange: (value: MedicationEntry[]) => void
}

export function MedicationDetailsDialog({
  open,
  onOpenChange,
  medications,
  options,
  onChange,
}: Props) {
  const getMedicationName = (value: string) => {
    if (value.startsWith("custom:")) {
      return value.slice("custom:".length)
    }

    return options.find((option) => option.value === value)?.label ?? value
  }

  const updateMode = (
    value: string,
    intakeMode: MedicationEntry["intake_mode"]
  ) => {
    onChange(
      medications.map((item) =>
        item.value === value
          ? { ...item, intake_mode: intakeMode }
          : item
      )
    )
  }

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent className="flex max-h-[85dvh] flex-col gap-0 overflow-hidden rounded-3xl bg-max-surface p-0">
        <div className="shrink-0 px-6 pt-6 pb-5">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-xl font-semibold tracking-tight text-max-text-primary">
              Приём лекарств
            </AlertDialogTitle>

            <AlertDialogDescription className="text-max-text-secondary">
              Уточните, как часто вы принимаете каждый препарат
            </AlertDialogDescription>
          </AlertDialogHeader>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain px-6 py-2">
          <div className="space-y-5">
            {medications.map((item, index) => (
              <div
                key={item.value}
                className={
                  index > 0
                    ? "border-t border-max-tertiary pt-5"
                    : ""
                }
              >
                <div className="mb-2">
                  <FormLabel>
                    {getMedicationName(item.value)}
                  </FormLabel>
                </div>

                <Select
                  aria-label={`Режим приёма: ${getMedicationName(item.value)}`}
                  value={item.intake_mode}
                  onValueChange={(value: string) =>
                    updateMode(
                      item.value,
                      value as MedicationEntry["intake_mode"]
                    )
                  }
                  options={intakeModeOptions}
                  placeholder="Выберите режим"
                  size="large"
                  mode="default"
                  multiple={false}
                  searchable={false}
                  dropdownWidth="trigger"
                />
              </div>
            ))}
          </div>
        </div>

        <div className="shrink-0 px-6 pt-5 pb-6">
          <Button
            type="button"
            size="large"
            variant="primary"
            stretched
            onClick={() => onOpenChange(false)}
          >
            Готово
          </Button>
        </div>
      </AlertDialogContent>
    </AlertDialog>
  )
}

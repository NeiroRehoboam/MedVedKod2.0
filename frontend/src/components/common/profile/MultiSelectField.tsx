import { useMemo, useState } from "react"
import { Check, Plus, Search, X } from "lucide-react"
import { Button, Input, Select } from "@maxhub/max-ui"
import { FormLabel } from "./FormLabel"
import { PageDescription } from "../typography"

type Props = {
  label: string
  options: string[]
  value: string[]
  onChange: (value: string[]) => void
}

export function MultiSelectField({ label, options, value, onChange }: Props) {
  const [search, setSearch] = useState("")
  const [customOptions, setCustomOptions] = useState<string[]>([])

  const allOptions = useMemo(
    () => [...new Set([...options, ...customOptions, ...value])],
    [options, customOptions, value]
  )

  const filteredOptions = allOptions.filter((item) =>
    item.toLowerCase().includes(search.trim().toLowerCase())
  )

  const addCustom = () => {
    const text = search.trim()
    if (!text) return

    const existing = allOptions.find(
      (item) => item.toLowerCase() === text.toLowerCase()
    )

    if (existing) {
      if (!value.includes(existing)) {
        onChange([...value, existing])
      }
    } else {
      setCustomOptions((prev) => [...prev, text])
      onChange([...value, text])
    }

    setSearch("")
  }

  const toggle = (item: string) => {
    if (value.includes(item)) {
      onChange(value.filter((v) => v !== item))
    } else {
      onChange([...value, item])
    }
  }

  const selectOptions = allOptions.map((item) => ({
    label: item,
    value: item,
  }))

  const canAddCustom =
    search.trim().length > 0 &&
    !allOptions.some(
      (item) => item.toLowerCase() === search.trim().toLowerCase()
    )

  return (
    <div>
      <FormLabel htmlFor="multi-select">{label}</FormLabel>

      <Select
        aria-label={label}
        multiple
        size="large"
        placeholder="Выбрать или добавить"
        value={value}
        options={selectOptions}
        onValueChange={(next: string[]) => onChange(next)}
        dropdownWidth="trigger"
        withClearButton
        customDropdownMenu={
          <div className="custom-select-menu flex flex-col">
            <div className="pb-2">
              <Input
                size="medium"
                mode="default"
                placeholder="Поиск или свой вариант..."
                iconBefore={<Search size={20} />}
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && canAddCustom) {
                    event.preventDefault()
                    addCustom()
                  }
                }}
                withClearButton
              />
            </div>

            <div className="max-h-56 overflow-y-auto">
              {filteredOptions.map((item) => {
                const selected = value.includes(item)

                return (
                  <button
                    key={item}
                    type="button"
                    onClick={() => toggle(item)}
                    aria-pressed={selected}
                    className={`flex min-h-11 w-full items-center justify-between rounded-max-small px-3 text-left text-sm transition-colors ${
                      selected && "bg-max-tertiary"
                    }`}
                  >
                    {item}

                    {selected && (
                      <Check size={15} className="text-max-text-primary" />
                    )}
                  </button>
                )
              })}

              {filteredOptions.length === 0 && (
                <div className="py-3 text-center text-sm">
                  <PageDescription>Ничего не найдено</PageDescription>
                </div>
              )}
            </div>

            {canAddCustom && (
              <div className="border-t border-max-tertiary p-2">
                <Button
                  disabled={false}
                  iconAfter={false}
                  iconBefore={<Plus size={15} />}
                  loading={false}
                  size="xsmall"
                  stretched={false}
                  variant="ghost"
                  className="w-full"

                  onClick={addCustom}
                >
                  Добавить «{search.trim()}»
                </Button>
              </div>
            )}
          </div>
        }
      />

      {value.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-3">
          {value.map((item) => (
            <div
              key={item}
              className="inline-flex items-center gap-1 rounded-max-small bg-max-tertiary py-1 pr-1 pl-2"
            >
              <p>{item}</p>
              <button
                type="button"
                aria-label={`Удалить ${item}`}
                onClick={() => onChange(value.filter((v) => v !== item))}
                className="rounded-max-button-xsmall flex size-7 shrink-0 items-center justify-center text-max-text-secondary transition-colors hover:bg-max-secondary hover:text-max-text-primary"
              >
                <X size={15} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

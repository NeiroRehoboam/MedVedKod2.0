import { useMemo, useState } from "react"
import { Check, Plus, Search, X } from "lucide-react"
import { Button, Input, Select } from "@maxhub/max-ui"
import type { ReactNode } from "react"
import { FormLabel } from "./FormLabel"
import { PageDescription } from "../typography"

type Option = {
  label: string
  value: string
}

type Props = {
  label: string
  options: Option[]
  value: string[]
  onChange: (value: string[]) => void
  disabled?: boolean
  action?: ReactNode
}

const CUSTOM_PREFIX = "custom:"

export function MultiSelectField({
  label,
  options,
  value,
  onChange,
  disabled = false,
  action,
}: Props) {
  const [search, setSearch] = useState("")

  const allOptions = useMemo(() => {
    const available = new Map<string, Option>()

    for (const option of options) {
      available.set(option.value, option)
    }

    for (const selected of value) {
      if (available.has(selected)) continue

      if (selected.startsWith(CUSTOM_PREFIX)) {
        available.set(selected, {
          value: selected,
          label: selected.slice(CUSTOM_PREFIX.length),
        })
      }
    }

    return [...available.values()]
  }, [options, value])

  const filteredOptions = useMemo(
    () =>
      allOptions.filter((option) =>
        option.label.toLowerCase().includes(search.trim().toLowerCase())
      ),
    [allOptions, search]
  )

  const getLabel = (selectedValue: string) => {
    const option = allOptions.find((item) => item.value === selectedValue)

    return (
      option?.label ??
      (selectedValue.startsWith(CUSTOM_PREFIX)
        ? selectedValue.slice(CUSTOM_PREFIX.length)
        : selectedValue)
    )
  }

  const toggle = (selectedValue: string) => {
    if (value.includes(selectedValue)) {
      onChange(value.filter((item) => item !== selectedValue))
    } else {
      onChange([...value, selectedValue])
    }
  }

  const addCustom = () => {
    const text = search.trim()

    if (!text) return

    const existing = allOptions.find(
      (option) => option.label.toLowerCase() === text.toLowerCase()
    )

    if (existing) {
      if (!value.includes(existing.value)) {
        onChange([...value, existing.value])
      }
    } else {
      const customValue = `${CUSTOM_PREFIX}${text}`

      if (!value.includes(customValue)) {
        onChange([...value, customValue])
      }
    }

    setSearch("")
  }

  const canAddCustom =
    search.trim().length > 0 &&
    !allOptions.some(
      (option) => option.label.toLowerCase() === search.trim().toLowerCase()
    )

  return (
    <div>
      <div className="mb-2 flex items-center justify-between gap-3">
        <FormLabel>{label}</FormLabel>
        {action}
      </div>

      <Select
        aria-label={label}
        multiple
        size="large"
        placeholder="Выбрать или добавить"
        value={value}
        options={allOptions}
        onValueChange={(next: string[]) => onChange(next)}
        dropdownWidth="trigger"
        withClearButton
        disabled={disabled}
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
              {filteredOptions.map((option) => {
                const selected = value.includes(option.value)

                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => toggle(option.value)}
                    aria-pressed={selected}
                    className={`flex min-h-11 w-full items-center justify-between rounded-max-small px-3 text-left text-sm transition-colors ${
                      selected ? "bg-max-tertiary" : ""
                    }`}
                  >
                    <span>{option.label}</span>

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
                  type="button"
                  iconBefore={<Plus size={15} />}
                  size="xsmall"
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
        <div className="mt-3 flex flex-wrap gap-2">
          {value.map((selectedValue) => {
            const label = getLabel(selectedValue)

            return (
              <div
                key={selectedValue}
                className="inline-flex items-center gap-1 rounded-max-small bg-max-tertiary py-1 pr-1 pl-2"
              >
                <p>{label}</p>

                <button
                  type="button"
                  aria-label={`Удалить ${label}`}
                  onClick={() =>
                    onChange(value.filter((item) => item !== selectedValue))
                  }
                  className="rounded-max-button-xsmall flex size-7 shrink-0 items-center justify-center text-max-text-secondary transition-colors hover:bg-max-secondary hover:text-max-text-primary"
                >
                  <X size={15} />
                </button>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

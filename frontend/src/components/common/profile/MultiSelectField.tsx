import { useState } from "react"
import { Check, Plus, X } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import {
  Command,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandEmpty,
} from "@/components/ui/command"

type Props = {
  label: string
  options: string[]
  value: string[]
  onChange: (value: string[]) => void
}

export function MultiSelectField({ label, options, value, onChange }: Props) {
  const [search, setSearch] = useState("")
  const [open, setOpen] = useState(false)

  const add = (item: string) => {
    const text = item.trim()
    if (!text) return

    const exists = value.some((v) => v.toLowerCase() === text.toLowerCase())

    if (!exists) {
      onChange([...value, text])
    }

    setSearch("")
  }

  const toggle = (item: string) => {
    if (value.includes(item)) {
      onChange(value.filter((v) => v !== item))
    } else {
      add(item)
    }
  }

  const filteredOptions = options.filter((item) =>
    item.toLowerCase().includes(search.toLowerCase())
  )

  const canAddCustom =
    search.trim().length > 0 &&
    !options.some(
      (item) => item.toLowerCase() === search.trim().toLowerCase()
    ) &&
    !value.some((item) => item.toLowerCase() === search.trim().toLowerCase())

  return (
    <div className="space-y-3">
      <Label>{label}</Label>

      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger
          render={<Button type="button" variant="default" className="h-11" />}
        >
          <Plus className="size-4" />
          Выбрать или добавить
        </PopoverTrigger>

        <PopoverContent
          align="start"
          className="w-[min(320px,calc(100vw-32px))] p-0"
        >
          <Command shouldFilter={false}>
            <CommandInput
              placeholder="Поиск или свой вариант..."
              value={search}
              onValueChange={setSearch}
            />

            <CommandList>
              {filteredOptions.length === 0 && !canAddCustom && (
                <CommandEmpty>Ничего не найдено</CommandEmpty>
              )}

              <CommandGroup>
                {filteredOptions.map((item) => {
                  const selected = value.includes(item)

                  return (
                    <CommandItem key={item} onSelect={() => toggle(item)}>
                      <Check
                        className={`mr-2 size-4 ${
                          selected ? "text-primary" : "opacity-0"
                        }`}
                      />
                      {item}
                    </CommandItem>
                  )
                })}

                {canAddCustom && (
                  <CommandItem onSelect={() => add(search)}>
                    <Plus className="mr-2 size-4" />
                    Добавить «{search.trim()}»
                  </CommandItem>
                )}
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>

      {value.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {value.map((item) => (
            <Badge
              key={item}
              variant="outline"
              className="h-9 gap-2 px-3 text-sm"
            >
              {item}

              <button
                type="button"
                aria-label={`Убрать ${item}`}
                onClick={() => onChange(value.filter((v) => v !== item))}
              >
                <X className="size-3.5" />
              </button>
            </Badge>
          ))}
        </div>
      )}
    </div>
  )
}

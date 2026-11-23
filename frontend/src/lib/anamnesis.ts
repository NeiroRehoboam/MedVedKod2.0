
export type MedicationEntry = {
  value: string
  intake_mode: "CONSTANT" | "AS_NEEDED"
}

export type StatusResponse = "YES" | "NO" | "UNKNOWN" | "NA"
export type SmokingStatus = "never" | "former" | "current"
export type AlcoholStatus = "never" | "sometimes" | "regularly"

export type AnamnesisData = {
  diseases: string[]
  allergies: string[]
  heredity: string[]
  medications: MedicationEntry[]

  recent_events_notes: string

  pregnancy: StatusResponse
  lactation: StatusResponse

  smoking_status: SmokingStatus | null
  alcohol_status: AlcoholStatus | null
}

const STORAGE_KEY = "medved.anamnesis"

export function emptyAnamnesis(): AnamnesisData {
  return {
    diseases: [],
    allergies: [],
    heredity: [],
    medications: [],

    recent_events_notes: "",

    pregnancy: "UNKNOWN",
    lactation: "UNKNOWN",

    smoking_status: null,
    alcohol_status: null,
  }
}

export function readAnamnesis(): AnamnesisData {
  const data = emptyAnamnesis()

  try {
    const saved: unknown = JSON.parse(
      localStorage.getItem(STORAGE_KEY) ?? "null"
    )

    if (!saved || typeof saved !== "object" || Array.isArray(saved)) {
      return data
    }

    const record = saved as Record<string, unknown>

    // Хронические заболевания, аллергии, наследственность
    for (const key of ["diseases", "allergies", "heredity"] as const) {
      const value = record[key]

      if (Array.isArray(value)) {
        data[key] = value.filter(
          (item): item is string => typeof item === "string"
        )
      }
    }

    // Лекарства с индивидуальным режимом приёма
    if (Array.isArray(record.medications)) {
      data.medications = record.medications.flatMap(
        (item): MedicationEntry[] => {
          if (typeof item === "string") {
            return [
              { value: item, intake_mode: "AS_NEEDED" },
            ]
          }

          if (
            !item ||
            typeof item !== "object" ||
            Array.isArray(item)
          ) {
            return []
          }

          const medication = item as Record<string, unknown>

          if (typeof medication.value !== "string") {
            return []
          }

          return [
            {
              value: medication.value,
              intake_mode:
                medication.intake_mode === "CONSTANT"
                  ? "CONSTANT"
                  : "AS_NEEDED",
            },
          ]
        }
      )
    }

    // Операции и госпитализации
    if (typeof record.recent_events_notes === "string") {
      data.recent_events_notes = record.recent_events_notes
    }

    // Беременность и лактация
    for (const key of ["pregnancy", "lactation"] as const) {
      const value = record[key]

      if (
        value === "YES" ||
        value === "NO" ||
        value === "UNKNOWN" ||
        value === "NA"
      ) {
        data[key] = value
      }
    }

    // Курение
    const smoking = record.smoking_status

    if (
      smoking === "never" ||
      smoking === "former" ||
      smoking === "current"
    ) {
      data.smoking_status = smoking
    } else if (smoking === null) {
      data.smoking_status = null
    }

    // Алкоголь
    const alcohol = record.alcohol_status

    if (
      alcohol === "never" ||
      alcohol === "sometimes" ||
      alcohol === "regularly"
    ) {
      data.alcohol_status = alcohol
    } else if (alcohol === null) {
      data.alcohol_status = null
    }
  } catch {
    return data
  }

  return data
}

export function saveAnamnesis(data: AnamnesisData): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
}

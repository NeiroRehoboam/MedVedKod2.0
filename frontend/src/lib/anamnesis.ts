export type AnamnesisData = {
  diseases: string[]
  allergies: string[]
  heredity: string[]
  frequency: string
  surgeries: string
  pregnancy: string
  smoking: string
  alcohol: string
}

const STORAGE_KEY = "medved.anamnesis"

export function emptyAnamnesis(): AnamnesisData {
  return {
    diseases: [],
    allergies: [],
    heredity: [],
    frequency: "",
    surgeries: "",
    pregnancy: "",
    smoking: "",
    alcohol: "",
  }
}

export function readAnamnesis(): AnamnesisData {
  const data = emptyAnamnesis()

  try {
    const saved: unknown = JSON.parse(
      localStorage.getItem(STORAGE_KEY) ?? "null"
    )
    if (!saved || typeof saved !== "object") return data
    const record = saved as Record<string, unknown>

    for (const key of ["diseases", "allergies", "heredity"] as const) {
      if (key in record) {
        const value = record[key]
        if (Array.isArray(value)) {
          data[key] = value.filter(
            (item): item is string => typeof item === "string"
          )
        }
      }
    }

    for (const key of [
      "frequency",
      "surgeries",
      "pregnancy",
      "smoking",
      "alcohol",
    ] as const) {
      const value = record[key]
      if (typeof value === "string") data[key] = value
    }
  } catch {}

  return data
}

export function saveAnamnesis(data: AnamnesisData) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
}

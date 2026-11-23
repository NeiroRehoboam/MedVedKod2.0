import type {
  AlcoholStatusEnum,
  FullAnamnesis,
  FullAnamnesisRequest,
  IntakeModeEnum,
  PregnancyEnum,
  SmokingStatusEnum,
} from "@/api/generated/models"

export type MedicationEntry = {
  value: string
  intake_mode: IntakeModeEnum
}

export type StatusResponse = PregnancyEnum
export type SmokingStatus = SmokingStatusEnum
export type AlcoholStatus = AlcoholStatusEnum

export type SelectFieldKey =
  "pregnancy" | "lactation" | "smoking_status" | "alcohol_status"

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

type Reference = {
  id?: number | null
  custom_name?: string | null
}

function toSelectedValue(reference: Reference): string | null {
  if (reference.id != null) {
    return String(reference.id)
  }

  if (reference.custom_name?.trim()) {
    return `custom:${reference.custom_name.trim()}`
  }

  return null
}

export function mapAnamnesisToForm(
  source: FullAnamnesis
): AnamnesisData {
  const data = emptyAnamnesis()

  data.diseases = (source.chronic_diseases ?? [])
    .map((item) =>
      toSelectedValue({
        id: item.disease,
        custom_name: item.custom_name,
      })
    )
    .filter((value): value is string => value !== null)

  data.heredity = (source.hereditary_diseases ?? [])
    .map((item) =>
      toSelectedValue({
        id: item.disease,
        custom_name: item.custom_name,
      })
    )
    .filter((value): value is string => value !== null)

  data.allergies = (source.allergies ?? [])
    .map((item) =>
      toSelectedValue({
        id: item.allergen,
        custom_name: item.custom_name,
      })
    )
    .filter((value): value is string => value !== null)

  data.medications = (source.medications ?? [])
    .flatMap((item) => {
      const value = toSelectedValue({
        id: item.medication,
        custom_name: item.custom_name,
      })

      if (!value) return []

      return [{
        value,
        intake_mode:
          item.intake_mode === "CONSTANT"
            ? "CONSTANT" as const
            : "AS_NEEDED" as const,
      }]
    })

  data.recent_events_notes = source.recent_events_notes ?? ""

  if (
    source.pregnancy === "YES" ||
    source.pregnancy === "NO" ||
    source.pregnancy === "UNKNOWN" ||
    source.pregnancy === "NA"
  ) {
    data.pregnancy = source.pregnancy
  }

  if (
    source.lactation === "YES" ||
    source.lactation === "NO" ||
    source.lactation === "UNKNOWN" ||
    source.lactation === "NA"
  ) {
    data.lactation = source.lactation
  }

  if (
    source.smoking_status === "never" ||
    source.smoking_status === "former" ||
    source.smoking_status === "current"
  ) {
    data.smoking_status = source.smoking_status
  }

  if (
    source.alcohol_status === "never" ||
    source.alcohol_status === "sometimes" ||
    source.alcohol_status === "regularly"
  ) {
    data.alcohol_status = source.alcohol_status
  }

  return data
}

const CUSTOM_PREFIX = "custom:"

function parseReference(value: string) {
  if (value.startsWith(CUSTOM_PREFIX)) {
    return {
      id: null,
      custom_name: value.slice(CUSTOM_PREFIX.length),
    }
  }

  return {
    id: Number(value),
    custom_name: "",
  }
}

export function createAnamnesisPayload(data: AnamnesisData): FullAnamnesisRequest {
  return {
    smoking_status: data.smoking_status || null,
    alcohol_status: data.alcohol_status || null,

    pregnancy: data.pregnancy,
    lactation: data.lactation,

    recent_events_notes: data.recent_events_notes,

    chronic_diseases: data.diseases.map((value) => {
      const reference = parseReference(value)

      return {
        disease: reference.id,
        custom_name: reference.custom_name,
      }
    }),

    hereditary_diseases: data.heredity.map((value) => {
      const reference = parseReference(value)

      return {
        disease: reference.id,
        custom_name: reference.custom_name,
      }
    }),

    allergies: data.allergies.map((value) => {
      const reference = parseReference(value)

      return {
        allergen: reference.id,
        custom_name: reference.custom_name,
      }
    }),

    medications: data.medications.map((item) => {
      const reference = parseReference(item.value)

      return {
        medication: reference.id,
        custom_name: reference.custom_name,
        intake_mode: item.intake_mode,
      }
    }),
  }
}

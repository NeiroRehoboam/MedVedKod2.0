export type Appeal = {
  id: string
  title: string
  summary?: string
  date: string
  status: "completed" | "in_progress"
}
